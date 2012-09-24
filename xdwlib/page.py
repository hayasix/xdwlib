#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""page.py -- Page and PageCollection

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

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

from xdwapi import *
from common import *
from observer import *
from struct import Point, Rect
from annotatable import Annotatable


__all__ = ("Page", "PageCollection")


class PageCollection(list):

    """Page collection i.e. container for pages."""

    def __repr__(self):
        return u"{cls}({seq})".format(
                cls=self.__class__.__name__,
                seq=", ".join(u"{0}[{1}]".format(pg.doc.name, pg.pos)
                        for pg in self))

    def __add__(self, y):
        if isinstance(y, Page):
            return PageCollection(list.__add__(self, [y]))
        elif isinstance(y, PageCollection):
            return PageCollection(list.__add__(self, y))
        raise TypeError(
                "only Page or PageCollection can be added")

    def __iadd__(self, y):
        if isinstance(y, Page):
            self.append(y)
        elif isinstance(y, PageCollection):
            self.extend(y)
        else:
            raise TypeError(
                    "only Page or PageCollection can be added")
        return self

    def view(self, light=False, wait=True, flat=False, group=True, *options):
        """View pages with DocuWorks Viewer (Light).

        light       (bool) force to use DocuWorks Viewer Light.
                    Note that DocuWorks Viewer is used if Light version is
                    not avaiable.
        wait        (bool) wait until viewer stops.
                    Given False, (proc, temp) is returned.  Users should
                    remove the file of path after the Popen object ends.
        flat        (bool) combine pages into a single document.
        group       (bool) group continuous pages by original document,
                    i.e. create document-in-binder.
        options     optional arguments for DocuWorks Viewer (Light).
                    See DocuWorks genuine help document.

        Returns (proc, temp) if wait is False, where:
                proc    subprocess.Popen object
                temp    pathname of temporary file to view.

        NB. Attachments are not shown.
        NB. Viewing signed pages will raise AccessDeniedError.
        """
        tempdir = os.path.split(mktemp(nofile=True))[0]
        tmp = os.path.join(tempdir, u"{0}_P{1}.{2}".format(
                self[0].doc.name, self[0].pos + 1, "xdw" if flat else "xbd"))
        temp = self.export(tmp, flat=flat, group=group)
        args = [get_viewer(light=light)]
        args.extend(options)
        args.append(temp)
        proc = subprocess.Popen(args)
        if wait:
            proc.wait()
            rmtemp(temp)
            return None
        else:
            return (proc, temp)

    def group(self):
        """Group continuous pages by original document."""
        if len(self) < 2:
            return [self]
        s = [False] + [(x.doc is y.doc) for (x, y) in zip(self[:-1], self[1:])]
        pc = list(self)
        result = []
        try:
            while s:
                p = s.index(False, 1)
                result.append(PageCollection(pc[:p]))
                del s[:p]
                del pc[:p]
        except ValueError:
            result.append(PageCollection(pc))
        return result

    def export(self, path=None, flat=False, group=True):
        """Create a binder or document as a container for page collection.

        path    (unicode) pathname for output
        flat    (bool) create document instead of binder
        group   (bool) group continuous pages by original document,
                i.e. create document-in-binder.

        Returns actual pathname of generated file, which may be different
        from `path' argument.
        """
        from document import create as create_document
        from binder import create_binder
        from xdwfile import xdwopen
        path = derivative_path(adjust_path(uc(path or
                (self[0].doc.name + (".xdw" if flat else ".xbd")))))
        if flat:
            path = create_document(output_path=path)
        else:
            path = create_binder(path)
        doc = xdwopen(path)
        temp = mktemp()
        tempdir = os.path.split(temp)[0]
        if flat:
            for pg in self:
                tmp = pg.export(os.path.join(tempdir, pg.doc.name + ".xdw"))
                doc.append(tmp)
                os.remove(tmp)
            del doc[0]  # Delete the initial blank page.
        elif group:
            for pc in self.group():
                tmp = os.path.join(tempdir, pc[0].doc.name + ".xdw")
                tmp = pc.export(tmp, flat=True)
                doc.append(tmp)
                os.remove(tmp)
        else:
            for pos, pg in enumerate(self):
                tmp = os.path.join(tempdir,
                        "{0}_P{1}.xdw".format(pg.doc.name, pg.pos + 1))
                tmp = pg.export(tmp)
                doc.append(tmp)
                os.remove(tmp)
        rmtemp(temp)
        doc.save()
        doc.close()
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
                pginfo.nWidth / 100.0,
                pginfo.nHeight / 100.0)  # float, in mm
        # XDW_PGT_FROMIMAGE/FROMAPPL/NULL
        self.type = XDW_PAGE_TYPE[pginfo.nPageType]
        self.resolution = Point(
                Page.norm_res(pginfo.nHorRes),
                Page.norm_res(pginfo.nVerRes))  # dpi
        self.compress_type = XDW_COMPRESS[pginfo.nCompressType]
        self.annotations = pginfo.nAnnotations
        self.degree = pginfo.nDegree
        self.original_size = Point(
                pginfo.nOrgWidth / 100.0,
                pginfo.nOrgHeight / 100.0)  # mm
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
        return u"{cls}({doc}[{pos}])".format(
                cls=self.__class__.__name__,
                doc=self.doc.name,
                pos=self.pos)

    def __str__(self):
        return (u"Page({doc}[{pos}]; "
                u"{width:.2f}*{height:.2f}mm, "
                u"{type}, {anns} annotations)").format(
                doc=self.doc.name,
                pos=self.pos,
                width=self.size.x,
                height=self.size.y,
                type=self.type,
                anns=self.annotations)

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
                return XDW_GetPageFormAttribute(doc.handle, form, name)
        return Annotatable.__getattribute__(self, name)

    def __setattr__(self, name, value):
        Annotatable.__setattr__(self, name, value)

    def get_userattr(self, name, default=None):
        """Get pagewise user defined attribute.

        name        (str or unicode) attribute name
        default     value to return if no attribute named name exist
        """
        try:
            return XDW_GetPageUserAttribute(
                    self.doc.handle, self.absolute_page() + 1, cp(name))
        except InvalidArgError:
            return default

    def set_userattr(self, name, value):
        """Set pagewise user defined attribute."""
        if isinstance(name, unicode):
            name = name.encode(CODEPAGE)
        XDW_SetPageUserAttribute(
                self.doc.handle, self.absolute_page() + 1, name, value)

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
            raise ValueError("illegal event type: {0}".format(event.type))

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

    def rasterize(self):
        """Rasterize; convert an application page into DocuWorks image page.

        Resolution of converted page is <= 600 dpi even for more precise page.

        CAUTION: Page will be replaced with just an image.  Visible annotations
        are drawn as parts of image and cannot be handled as effective
        annotations any more.  Application/OCR text will be lost.
        """
        if self.type == "APPLICATION":
            doc, pos = self.doc, self.pos
            doc.rasterize(pos)
            self = doc.page(pos)  # reset

    def rotate(self, degree=0, auto=False):
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
        if self.type != "IMAGE":
            raise TypeError("rotation is available for image pages")
        doc, pos = self.doc, self.pos
        doc.rotate(pos, degree=degree, auto=auto)
        self = doc.page(pos)  # reset

    def reduce_noise(self, level="NORMAL"):
        """Process page by noise reduction engine.

        level   "NORMAL" | "WEAK" | "STRONG"
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
            ):
        """Process page by OCR engine.

        engine          "DEFAULT" | "WINREADER PRO"
        strategy        "STANDARD" | "SPEED" | "ACCURACY"
        proprocessing   "SPEED" | "ACCURACY"
        noise_reduction "NONE" | "NORMAL" | "WEAK" | "STRONG"
        deskew          (bool)
        form            "AUTO" | "TABLE" | "WRITING"
        column          "AUTO" | "HORIZONTAL_SINGLE" | "HORIZONTAL_MULTI"
                               | "VERTICAL_SINGLE"   | "VERTICAL_MULTI"
        rects           (list of Rect)
        language        "AUTO" | "JAPANESE" | "ENGLISH"
        main_language   "BALANCED" | "JAPANESE" | "ENGLISH"
        use_ascii       (bool)
        insert_space    (bool)
        verbose         (bool)
        """
        if self.type != "IMAGE":
            raise TypeError("OCR is available for image pages")
        opt = XDW_OCR_OPTION_V7()
        engine = XDW_OCR_ENGINE.normalize(engine)
        opt.nEngineLevel = XDW_OCR_STRATEGY.normalize(strategy)
        opt.nPriority = XDW_OCR_PREPROCESSING.normalize(preprocessing)
        opt.nNoiseReduction = XDW_OCR_NOISEREDUCTION.normalize(noise_reduction)
        opt.nAutoDeskew = bool(deskew)
        opt.nForm = XDW_OCR_FORM.normalize(form)
        opt.nColumn = XDW_OCR_COLUMN.normalize(column)
        opt.nLanguage = XDW_OCR_LANGUAGE.normalize(language)
        opt.nLanguageMixedRate = XDW_OCR_MAIN_LANGUAGE.normalize(main_language)
        opt.nHalfSizeChar = bool(use_ascii)
        opt.nInsertSpaceCharacter = bool(insert_space)
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
        XDW_ApplyOcr(self.doc.handle, self.absolute_page() + 1, engine, opt)

    def clear_ocr_text(self):
        """Clear OCR text."""
        if self.type != "IMAGE":
            raise TypeError("OCR text is available for image pages")
        XDW_SetOcrData(self.doc.handle, self.absolute_page() + 1, NULL)

    def set_ocr_text(self, rtlist, charset="SHIFTJIS", half_open=True):
        """Set OCR text.

        rtlist      sequence of (rect, text), where:
                        rect    Rect
                        text    basestring
        charset     'DEFAULT' | 'OEM' | 'ANSI' | 'SYMBOL' | 'MAC' |
                    'SHIFTJIS' | 'HANGEUL' | 'CHINESEBIG5' |
                    'GREEK' | 'TURKISH' | 'BALTIC' | 'RUSSIAN' |
                    'EASTEUROPE'
        half_open   (bool) rect's are half open i.e. right-bottom is outside

        CAUTION: After calling this method, text_regions()/re_regions() will
        raise AccessDeniedError, restricted by genuine XDWAPI.
        """
        if self.type != "IMAGE":
            raise TypeError("OCR text is available for image pages")
        rects = (XDW_RECT * len(rtlist))()
        crlf = "\x0d\x0a"
        text = []
        for i, (r, t) in enumerate(rtlist):
            text.append(cp(t.strip()) + crlf)  # TODO: cp() != charset
            if not isinstance(r, Rect):
                r = Rect(*r)
            if half_open:
                r = r.closed()
            rects[i].left = int(mm2px(r.left, self.resolution.x))
            rects[i].top = int(mm2px(r.top, self.resolution.y))
            rects[i].right = int(mm2px(r.right, self.resolution.x))
            rects[i].bottom = int(mm2px(r.bottom, self.resolution.y))
        text = "".join(text)
        info = XDW_OCR_TEXTINFO()
        info.nWidth = int(self.image_size.x)
        info.nHeight = int(self.image_size.y)
        info.charset = XDW_FONT_CHARSET.normalize(charset)
        info.lpszText = text
        info.nLineRect = len(rtlist)
        info.pLineRect = pointer(rects[0])
        XDW_SetOcrData(self.doc.handle, self.absolute_page() + 1, info)

    def export(self, path=None):
        """Export page to another document.

        path    (str or unicode) pathname to export;
                given only basename without directory, exported file is
                placed in the very directory of the original document.

        Returns the actual pathname of generated XDW file, which may be
        different from `path' argument.  If path is not available,
        default name "DOCUMENTNAME_Pxx.xdw" will be used.
        """
        return self.doc.export(self.pos, path=path)

    def export_image(self,
            path=None, dpi=600, color="COLOR", format=None, compress="NORMAL",
            direct=False):
        """Export page to image file.

        path        (str or unicode) pathname to output
        dpi         (int) 10..600
        color       "COLOR" | "MONO" | "MONO_HIGHQUALITY"
        format      "BMP" | "TIFF" | "JPEG" | "PDF"
        compress    for BMP, not available
                    for TIFF, "NOCOMPRESS" | "PACKBITS" |
                              "JPEG | "JPEG_TTN2" | "G4"
                    for JPEG, "NORMAL" | "HIGHQUALITY" | "HIGHCOMPRESS"
                    for PDF,  "NORMAL" | "HIGHQUALITY" | "HIGHCOMPRESS" |
                              "MRC_NORMAL" | "MRC_HIGHQUALITY" |
                              "MRC_HIGHCOMPRESS"
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

        Returns actual pathname of created image file.
        """
        return self.doc.export_image(self.pos,
                path=path, pages=1, dpi=dpi, color=color, format=format,
                compress=compress, direct=direct)

    def view(self, light=False, wait=True, *options):
        """View page with DocuWorks Viewer (Light).

        light       (bool) force to use DocuWorks Viewer Light.
                    Note that DocuWorks Viewer is used if Light version is
                    not avaiable.
        wait        (bool) wait until viewer stops.
                    Given False, (Popen, path) is returned.  Users should
                    remove the file of path after the Popen object ends.
        options     optional arguments for DocuWorks Viewer (Light).
                    See DocuWorks genuine help document.
        """
        pc = PageCollection() + self
        return pc.view(light=light, wait=wait, flat=True, *options)

    def text_regions(self, text,
            ignore_case=False, ignore_width=False, ignore_hirakata=False):
        """Search text in page and get regions occupied by them.

        Returns a list of Rect or None (when rect is unavailable).
        Note that Rect is half-open i.e. right-bottom is outside.
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
        if isinstance(text, unicode):
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
                for i in xrange(n):
                    r, s = XDW_GetRectInFoundObject(fh, i + 1)
                    if s == XDW_FOUND_RECT_STATUS_HIT:
                        # Rect is half open.
                        r.right += 1
                        r.bottom += 1
                        r = Rect(r.left / 100.0, r.top / 100.0,
                                r.right / 100.0, r.bottom / 100.0)
                        r = r.half_open()
                    else:
                        r = None  # Actually rect is not available.
                    result.append(r)
                fh = XDW_FindNext(fh)
        finally:
            XDW_CloseFoundHandle(fh)
        return result

    def re_regions(self, pattern):
        """Search regular expression in page and get regions occupied.

        Returns a list of Rect or None (when rect is unavailable).
        """
        if isinstance(pattern, basestring):
            opt = re.LOCALE if isinstance(pattern, str) else re.UNICODE
            pattern = re.compile(pattern, opt)
        result = []
        for text in set(pattern.findall(self.fulltext())):
            result.extend(self.text_regions(text))
        return result
