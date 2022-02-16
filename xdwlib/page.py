#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix expandtab :

"""page.py -- Page and PageCollection

Copyright (C) 2010 HAYASHI Hideki <hideki@hayasix.com>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import os
import re
import subprocess
import itertools
from functools import cmp_to_key
from os.path import abspath, split as splitpath, join as joinpath
import codecs
from urllib.request import Request, urlopen
from urllib.parse import urlencode, urlparse, urlunparse
import time
import json

from .xdwapi import *
from .common import *
from .xdwtemp import XDWTemp
from .observer import *
from .struct import Point, Rect
from .annotatable import Annotatable


__all__ = ("Page", "PageCollection")

U0000 = chr(0)
XDWRES = 100.0  # XDWAPI resolution is 1/100 mm.
CHARSET2ENC = {
        ANSI_CHARSET: "ascii",
        DEFAULT_CHARSET: CODEPAGE,
        SHIFTJIS_CHARSET: "cp932",
        HANGEUL_CHARSET: "cp949",
        CHINESEBIG5_CHARSET: "big5",
        GREEK_CHARSET: "cp869",
        TURKISH_CHARSET: "cp1026",
        BALTIC_CHARSET: "cp775",
        RUSSIAN_CHARSET: "cp855",
        EASTEUROPE_CHARSET: "cp852",
        OEM_CHARSET: "utf-8",  # unknown
        }
OCR_LANGUAGES = {
        437: "ENGLISH",
        863: "FRENCH",
        936: "SIMPLIFIED_CHINESE",
        950: "TRADITIONAL_CHINESE",
        874: "THAI",
        932: "JAPANENSE",
        949: "KOREAN",
        1258: "VIETNAMESE",
        }
ENV_AZURE_URL = "XDWLIB_OCR_AZURE_ENDPOINT"
ENV_AZURE_KEY = "XDWLIB_OCR_AZURE_SUBSCRIPTION_KEY"


class PageCollection(list):

    """Page collection i.e. container for pages."""

    def __repr__(self):
        return "{cls}({seq})".format(
                cls=self.__class__.__name__,
                seq=", ".join(repr(pg) for pg in self))

    def __getitem__(self, pos):
        if isinstance(pos, slice):
            return PageCollection(list.__getitem__(self, pos))
        return list.__getitem__(self, pos)

    def __add__(self, y):
        if isinstance(y, Page):
            return PageCollection(list.__add__(self, [y]))
        elif isinstance(y, PageCollection):
            return PageCollection(list.__add__(self, y))
        raise TypeError("only Page or PageCollection can be added")

    def __radd__(self, y):
        if isinstance(y, Page):
            return PageCollection(list.__add__([y], self))
        elif isinstance(y, PageCollection):
            return PageCollection(list.__add__(y, self))
        raise TypeError("only Page or PageCollection can be added")

    def __iadd__(self, y):
        if isinstance(y, Page):
            self.append(y)
        elif isinstance(y, PageCollection):
            self.extend(y)
        else:
            raise TypeError("only Page or PageCollection can be added")
        return self

    def __mul__(self, n):
        return PageCollection(list.__mul__(self, n))

    __rmul__ = __mul__

    def __imul__(self, n):
        if n < 1:
            return PageCollection()
        self.extend(self * (n - 1))
        return self

    def view(self, light=False, wait=True, flat=False, group=True,
             page=0, fullscreen=False, zoom=0):
        """View pages with DocuWorks Viewer (Light).

        light       (bool) force to use DocuWorks Viewer Light.
                    Note that DocuWorks Viewer is used if Light version is
                    not avaiable.
        wait        (bool) wait until viewer stops and get annotation info
        flat        (bool) combine pages into a single document.
        group       (bool) group continuous pages by original document,
                    i.e. create document-in-binder.
        page        (int) page number to view
        fullscreen  (bool) view in full screen (presentation mode)
        zoom        (int) in 10-1600 percent; 0 means 100%
                    (str) 'WIDTH' | 'HEIGHT' | 'PAGE'

        If wait is True, returns a dict, each key of which is the page pos
        and the value is a list of AnnotationCache objects i.e.:

            {0: [ann_cache, ann_cache, ...], 1: [...], ...}

        Note that pages without annotations are ignored.

        If wait is False, returns (proc, path) where:

                proc    subprocess.Popen object
                path    pathname of temporary file being viewed

        In this case, you should remove temp and its parent dir after use.

        NB. Attachments are not shown.
        NB. Viewing signed pages will raise AccessDeniedError.
        """
        temp = XDWTemp(autoclose=wait)
        temp.path = self.export(
                joinpath(temp.dir, "{0}_P{1}.{2}".format(
                        self[0].doc.name,
                        self[0].pos + 1,
                        "xdw" if flat else "xbd")),
                flat=flat, group=group)
        args = [get_viewer(light=light), temp.path]
        if page:
            args.append(f"/n{page + 1}")
        if fullscreen:
            args.append("/f")
        if isinstance(zoom, (int, float)) and zoom:
            if zoom and not (10 <= zoom <= 1600):
                raise ValueError(f"10..1600(%) is valid, {zoom} given")
            args.append(f"/m{int(zoom)}")
        elif isinstance(zoom, str):
            if zoom.upper() not in ("WIDTH", "HEIGHT", "PAGE"):
                raise ValueError((
                        f"int, 'WIDTH', 'HEIGHT' or 'PAGE' is valid"
                        f"for window size, {repr(zoom)} given"))
            args.append(f"/m{zoom[0].lower()}")
        elif zoom:
            raise ValueError(f"10..1600(%) or W/H/P is valid for zoom, "
                             f"{zoom} given")
        proc = subprocess.Popen(args)
        if not wait:
            return (proc, temp.path)
        from .xdwfile import xdwopen
        from .annotation import AnnotationCache
        proc.wait()
        doc = xdwopen(temp.path)
        r = [(p, [AnnotationCache(ann) for ann in doc.page(p)])
                for p in range(doc.pages) if doc.page(p).annotations]
        doc.close()
        temp.close()
        return dict(r)

    def group(self):
        """Make an iterator that returns consecutive page-groups.

        Pages are grouped by belonging BaseDocument object.

        Example:
            >>> pc = PageCollection([doc1[0], doc1[2]])
            >>> pc.extend(doc2[1:4])
            >>> pc
            PageCollection([doc1[0], doc1[2], doc2[1], doc2[2], doc2[3]])
            >>> pc.group()
            [PageCollection(Page(doc1[0]), Page(doc1[2]), PageCollection(Page(
            doc2[1]), Page(doc2[2]), Page(doc2[3]))]
        """
        for g in itertools.groupby(self, lambda pg: pg.doc):
            yield PageCollection(g[1])

    def export(self, path=None, flat=False, group=True):
        """Create a binder or document as a container for page collection.

        path    (str) export to {path};
                      with no dir, export to {document/binder dir}/{path}
                (None) save to {document/binder dir}/{.xdw or .xbd}
        flat    (bool) create document instead of binder
        group   (bool) group continuous pages by original document,
                i.e. create document-in-binder.

        Returns the exported pathname which may differ from path.
        """
        from .document import create as create_document
        from .binder import create_binder
        from .xdwfile import xdwopen
        path = newpath(path or self[0].doc.name + (".xdw" if flat else ".xbd"),
                       dir=self[0].doc.dirname())
        if flat:
            path = create_document(output_path=path)
        else:
            path = create_binder(path)
        with xdwopen(path) as doc:
            with XDWTemp() as temp:
                if flat:
                    for pg in self:
                        tmp = joinpath(temp.dir, pg.doc.name + ".xdw")
                        tmp = pg.export(tmp)
                        doc.append(tmp)
                        os.remove(tmp)
                    del doc[0]  # Delete the initial blank page.
                elif group:
                    for pc in self.group():
                        tmp = joinpath(temp.dir, pc[0].doc.name + ".xdw")
                        tmp = pc.export(tmp, flat=True)
                        doc.append(tmp)
                        os.remove(tmp)
                else:
                    for pos, pg in enumerate(self):
                        tmp = joinpath(temp.dir,
                                f"{pg.doc.name}_P{pg.pos + 1}.xdw")
                        tmp = pg.export(tmp)
                        doc.append(tmp)
                        os.remove(tmp)
            doc.save()
        return path


class Page(Annotatable, Observer):

    """Page of DocuWorks document."""

    @staticmethod
    def norm_res(n):
        if n <= 6:
            return (100, 200, 400, 200, 300, 400, 200)[n]
        return n

    def reset_attr(self):
        abspos = self.doc.absolute_page(self.pos)
        pginfo = XDW_GetPageInformation(
                self.doc.handle, abspos + 1, extend=True)
        self.size = Point(
                pginfo.nWidth / XDWRES,
                pginfo.nHeight / XDWRES)  # float, in mm
        # XDW_PGT_FROMIMAGE/FROMAPPL/NULL
        self.type = XDW_PAGE_TYPE[pginfo.nPageType]
        self.resolution = Point(
                Page.norm_res(pginfo.nHorRes),
                Page.norm_res(pginfo.nVerRes))  # dpi
        self.compress_type = XDW_COMPRESS[pginfo.nCompressType]
        self.annotations = pginfo.nAnnotations
        self.degree = pginfo.nDegree
        self.original_size = Point(
                pginfo.nOrgWidth / XDWRES,
                pginfo.nOrgHeight / XDWRES)  # mm
        self.original_resolution = Point(
                Page.norm_res(pginfo.nOrgHorRes),
                Page.norm_res(pginfo.nOrgVerRes))  # dpi
        self.image_size = Point(
                pginfo.nImageWidth,
                pginfo.nImageHeight)  # px
        # Page color info.
        pci = XDW_GetPageColorInformation(self.doc.handle, abspos + 1)
        self.is_color = bool(pci.nColor)
        self.bpp = pci.nImageDepth

    def __init__(self, doc, pos):
        self.pos = pos
        Annotatable.__init__(self)
        Observer.__init__(self, doc, EV_PAGE_INSERTED)
        self.doc = doc
        self.reset_attr()

    def absolute_page(self, append=False):
        return self.doc.absolute_page(self.pos, append=append)

    def color_scheme(self):
        if self.is_color:
            return "COLOR"
        elif 1 < self.bpp:
            return "MONO_HIGHQUALITY"
        else:
            return "MONO"

    def __repr__(self):
        return "{cls}({doc}[{pos}])".format(
                cls=self.__class__.__name__,
                doc=self.doc.name,
                pos=self.pos)

    def __str__(self):
        return ("Page({doc}[{pos}]; "
                "{width:.2f}*{height:.2f}mm, "
                "{type}, {anns} annotations)").format(
                doc=self.doc.name,
                pos=self.pos,
                width=self.size.x,
                height=self.size.y,
                type=self.type,
                anns=self.annotations)

    def __eq__(self, other): return self._cmp(other) == 0
    def __ne__(self, other): return self._cmp(other) != 0
    def __lt__(self, other): return self._cmp(other) < 0
    def __gt__(self, other): return self._cmp(other) > 0
    def __le__(self, other): return self._cmp(other) <= 0
    def __ge__(self, other): return self._cmp(other) >= 0

    @staticmethod
    def _cmpvalue(a, b):
        return 0 if a == b else (-1 if a < b else 1)

    @staticmethod
    def _cmppath(*docs):  # for narrow Python build
        return _cmpvalue(*[
                abspath(joinpath(doc.dir, doc.name)).replace(os.sep, U0000)
                for doc in docs])

    def _cmp(self, other):
        """Substitute for __cmp__(), which is no longer supported.

        Rules to determine page order are:
            1.  For pages in the same BaseDocument, follow their page numbers.
            2.  Page in Document is less than Page in DocumentInBinder.
            3.  For DocumentInBinder's in the same Binder,
                follow their document positions in the Binder.
            4.  Documents or Binders are compared for their pathnames.
        """
        if not isinstance(other, Page):
            raise TypeError("can only compare to a page")
        if self.doc is other.doc:
            return self._cmpvalue(self.pos, other.pos)
        in_dib = hasattr(self.doc, "binder")  # DocumentInBinder
        if self.doc.__class__ is not other.doc.__class__:
            return +1 if in_dib else -1
        if in_dib:
            if self.doc.binder is other.doc.binder:
                return self._cmpvalue(self.doc.pos, other.doc.pos)
            return self._cmppath(self.doc.binder, other.doc.binder)
        return self._cmppath(self.doc, other.doc)

    @staticmethod
    def _split_attrname(name, store=False):
        if "_" not in name:
            return (None, name)
        forms = {
                "header": XDW_PAGEFORM_HEADER,
                "footer": XDW_PAGEFORM_FOOTER,
                "pagenumber": XDW_PAGEFORM_PAGENUMBER,
                }
        if store:
            forms["topimage"] = XDW_PAGEFORM_TOPIMAGE
            forms["bottomimage"] = XDW_PAGEFORM_BOTTOMIMAGE
        form = forms.get(name.split("_")[0], None)
        if form is not None:
            name = name[name.index("_") + 1:]
        return (form, name)

    def __getattribute__(self, name):
        if "_" in name:
            spl = Annotatable.__getattribute__(self, "_split_attrname")
            form, name = spl(name)
            if form is not None:
                name = inner_attribute_name(name)
                doc = Annotatable.__getattribute__(self, "doc")
                return XDW_GetPageFormAttribute(doc.handle, form, cp(name))
        return Annotatable.__getattribute__(self, name)

    def __setattr__(self, name, value):
        Annotatable.__setattr__(self, name, value)

    def get_userattr(self, name, default=None):
        """Get pagewise user defined attribute.

        name        (str or bytes) attribute name
        default     value to return if no attribute named name exist

        Returns a bytes value.
        """
        try:
            return XDW_GetPageUserAttribute(
                    self.doc.handle, self.absolute_page() + 1, cp(name))
        except InvalidArgError:
            return default

    def set_userattr(self, name, value):
        """Set pagewise user defined attribute.

        name        (str or bytes) attribute name
        value       (bytes) value to set
        """
        XDW_SetPageUserAttribute(
                self.doc.handle, self.absolute_page() + 1, cp(name), value)

    def update(self, event):
        if not isinstance(event, Notification):
            raise TypeError("not an instance of Notification class")
        if event.type == EV_PAGE_REMOVED:
            if event.para[0] < self.pos:
                self.pos -= 1
        elif event.type == EV_PAGE_INSERTED:
            if event.para[0] < self.pos:
                self.pos += 1
        else:
            raise ValueError(f"illegal event type: {event.type}")

    def _add(self, ann_type, position, init_dat):
        """Concrete method over _add() for add()."""
        ann_type = XDW_ANNOTATION_TYPE.normalize(ann_type)
        return XDW_AddAnnotation(self.doc.handle,
                ann_type, self.absolute_page() + 1,
                int(position.x * 100), int(position.y * 100),
                init_dat)

    def _delete(self, ann):
        """Concrete method over _delete() for delete()."""
        XDW_RemoveAnnotation(self.doc.handle, ann.handle)

    def content_text(self, type=None):
        """Returns content text of page.

        type    None | "IMAGE" | "APPLICATION"
                None means both.
        """
        if type and type.upper() != self.type:
            return None
        return XDW_GetPageTextToMemoryW(
                self.doc.handle, self.absolute_page() + 1)

    def bitmap(self):
        """Returns page image with annotations as a Bitmap object."""
        opt = XDW_IMAGE_OPTION()
        opt.nDpi = int(max(10, min(600, max(self.resolution))))
        opt.nColor = XDW_IMAGE_COLORSCHEME.normalize(self.color_scheme())
        return XDW_ConvertPageToImageHandle(self.doc.handle, self.pos + 1, opt)

    def rasterize(self, direct=False):
        """Rasterize; convert an application page into DocuWorks image page.

        Resolution of converted page is <= 600 dpi even for more precise page.

        CAUTION: Page will be replaced with just an image.  Visible annotations
        are drawn as parts of image and cannot be handled as effective
        annotations any more.  Application/OCR text will be lost.
        """
        if self.type == "APPLICATION":
            doc, pos = self.doc, self.pos
            doc.rasterize(pos, direct=direct)
            self = doc.page(pos)  # reset

    def rotate(self, degree=0, auto=False, direct=False):
        """Rotate page around the center.

        degree  (int) rotation angle in clockwise degree
        auto    (bool) automatic rotation for OCR

        Resolution of converted page is <= 600 dpi even for more precise page,
        as far as degree is neither 0, 90, 180 or 270.

        CAUTION: If degree is not 0, 90, 180 or 270, Page will be replaced with
        just an image.  Visible Annotations are drawn as parts of image and
        cannot be handled as effective annotations any more.  Application/OCR
        text will be lost.
        """
        doc, pos = self.doc, self.pos
        doc.rotate(pos, degree=degree, auto=auto, direct=direct)
        self.reset_attr()

    def reduce_noise(self, level="NORMAL"):
        """Process page with internal noise reduction engine.

        level   'NORMAL' | 'WEAK' | 'STRONG'
        """
        if self.type != "IMAGE" or self.color_scheme() != "MONO":
            raise TypeError("noise reduction is for monochrome image pages")
        level = XDW_OCR_NOISEREDUCTION.normalize(level)
        XDW_ReducePageNoise(self.doc.handle, self.absolute_page() + 1, level)

    def ocr(self,
            engine="DEFAULT",
            strategy="SPEED",
            preprocessing="SPEED",
            noise_reduction="NONE",
            deskew=True,
            form="AUTO",
            column="AUTO",
            rects=None,
            language="AUTO",
            main_language="BALANCED",
            use_ascii=True,
            insert_space=False,
            verbose=False,
            failover=True,
            ):
        """Process page with OCR engine.

        engine          'DEFAULT' | 'WINREADER PRO'  -- DW9.1+
                        'DEFAULT' | 'WINREADER PRO' | 'MULTI'  -- DW<=9.0
        strategy        'STANDARD' | 'SPEED' | 'ACCURACY'
        preprocessing   'SPEED' | 'ACCURACY'  -- DW<9
                        'MONO_SPEED' | 'MONO_ACCURACY' | 'COLOR'  -- DW9+
        noise_reduction 'NONE' | 'NORMAL' | 'WEAK' | 'STRONG'
        deskew          (bool)
        form            'AUTO' | 'TABLE' | 'WRITING'
        column          'AUTO' | 'HORIZONTAL_SINGLE' | 'HORIZONTAL_MULTI'
                               | 'VERTICAL_SINGLE'   | 'VERTICAL_MULTI'
        rects           (list of Rect) Rects to OCR
        language        'AUTO' | 'JAPANESE' | 'ENGLISH'  -- DW<9
                        (str) comma-separated list of followings:  -- DW9+
                              'AUTO' | 'JAPANESE' | 'ENGLISH'
                                     | 'SIMPLIFIED_CHINESE'
                                     | 'TRADITIONAL_CHINESE'
                                     | 'THAI' | 'KOREAN' | 'VIETNAMESE'
                                     | 'INDONESIAN' | 'MALAY' | 'TAGALOG'
        main_language   'BALANCED' | 'JAPANESE' | 'ENGLISH'
        use_ascii       (bool) use ASCII chars
        insert_space    (bool) insert spaces for blanks
        verbose         (bool) show progress banner
        failover        (bool) do ocr_azure() if ocr() failed

        CAUTION: To do ocr_azure(), enable internet connection and set
        environment variables XDWLIB_OCR_AZURE_ENDPOINT and
        XDWLIB_OCR_AZURE_SUBSCRIPTION_KEY.
        """
        if self.type != "IMAGE":
            raise TypeError("OCR is available for image pages")
        if not OCRENABLED:
            if all(self.azure_env()):
                return self.ocr_azure()
            raise AccessDeniedError("OCR is out of service")
        en = XDW_OCR_ENGINE.normalize(engine)
        if en == XDW_OCR_ENGINE_WRP:
                opt = XDW_OCR_OPTION_WRP()
                opt.nLanguage = XDW_OCR_LANGUAGE.normalize(language)
                opt.nPriority = XDW_OCR_PREPROCESSING.normalize(preprocessing)
        else:
            if XDWVER < 9:
                opt = XDW_OCR_OPTION_V7()
                opt.nLanguage = XDW_OCR_LANGUAGE.normalize(language)
                opt.nPriority = XDW_OCR_PREPROCESSING.normalize(preprocessing)
                opt.nLanguageMixedRate = XDW_OCR_MAIN_LANGUAGE.normalize(
                                main_language)
            else:
                if en != XDW_OCR_ENGINE_DEFAULT:  # FRE or FRE_MULTI
                    raise ValueError(f"illegal OCR engine '{engine}'")
                opt = XDW_OCR_OPTION_V9()
                if language.upper() == "AUTO":
                    language = ",".join([OCR_LANGUAGES.get(CP, ""), "ENGLISH"])
                opt.nLanguage = flagvalue(XDW_OCR_MULTIPLELANGUAGES, language)
                opt.nPriority = XDW_OCR_PREPROCESS_PRIORITY.normalize(
                                preprocessing)
            opt.nEngineLevel = XDW_OCR_STRATEGY.normalize(strategy)
            opt.nHalfSizeChar = bool(use_ascii)
            opt.nDisplayProcess = bool(verbose)
            if rects:
                opt.nAreaNum = len(rects)
                rs = (XDW_RECT * len(rects))()
                ps = (POINTER(XDW_RECT) * len(rects))()
                for i, rect in enumerate(rects):
                    rs[i].left, rs[i].top, rs[i].right, rs[i].bottom = \
                            [int(x * 100) for x in rect]
                    ps[i] = pointer(rs[i])
                opt.pAreaRects = ps
            else:
                opt.pAreaRects = NULL
        opt.nNoiseReduction = XDW_OCR_NOISEREDUCTION.normalize(noise_reduction)
        opt.nAutoDeskew = bool(deskew)
        opt.nForm = XDW_OCR_FORM.normalize(form)
        opt.nColumn = XDW_OCR_COLUMN.normalize(column)
        opt.nInsertSpaceCharacter = bool(insert_space)
        XDW_ApplyOcr(self.doc.handle, self.absolute_page() + 1, en, opt)

    @staticmethod
    def azure_env():
        return (os.environ.get(f"{ENV_AZURE_URL}"),
                os.environ.get(f"{ENV_AZURE_KEY}"))

    def ocr_azure(self,
            language=None, charset="DEFAULT", errors="replace", timeout=60,
            endpoint="", subscription_key="",
            version="3.2", model_version="latest",
            ):
        """Process page with Azure OCR.

        language        (None) expect no specific language
                        (str) 'ja', 'en', etc.
        charset         'DEFAULT' | 'ANSI' | 'SYMBOL' | 'MAC' | 'SHIFTJIS'
                                  | 'HANGEUL' | 'CHINESEBIG5' | 'GREEK'
                                  | 'TURKISH' | 'BALTIC' | 'RUSSIAN'
                                  | 'EASTEUROPE' | 'OEM'
        errors          'replace' | strict' | 'ignore' | 'xmlcharrefreplace'
                                  | 'backslashreplace' | 'namereplace'
                                  | 'surrogateescape'
                                  | 'surrogatepass' (valid only for utf-8)
        timeout         (int) seconds to wait for OCR result
        endpoint        (str) Azure OCR endpoint e.g.:
                              'https://yourproject.cognitiveservices.azure.com/'
        subscription_key  (str) Azure OCR subscription key
        version         (str) OCR engine version e.g. '3.2'
        model_version   (str) see Azure Read API document e.g.:
                              'latest', '2021-09-30-preview', or '2021-04-12'

        Notes: Default endpoint and subscription_key can be set in environment
        variables XDWLIB_OCR_AZURE_ENDPOINT and
        XDWLIB_OCR_AZURE_SUBSCRIPTION_KEY.
        """
        url, key = self.azure_env()
        url = endpoint or url
        key = subscription_key or key
        if not (url and key):
            raise ValueError(f"{ENV_AZURE_URL} or {ENV_AZURE_KEY} is missing")
        with XDWTemp(suffix=".jpg") as temp:
            self.export_image(path=temp.path, format="JPEG",
                              dpi=self.resolution.x)
            with open(temp.path, "rb") as in_:
                data = in_.read()
        assert str(version) == "3.2"
        url = url.rstrip("/") + f"/vision/v{version}/read/analyze"
        headers = {"Ocp-Apim-Subscription-Key": key,
                   "Content-Type": "application/octet-stream"}
        params = {"language": language or "",
                  "model-version": model_version,
                  "readingOrder": "natural"}
        def build_req(url, headers=None, params=None, method="GET"):
            url = list(urlparse(url))
            if params: url[4] = urlencode(params)
            return Request(urlunparse(url), headers=headers, method=method)
        req = build_req(url, headers=headers, params=params, method="POST")
        res = urlopen(req, data=data)
        if not str(res.status).startswith("2"):
            raise ApplicatonFailedError(
                    f"falure in Azure OCR, status={result.status}")
        req = build_req(res.headers["Operation-Location"], headers=headers)
        tick = 3
        for elapsed in range(0, timeout, tick):
            res = urlopen(req)
            result = json.loads(res.read().decode("utf-8"))
            if result.get("status") == "failed":
                raise ApplicatonFailedError("failure in Azure OCR")
            if "analyzeResult" in result:
                break
            time.sleep(tick)
        else:
            raise ApplicatonFailedError("time out in Azure OCR")
        lines = result["analyzeResult"]["readResults"][0]["lines"]
        rtlist = [(Rect(*[line["boundingBox"][i] for i in (0, 1, 4, 5)]),
                   line["text"]) for line in lines]
        # Text segments in vertically written documents should be reordered.
        if sum(-1 if r.size().x < r.size().y else 1 for r, t in rtlist) < 0:
            def cmp(rt0, rt1):
                lt0, lt1 = rt0[0].position(), rt1[0].position()
                rb0, rb1 = lt0 + rt0[0].size(), lt1 + rt1[0].size()
                if rb0.y < lt1.y: result = -1
                elif rb1.y < lt0.y: result = 1
                elif lt0.x < lt1.x: result = 1
                else: result = -1
                return result
            rtlist.sort(key=cmp_to_key(cmp))
        self.set_ocr_text(rtlist, charset=charset, errors=errors, unit="px")

    def clear_ocr_text(self):
        """Clear OCR text."""
        if self.type != "IMAGE":
            raise TypeError("OCR text is available for image pages")
        XDW_SetOcrData(self.doc.handle, self.absolute_page() + 1, NULL)

    def set_ocr_text(self, rtlist, charset="DEFAULT", half_open=True,
                           errors="strict", unit="mm"):
        """Set OCR text.

        rtlist      sequence of (rect, text), where:
                        rect    Rect
                        text    str
        charset     'DEFAULT' | 'ANSI' | 'SYMBOL' | 'MAC' | 'SHIFTJIS'
                              | 'HANGEUL' | 'CHINESEBIG5' | 'GREEK' | 'TURKISH'
                              | 'BALTIC' | 'RUSSIAN' | 'EASTEUROPE' | 'OEM'
        half_open   (bool) rect's are half open i.e. right-bottom is outside
        errors      'strict' | 'ignore' | 'replace' | 'xmlcharrefreplace'
                             | 'backslashreplace' | 'namereplace'
                             | 'surrogateescape'
                             | 'surrogatepass' (valid only for utf-8)

        unit        'mm' | 'px' (for Rect)

        CAUTION: After calling this method, text_regions()/re_regions() will
        raise AccessDeniedError, restricted by genuine XDWAPI.
        """
        if self.type != "IMAGE":
            raise TypeError("OCR text is available for image pages")
        rects = (XDW_RECT * len(rtlist))()
        crlf = "\x0d\x0a"
        text = []
        if unit == "mm":
            cx = lambda x: int(mm2px(x, self.resolution.x))
            cy = lambda y: int(mm2px(y, self.resolution.y))
        else:  # if unit == "px"
            cx = cy = int
        for i, (r, t) in enumerate(rtlist):
            text.append(t)
            if not isinstance(r, Rect):
                r = Rect(*r)
            if half_open:
                r = r.closed()
            rects[i].left = cx(r.left)
            rects[i].top = cy(r.top)
            rects[i].right = cx(r.right)
            rects[i].bottom = cy(r.bottom)
        info = XDW_OCR_TEXTINFO()
        info.nWidth = int(self.image_size.x)
        info.nHeight = int(self.image_size.y)
        info.charset = XDW_FONT_CHARSET.normalize(charset)
        encoding = f"cp{charset_to_codepage(info.charset)}"
        info.lpszText = crlf.join(text).encode(encoding, errors=errors) + b"\x00"
        info.nLineRect = len(rtlist)
        info.pLineRect = rects
        XDW_SetOcrData(self.doc.handle, self.absolute_page() + 1, info)

    def export(self, path=None):
        """Export page to another document.

        path    (str) export to {path};
                      with no dir, export to {document/binder dir}/{path}
                (None) export to
                      {document/binder dir}/{document name}_P{num}.xdw

        Returns the exported pathname which may differ from path.
        """
        return self.doc.export(self.pos, path=path)

    def export_image(self,
            path=None, dpi=600, color="COLOR", format=None, compress="NORMAL",
            direct=False):
        """Export page to image file.

        path        (str) export to {path};
                          with no dir, export to {document/binder dir}/{path}
                    (None) export to
                          {document/binder dir}/{document name}_P{num}.bmp
        dpi         (int) 10..600
        color       'COLOR' | 'MONO' | 'MONO_HIGHQUALITY'
        format      'BMP' | 'TIFF' | 'JPEG' | 'PDF'
        compress    for BMP, not available
                    for TIFF, 'NOCOMPRESS' | 'PACKBITS' |
                              'JPEG | 'JPEG_TTN2' | 'G4'
                    for JPEG, 'NORMAL' | 'HIGHQUALITY' | 'HIGHCOMPRESS'
                    for PDF,  'NORMAL' | 'HIGHQUALITY' | 'HIGHCOMPRESS' |
                              'MRC_NORMAL' | 'MRC_HIGHQUALITY' |
                              'MRC_HIGHCOMPRESS'
        direct      (bool) export internal compressed image data directly.
                    If True:
                      - dpi, color, format and compress are ignored.
                      - Exported image format is recognized with the
                        extension of returned pathname, which is either
                        'tiff', 'jpeg' or 'pdf'.
                      - Annotations and page forms are not included in
                        the exported image.  Image orientation depends
                        on the internal state, so check 'degree' attribute
                        of the page if needed.

        Returns the exported pathname which may differ from path.
        """
        return self.doc.export_image(self.pos,
                path=path, pages=1, dpi=dpi, color=color, format=format,
                compress=compress, direct=direct)

    def view(self, light=False, wait=True, fullscreen=False, zoom=0):
        """View page with DocuWorks Viewer (Light).

        light       (bool) force to use DocuWorks Viewer Light.
                    Note that DocuWorks Viewer is used if Light version is
                    not avaiable.
        wait        (bool) wait until viewer stops and get annotation info
        fullscreen  (bool) view in full screen (presentation mode)
        zoom        (int) in 10-1600 percent; 0 means 100%
                    (str) 'WIDTH' | 'HEIGHT' | 'PAGE'

        If wait is True, returns a list of AnnotationCache objects.

        If wait is False, returns (proc, path) where:

                proc    subprocess.Popen object
                path    pathname of temporary file begin viewed

        In this case, you should remove temp and its parent dir after use.
        """
        pc = PageCollection() + self
        r = pc.view(light=light, wait=wait, flat=True,
                    fullscreen=fullscreen, zoom=zoom)
        if wait:
            return r[0] if r else []
        return r

    def text_regions(self, text,
            ignore_case=False, ignore_width=False, ignore_hirakata=False):
        """Search text in page and get regions occupied by them.

        text            (str or bytes)
        ignore_case     (bool)
        ignore_width    (bool)
        ignore_hirakata (bool)

        Returns a list of Rect, or None if rect is unavailable.
        * No rects are given if OCR-ed on DW9+.
        * Rect is half-open i.e. right-bottom is outside.
        """
        result = []
        opt = XDW_FIND_TEXT_OPTION()
        opt.nIgnoreMode = 0
        if ignore_case:
            opt.nIgnoreMode |= XDW_IGNORE_CASE
        if ignore_width:
            opt.nIgnoreMode |= XDW_IGNORE_WIDTH
        if ignore_hirakata:
            opt.nIgnoreMode |= XDW_IGNORE_HIRAKATA
        opt.nReserved = opt.nReserved2 = 0
        """TODO: unicode handling.
        Currently Author has no idea to take unicode with ord < 256.
        Python's unicode may have inner representation with 0x00,
        e.g.  0x41 0x00 0x42 0x00 0x43 0x00 for "ABC".  This results in
        unexpected string termination e.g. "ABC" -> "A".  So, if the next
        if-block is not placed, you will get much more but inexact
        elements in result for abbreviated search string.
        """
        if isinstance(text, str):
            text = text.encode(CODEPAGE)  # TODO: how can we take all unicodes?
        if 255 < len(text):
            raise ValueError("text length must be <= 255")
        fh = XDW_FindTextInPage(
                self.doc.handle, self.absolute_page() + 1, text, opt)
        try:
            while fh:
                try:
                    n = XDW_GetNumberOfRectsInFoundObject(fh)
                except InvalidArgError as e:
                    break
                for i in range(n):
                    r, s = XDW_GetRectInFoundObject(fh, i + 1)
                    if s == XDW_FOUND_RECT_STATUS_HIT:
                        # Rect is half open.
                        r.right += 1
                        r.bottom += 1
                        r = Rect(r.left / XDWRES, r.top / XDWRES,
                                r.right / XDWRES, r.bottom / XDWRES)
                        r = r.half_open()
                        w, h = r.size()
                        if 9 <= XDWVER and self.size.x <= w or self.size.y <= h:
                            r = None
                    else:
                        r = None  # Actually rect is not available.
                    result.append(r)
                fh = XDW_FindNext(fh)
        finally:
            XDW_CloseFoundHandle(fh)
        return result

    def re_regions(self, pattern):
        """Search regular expression in page and get regions occupied.

        pattern     (str or regular expression supported by re module)

        Returns a list of Rect or None (when rect is unavailable).
        """
        if isinstance(pattern, (str, bytes)):
            opt = re.LOCALE if isinstance(pattern, bytes) else re.UNICODE
            pattern = re.compile(pattern, opt)
        result = []
        for text in set(pattern.findall(self.fulltext())):
            result.extend(self.text_regions(text))
        return result
