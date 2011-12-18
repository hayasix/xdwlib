#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""page.py -- DocuWorks library for Python.

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import os
import tempfile

from xdwapi import *
from common import *
from observer import *
from struct import Point, Rect
from annotatable import Annotatable


__all__ = ("Page", "PageCollection")


class PageCollection(list):

    """Page collection ie. container for pages."""

    def __repr__(self):
        return u"PageCollection(%s)" % ", ".join(
                "%s[%d]" % (page.doc.name, page.pos) for page in self)

    def __add__(self, y):
        if isinstance(y, Page):
            return PageCollection(list.__add__(self, [y]))
        elif isinstance(y, PageCollection):
            return PageCollection(list.__add__(self, y))
        raise TypeError("can only concatenate Page or PageCollection "
                        "to PageCollection")

    def __iadd__(self, y):
        if isinstance(y, Page):
            self.append(y)
        elif isinstance(y, PageCollection):
            self.extend(y)
        else:
            TypeError("can only concatenate Page or PageCollection "
                      "to PageCollection")
        return self

    def save(self, path):
        """Create a binder (XBD file) as a container for page collection."""
        from binder import Binder, create_binder
        create_binder(path)
        binder = Binder(path)
        for pos, page in enumerate(self):
            # Preserve original document name.
            temp = page.copy()
            XDW_InsertDocumentToBinder(binder.handle, pos + 1, temp)
            os.remove(temp)
        binder.save()
        binder.close()
        return path

    def combine(self, path=None):
        """Create a document (XDW file) as a container for page collection.

        Returns path;  if no path is given, this method creates a temporary
        file somewhere and returns its path.  You have to remove the temporary
        file after use.
        """
        from document import Document
        path = path or tempfile.mkstemp(".xdw")
        path = self[0].copy(path)
        doc = Document(path)
        for pos, page in enumerate(self[1:]):
            temp = page.copy()
            XDW_InsertDocument(doc.handle, pos + 1 + 1, temp)
            os.remove(temp)
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
        page_info = XDW_GetPageInformation(
                self.doc.handle, abspos + 1, extend=True)
        self.size = Point(
                page_info.nWidth / 100.0,
                page_info.nHeight / 100.0)  # float, in mm
        # XDW_PGT_FROMIMAGE/FROMAPPL/NULL
        self.page_type = XDW_PAGE_TYPE[page_info.nPageType]
        self.resolution = Point(
                Page.norm_res(page_info.nHorRes),
                Page.norm_res(page_info.nVerRes))  # dpi
        self.compress_type = XDW_COMPRESS[page_info.nCompressType]
        self.annotations = page_info.nAnnotations
        self.degree = page_info.nDegree
        self.original_size = Point(
                page_info.nOrgWidth / 100.0,
                page_info.nOrgHeight / 100.0)  # mm
        self.original_resolution = Point(
                Page.norm_res(page_info.nOrgHorRes),
                Page.norm_res(page_info.nOrgVerRes))  # dpi
        self.image_size = Point(
                page_info.nImageWidth,
                page_info.nImageHeight)  # px
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

    def absolute_page(self):
        return self.doc.absolute_page(self.pos)

    def __repr__(self):
        return u"Page(%s[%d])" % (self.doc.name, self.pos)

    def __str__(self):
        return u"Page(page %d: %.2f*%.2fmm, %s, %d annotations)" % (
                self.pos, self.size.x, self.size.y, self.page_type,
                self.annotations)

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

    def __getattr__(self, name):
        if "_" in name:
            form, name = self._split_attrname(name)
            if form is not None:
                name = inner_attribute_name(name)
                return XDW_GetPageFormAttribute(self.doc.handle, form, name)
        return self.__dict__[name]

    def __setattr__(self, name, value):
        self.__dict__[name] = value

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
            raise ValueError("illegal event type: %d" % event.type)

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

    def content_text(self):
        """Returns content text of page."""
        return XDW_GetPageTextToMemoryW(
                self.doc.handle, self.absolute_page() + 1)

    def rotate(self, degree=0, auto=False):
        """Rotate a page.

        rotate(degree=0, auto=False)
            degree  90, 180 or 270
            auto    True/False
        """
        abspos = self.absolute_page()
        if auto:
            XDW_RotatePageAuto(self.doc.handle, abspos + 1)
        else:
            XDW_RotatePage(self.doc.handle, abspos + 1, degree)
        self.reset_attr()

    def reduce_noise(self, level=XDW_REDUCENOISE_NORMAL):
        """Process a page by noise reduction engine.

        reduce_noise(self, level=XDW_REDUCENOISE_NORMAL)
            level   XDW_REDUCENOISE_NORMAL
                    XDW_REDUCENOISE_WEAK
                    XDW_REDUCENOISE_STRONG
        """
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
        """Process a page by OCR engine."""
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
            rectlist = XDW_RECT() * len(rects)
            for r, rect in zip(rectlist, rects):
                r.left, r.top, r.right, r.bottom = rect.left
            opt.pAreaRects = byref(rectlist)
        else:
            opt.pAreaRects = NULL
        XDW_ApplyOcr(self.doc.handle, self.absolute_page() + 1,
                engine, opt)

    def clear_ocr_text(self):
        """Clear OCR text."""
        XDW_SetOcrData(self.doc.handle, self.absolute_page(), NULL)

    def copy(self, path=None):
        """Copy current page and create another document.

        Returns the path name of created XDW file.
        Default path name is "DOCUMENTNAME_Pxx.xdw".
        """
        if path:
            path = cp(path)
        else:
            path = "%s_P%d.xdw" % (self.doc.name, self.pos + 1)
            path = cp(path, dir=self.doc.dirname())
        # Append _2, _3, _4,...  for filename collision.
        n = 1
        root, ext = os.path.splitext(path)
        while os.path.exists(path):
            n += 1
            path = "%s_%d" % (root, n) + ext
        XDW_GetPage(self.doc.handle, self.absolute_page() + 1, path)
        return path

    def view(self, wait=True, light=False):
        """View current page with DocuWorks Viewer (Light)."""
        import subprocess
        env = environ()
        viewer = env.get("DWVIEWERPATH")
        if light or not viewer:
            viewer = env.get("DWVLTPATH", viewer)
        if not viewer:
            raise NotInstalledError("DocuWorks/Viewer is not installed")
        temp = tempfile.NamedTemporaryFile(suffix=".xdw")
        temppath = temp.name
        temp.close()  # On Windows, you cannot reopen temp.  TODO: better code
        self.copy(path=temppath)
        proc = subprocess.Popen([viewer, temppath])
        if wait:
            proc.wait()
            os.remove(temppath)
            return None
        else:
            return (proc, temppath)

    def text_regions(self, text,
            ignore_case=False, ignore_width=False, ignore_hirakata=False):
        """Search text in current page and get regions occupied by them.

        text_regions(self, text, ignore_case=False, ignore_width=False, ignore_hirakata=False):

        Returns a list of Rect or None (when rect is unavailable).
        """
        result = []
        opt = XDW_FIND_TEXT_OPTION()
        opt.nIgnoreMode = 0
        if ignore_case: opt.nIgnoreMode |= XDW_IGNORE_CASE
        if ignore_width: opt.nIgnoreMode |= XDW_IGNORE_WIDTH
        if ignore_hirakata: opt.nIgnoreMode |= XDW_IGNORE_HIRAKATA
        opt.nReserved = opt.nReserved2 = 0
        """TODO: unicode handling.
        Currently Author has no idea to take unicode with ord < 256.
        Python's unicode may have inner representation with 0x00,
        eg.  0x41 0x00 0x42 0x00 0x43 0x00 for "ABC".  This results in
        unexpected string termination eg. "ABC" -> "A".  So, if the next
        if-block is not placed, you will get much more but inexact
        elements in result for abbreviated search string.
        """
        if isinstance(text, unicode):
            text = text.encode(CODEPAGE)  # TODO: how can we take all unicodes?
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
                        r.right +=1
                        r.bottom += 1
                        r = Rect(r.left / 100.0, r.top / 100.0,
                                r.right / 100.0, r.bottom / 100.0)
                    else:
                        r = None  # Actually rect is not available.
                    result.append(r)
                fh = XDW_FindNext(fh)
        finally:
            XDW_CloseFoundHandle(fh)
        return result

    def re_regions(self, pattern):
        if isinstance(pattern, basestring):
            import re
            opt = re.LOCALE if isinstance(pattern, str) else re.UNICODE
            pattern = re.compile(pattern, opt)
        result = []
        for text in set(pattern.findall(self.fulltext())):
            result.extend(self.text_regions(text))
        return result
