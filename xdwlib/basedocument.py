#!/usr/bin/env python2.6
#vim:fileencoding=cp932:fileformat=dos

"""basedocument.py -- DocuWorks library for Python.

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import os

from xdwapi import *
from common import *
from observer import *
from struct import Point
from xdwfile import xdwopen
from page import Page, PageCollection


__all__ = ("BaseDocument",)


class BaseDocument(Subject):

    """DocuWorks document base class.

    This class is a base class, which is expected to be inherited by Document
    or DocumentInBinder class.

    Each BaseDocument instance has an observer dict.  This dict holds
    (page_number, Page_object) pairs, and is used to notify page insertion
    or deletion.  Receiving this notification, every Page object should adjust
    its memorized page number.
    """

    def __init__(self):
        Subject.__init__(self)

    def __repr__(self):  # abstract
        raise NotImplementedError()

    def __str__(self):  # abstract
        raise NotImplementedError()

    def __len__(self):
        return self.pages

    def __getitem__(self, pos):
        return self.page(pos)

    def __setitem__(self, pos, val):
        raise NotImplementedError()

    def __iter__(self):
        for pos in xrange(self.pages):
            yield self.page(pos)

    def absolute_page(self, pos):
        """Abstract method to get absolute page number in binder/document."""
        raise NotImplementedError()

    def page(self, pos):
        """Get a Page."""
        if self.pages <= pos:
            raise IndexError("Page number must be < %d, %d given" % (
                    self.pages, pos))
        if pos not in self.observers:
            self.observers[pos] = Page(self, pos)
        return self.observers[pos]

    def range(self, start, end):
        return PageCollection(self.page(i) for i in xrange(start, end))

    def append(self, obj):
        """Append a Page/PageCollection/Document at the end of document."""
        self.insert(self.pages, obj)

    def insert(self, pos, obj):
        """Insert a Page/PageCollection/Document.

        insert(pos, obj) --> None

        pos: position to insert; starts with 0
        obj: Page/PageCollection/BaseDocument
        """
        doc = None
        if isinstance(obj, Page): pc = PageCollection([obj])
        elif isinstance(obj, PageCollection):
            pc = obj
        elif isinstance(obj, BaseDocument):
            pc = PageCollection(obj)
        elif isinstance(obj, basestring):  # XDW path
            assert obj.lower().endswith(".xdw")  # binder is not acceptable
            doc = xdwopen(obj)
            pc = PageCollection(doc)
        else:
            raise ValueError("can't insert %s object" % (obj.__class__))
        if pos < 0:
            pos += self.pages
        temp = os.path.join(self.dirname(), "$$%s.xdw" % (self.name,))
        temp = pc.combine(temp)
        XDW_InsertDocument(self.handle, self.absolute_page(pos) + 1, temp)
        os.remove(temp)
        if doc:
            doc.close()
        # Check inserted pages in order to attach them to this document and
        # shift observer entries appropriately.
        for p in xrange(pos, pos + len(pc)):
            page = Page(self, p)
        self.pages += len(pc)

    def insert_image(self, pos, input_path,
            fitimage=XDW_CREATE_FITDEF,
            compress=XDW_COMPRESS_NORMAL,
            zoom=0,  # %; 0=100%
            size=Point(0, 0),  # Point(width, height); 0=A4R
            align=("center", "center"),  # left/center/right, top/center/bottom
            maxpapersize=XDW_CREATE_DEFAULT_SIZE,
            ):
        """Insert a page created from image files."""
        if pos < 0:
            pos += self.pages
        opt = XDW_CREATE_OPTION_EX2()
        opt.nFitImage = XDW_CREATE_FITIMAGE.normalize(fitimage)
        opt.nCompress = XDW_COMPRESS.normalize(compress)
        #opt.nZoom = 0
        opt.nZoomDetail = int(zoom * 1000)  # .3f
        # NB. Width and height are valid only for XDW_CREATE_USERDEF(_FIT).
        opt.nWidth, opt.nHeight = size.int() * 100  # .2f;
        opt.nHorPos = XDW_CREATE_HPOS.normalize(align[0])
        opt.nVerPos = XDW_CREATE_VPOS.normalize(align[1])
        opt.nMaxPaperSize = XDW_CREATE_MAXPAPERSIZE.normalize(maxpapersize)
        XDW_CreateXdwFromImageFileAndInsertDocument(
                self.handle, self.absolute_page(pos) + 1, input_path, opt)
        # Check inserted pages in order to attach them to this document and
        # shift observer entries appropriately.
        page = Page(self, pos)
        self.pages += 1
        ## TODO: recalc page data if image has been divided into pages.

    def export_image(self, pos, pages=1, path=None,
            dpi=600, color="COLOR", format=None, compress="NORMAL"):
        """Export page(s) to image file.

        export_image(pos, pages=1, path=None, dpi=600, color="COLOR",
                     format=None, compress="NORMAL")

        pos:        (int) or (tuple like slice)
        dpi:        (int) 10..600
        color:      COLOR | MONO | MONO_HIGHQUALITY
        format:     BMP | TIFF | JPEG | PDF
        compress:   for BMP, not available
                    for TIFF, NOCOMPRESS | PACKBITS | JPEG | JPEG_TTN2 | G4
                    for JPEG, NORMAL | HIGHQUALITY | HIGHCOMPRESS
                    for PDF,  NORMAL | HIGHQUALITY | HIGHCOMPRESS |
                              MRC_NORMAL | MRC_HIGHQUALITY | MRC_HIGHCOMPRESS
        """
        path = cp(path)
        if isinstance(pos, (list, tuple)):
            pos, pages = pos
            pages -= pos
        if not format:
            _, ext = os.path.splitext(path)
            ext = ((ext or "").lstrip(".") or "bmp").lower()
            table = {"dib":"bmp", "tif":"tiff", "jpg":"jpeg"}
            format = table.get(ext, ext)
        if format.lower() not in ("bmp", "tiff", "jpeg", "pdf"):
            raise TypeError("image type must be BMP, TIFF, JPEG or PDF.")
        if not path:
            path = "%s_P%d" % (self.name, pos + 1)
            path = adjust_path(path,
                    default_dir=self.dirname(), coding=CODEPAGE)
            if 1 < pages:
                path += "-%d" % (pos + 1) + (pages - 1)
            path += "." + format
        dpi = int(dpi)
        if not (10 <= dpi <= 600):
            raise ValueError("specify resolution between 10 and 600")
        opt = XDW_IMAGE_OPTION_EX()
        opt.nDpi = int(dpi)
        opt.nColor = XDW_IMAGE_COLORSCHEME.normalize(color)
        opt.nImageType = XDW_IMAGE_FORMAT.normalize(format)
        if opt.nImageType == XDW_IMAGE_DIB:
            dopt = None
        elif opt.nImageType == XDW_IMAGE_TIFF:
            dopt = XDW_IMAGE_OPTION_TIFF()
            dopt.nCompress = XDW_COMPRESS.normalize(compress)
            if dopt.nCompress not in (
                    XDW_COMPRESS_NOCOMPRESS,
                    XDW_COMPRESS_PACKBITS,
                    XDW_COMPRESS_JPEG,
                    XDW_COMPRESS_JPEG_TTN2,
                    XDW_COMPRESS_G4,
                    ):
                dopt.nCompress = XDW_COMPRESS_NOCOMPRESS
            dopt.nEndOfMultiPages = (pos + 1) + (pages - 1)
        elif opt.nImageType == XDW_IMAGE_JPEG:
            dopt = XDW_IMAGE_OPTION_JPEG()
            dopt.nCompress = XDW_COMPRESS.normalize(compress)
            if dopt.nCompress not in (
                    XDW_COMPRESS_NORMAL,
                    XDW_COMPRESS_HIGHQUALITY,
                    XDW_COMPRESS_HIGHCOMPRESS,
                    ):
                dopt.nCompress = XDW_COMPRESS_NORMAL
        elif opt.nImageType == XDW_IMAGE_PDF:
            dopt = XDW_IMAGE_OPTION_PDF()
            dopt.nCompress = XDW_COMPRESS.normalize(compress)
            if dopt.nCompress not in (
                    XDW_COMPRESS_NORMAL,
                    XDW_COMPRESS_HIGHQUALITY,
                    XDW_COMPRESS_HIGHCOMPRESS,
                    XDW_COMPRESS_MRC_NORMAL,
                    XDW_COMPRESS_MRC_HIGHQUALITY,
                    XDW_COMPRESS_MRC_HIGHCOMPRESS,
                    ):
                dopt.nCompress = XDW_COMPRESS_MRC_NORMAL
            dopt.nEndOfMultiPages = (pos + 1) + (pages - 1)
            # Compression method option is deprecated.
            dopt.nConvertMethod = XDW_CONVERT_MRC_OS
        opt.pDetailOption = cast(pointer(dopt), c_void_p)
        XDW_ConvertPageToImageFile(
                self.handle, self.absolute_page(pos) + 1, path, opt)

    def delete(self, pos):
        """Delete a page."""
        page = self.page(pos)
        XDW_DeletePage(self.handle, self.absolute_page(pos) + 1)
        self.detach(page, EV_PAGE_REMOVED)
        self.pages -= 1

    def rasterize(self, pos, dpi=600, color="COLOR"):
        """Rasterize; convert an application page into DocuWorks image page."""
        import tempfile
        dpi = int(dpi)
        if not (10 <= dpi <= 600):
            raise ValueError("specify resolution between 10 and 600")
        opt = XDW_IMAGE_OPTION()
        opt.nDpi = int(dpi)
        opt.nColor = XDW_IMAGE_COLORSCHEME.normalize(color)
        temp = tempfile.NamedTemporaryFile(suffix=".bmp")
        temppath = temp.name
        temp.close()  # On Windows, you cannot reopen temp.  TODO: better code
        XDW_ConvertPageToImageFile(
                self.handle, self.absolute_page(pos) + 1, temppath, opt)
        self.insert_image(pos, temppath)  # Insert rasterized image page.
        self.delete(pos + 1)  # Delete original application page.
        os.remove(temppath)

    def content_text(self):
        """Get all content text."""
        return joinf(PSEP, [page.content_text() for page in self])

    def annotation_text(self):
        """Get all text in annotations."""
        return joinf(PSEP, [page.annotation_text() for page in self])

    def fulltext(self):
        """Get all content and annotation text."""
        return joinf(PSEP, [
                joinf(ASEP, [page.content_text(), page.annotation_text()])
                for page in self])

    def find_content_text(self, pattern):
        """Find given pattern (text or regex) in all content text."""
        return self.find(pattern, func=lambda page: page.content_text())

    def find_annotation_text(self, pattern):
        """Find given pattern (text or regex) in all annotation text."""
        return self.find(pattern, func=lambda page: page.annotation_text())

    def find_fulltext(self, pattern):
        """Find given pattern in all content and annotation text."""
        return self.find(pattern)

    def find(self, pattern, func=None):
        """Find given pattern (text or regex) through document.

        find(pattern, func) --> PageCollection

        pattern:  a string/unicode or regexp (by re module)
        func:  a function which takes a page and returns text in it
               (default) lambda page: page.fulltext()
        """
        func = func or (lambda page: page.fulltext())
        if isinstance(pattern, (str, unicode)):
            f = lambda page: pattern in func(page)
        else:
            f = lambda page: pattern.search(func(page))
        return PageCollection(filter(f, self))

    def dirname(self):
        """Abstract method for concrete dirname()."""
        raise NotImplementedError()


