#!/usr/bin/env python2.6
#vim:fileencoding=cp932:fileformat=dos

"""basedocument.py -- BaseDocument, base class for Document/DocumentInBinder

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import sys
import os
import tempfile
from cStringIO import StringIO

from xdwapi import *
from common import *
from observer import *
from struct import Point
from xdwfile import xdwopen
from page import Page, PageCollection


PIL_ENABLED = True
try:
    import Image
except ImportError:
    PIL_ENABLED = False


__all__ = ("BaseDocument",)


def check_PIL():
    if PIL_ENABLED:
        return
    raise NotImplementedError("Install PIL (Python Imaging Library) package.")


class BaseDocument(Subject):

    """DocuWorks document base class.

    This class is a base class, which is expected to be inherited by Document
    or DocumentInBinder class.

    Each BaseDocument instance has an observer dict.  This dict holds
    (page_number, Page_object) pairs, and is used to notify page insertion
    or deletion.  Receiving this notification, every Page object should adjust
    its memorized page number.
    """

    def _pos(self, pos, append=False):
        append = 1 if append else 0
        if not (-self.pages <= pos < self.pages + append):
            raise IndexError(
                    "Page number must be in [{0}, {1}), {2} given".format(
                    -self.pages, self.pages + append, pos))
        if pos < 0:
            pos += self.pages
        return pos

    def _slice(self, pos):
        if pos.step == 0 and pos.start != pos.stop:
            raise ValueError("slice.step must not be 0")
        return slice(
                self._pos(pos.start or 0),
                self.pages if pos.stop is None else pos.stop,
                1 if pos.step is None else pos.step)

    def __init__(self):
        Subject.__init__(self)

    def __repr__(self):  # abstract
        raise NotImplementedError()

    def __str__(self):  # abstract
        raise NotImplementedError()

    def __len__(self):
        return self.pages

    def __getitem__(self, pos):
        if isinstance(pos, slice):
            pos = self._slice(pos)
            return PageCollection(self.page(p)
                    for p in range(pos.start, pos.stop, pos.step))
        return self.page(pos)

    def __setitem__(self, pos, val):
        raise NotImplementedError()

    def __delitem__(self, pos):
        if isinstance(pos, slice):
            pos = self._slice(pos)
            for p in range(pos.start, pos.stop, pos.step):
                self.delete(p)
        else:
            self.delete(pos)

    def __iter__(self):
        for pos in xrange(self.pages):
            yield self.page(pos)

    def absolute_page(self, pos, append=False):
        """Abstract method to get absolute page number in binder/document."""
        raise NotImplementedError()

    def update_pages(self):
        """Abstract method to update number of pages."""
        raise NotImplementedError()

    def page(self, pos):
        """Get a Page."""
        pos = self._pos(pos)
        if pos not in self.observers:
            self.observers[pos] = Page(self, pos)
        return self.observers[pos]

    def append(self, obj):
        """Append a Page/PageCollection/Document at the end of document."""
        self.insert(self.pages, obj)

    def insert(self, pos, obj):
        """Insert a Page/PageCollection/Document.

        pos     position to insert; starts with 0
        obj     Page/PageCollection/BaseDocument or path
        """
        pos = self._pos(pos, append=True)
        doc = None
        if isinstance(obj, Page):
            pc = PageCollection([obj])
        elif isinstance(obj, PageCollection):
            pc = obj
        elif isinstance(obj, BaseDocument):
            pc = PageCollection(obj)
        elif isinstance(obj, basestring):  # XDW path
            assert obj.lower().endswith(".xdw")  # binder is not acceptable
            if isinstance(obj, str):
                obj = obj.decode(CODEPAGE)
            doc = xdwopen(obj)
            pc = PageCollection(doc)
        else:
            raise ValueError("can't insert {0} object".format(obj.__class__))
        temp = pc.combine(mktemp())
        XDW_InsertDocument(
                self.handle,
                self.absolute_page(pos, append=True) + 1,
                cp(temp))
        self.pages += len(pc)
        if doc:
            doc.close()
        os.remove(temp)
        # Check inserted pages in order to attach them to this document and
        # shift observer entries appropriately.
        for p in xrange(pos, pos + len(pc)):
            Page(self, p)

    def append_image(self, *args, **kw):
        """Append a page created from image file(s)."""
        self.insert_image(self.pages, *args, **kw)

    def insert_image(self, pos, input_path,
            fitimage="FITDEF",
            compress="NORMAL",
            zoom=0,  # %; 0=100%
            size=Point(0, 0),  # Point(width, height); 0=A4R
            align=("CENTER", "CENTER"),  # LEFT/CENTER/RIGHT, TOP/CENTER/BOTTOM
            maxpapersize="DEFAULT",
            ):
        """Insert a page created from image file(s).

        fitimage        "FITDEF" | "FIT" | "FITDEF_DIVIDEBMP" |
                        "USERDEF" | "USERDEF_FIT"
        compress        "NORMAL" | "LOSSLESS" | "NOCOMPRESS" |
                        "HIGHQUALITY" | "HIGHCOMPRESS" |
                        "JPEG" | "JPEG_TTN2" | "PACKBITS" | "G4" |
                        "MRC_NORMAL" | "MRC_HIGHQUALITY" | "MRC_HIGHCOMPRESS"
        zoom            (float) in percent; 0 means 100%.  < 1/1000 is ignored.
        size            (Point) in mm; for fitimange "userdef" or "userdef_fit"
                        (int)   1=A3R, 2=A3, 3=A4R, 4=A4, 5=A5R, 6=A5,
                                7=B4R, 8=B4, 9=B5R, 10=B5
        align           (horiz, vert) where:
                            horiz   "CENTER" | "LEFT" | "RIGHT"
                            vert    "CENTER" | "TOP" | "BOTTOM"
        maxpapersize    "DEFAULT" | "A3" | "2A0"
        """
        prev_pages = self.pages
        pos = self._pos(pos, append=True)
        input_path = uc(input_path)
        opt = XDW_CREATE_OPTION_EX2()
        opt.nFitImage = XDW_CREATE_FITIMAGE.normalize(fitimage)
        opt.nCompress = XDW_COMPRESS.normalize(compress)
        #opt.nZoom = 0
        opt.nZoomDetail = int(zoom * 1000)  # .3f
        # NB. Width and height are valid only for XDW_CREATE_USERDEF(_FIT).
        opt.nWidth, opt.nHeight = map(int, size * 100)  # .2f;
        opt.nHorPos = XDW_CREATE_HPOS.normalize(align[0])
        opt.nVerPos = XDW_CREATE_VPOS.normalize(align[1])
        opt.nMaxPaperSize = XDW_CREATE_MAXPAPERSIZE.normalize(maxpapersize)
        XDW_CreateXdwFromImageFileAndInsertDocument(
                self.handle,
                self.absolute_page(pos, append=True) + 1,
                cp(input_path),
                opt)
        self.update_pages()
        # Check inserted pages in order to attach them to this document and
        # shift observer entries appropriately.
        for p in range(pos, pos + (self.pages - prev_pages)):
            Page(self, p)

    def export_image(self, pos, path, pages=1,
            dpi=600, color="COLOR", format=None, compress="NORMAL"):
        """Export page(s) to image file.

        pos         (int or tuple (start stop) in half-open style like slice)
        path        (basestring) pathname to output
        pages       (int)
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
        """
        path = uc(path)
        if isinstance(pos, (list, tuple)):
            pos, pages = pos
            pages -= pos
        pos = self._pos(pos)
        if not format:
            _, ext = os.path.splitext(path)
            ext = ((ext or "").lstrip(".") or "bmp").lower()
            format = {"dib": "bmp", "tif": "tiff", "jpg": "jpeg"}.get(ext, ext)
        if format.lower() not in ("bmp", "tiff", "jpeg", "pdf"):
            raise TypeError("image type must be BMP, TIFF, JPEG or PDF.")
        if not path:
            path = u"{0}_P{1}".format(self.name, pos + 1)
            path = adjust_path(path, dir=self.dirname())
            if 1 < pages:
                path += "-{0}".format((pos + pages - 1) + 1)
            path += "." + format
        if not (10 <= dpi <= 600):
            raise ValueError("specify resolution between 10 and 600")
        opt = XDW_IMAGE_OPTION_EX()
        opt.nDpi = int(dpi)
        opt.nColor = XDW_IMAGE_COLORSCHEME.normalize(color)
        opt.nImageType = XDW_IMAGE_FORMAT.normalize(format)
        if opt.nImageType == XDW_IMAGE_DIB:
            opt.pDetailOption = NULL
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
            dopt.nEndOfMultiPages = (pos + pages - 1) + 1
            opt.pDetailOption = cast(pointer(dopt), c_void_p)
        elif opt.nImageType == XDW_IMAGE_JPEG:
            dopt = XDW_IMAGE_OPTION_JPEG()
            dopt.nCompress = XDW_COMPRESS.normalize(compress)
            if dopt.nCompress not in (
                    XDW_COMPRESS_NORMAL,
                    XDW_COMPRESS_HIGHQUALITY,
                    XDW_COMPRESS_HIGHCOMPRESS,
                    ):
                dopt.nCompress = XDW_COMPRESS_NORMAL
            opt.pDetailOption = cast(pointer(dopt), c_void_p)
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
            dopt.nEndOfMultiPages = (pos + pages - 1) + 1
            # Compression method option is deprecated.
            dopt.nConvertMethod = XDW_CONVERT_MRC_OS
            opt.pDetailOption = cast(pointer(dopt), c_void_p)
        XDW_ConvertPageToImageFile(
                self.handle, self.absolute_page(pos) + 1, cp(path), opt)

    def page_image(self, pos):
        """Returns page image with annotations in BMP/DIB format."""
        pg = self.page(pos)
        opt = XDW_IMAGE_OPTION()
        opt.nDpi = int(max(10, min(600, max(pg.resolution))))
        opt.nColor = XDW_IMAGE_COLORSCHEME.normalize(pg.color_scheme())
        return XDW_ConvertPageToImageHandle(self.handle, pos + 1, opt)

    def delete(self, pos):
        """Delete a page."""
        pos = self._pos(pos)
        pg = self.page(pos)
        XDW_DeletePage(self.handle, self.absolute_page(pos) + 1)
        self.detach(pg, EV_PAGE_REMOVED)
        self.pages -= 1

    def _preprocess(self, pos):
        pg = self.page(pos)
        dpi = int(max(pg.resolution))
        dpi = max(10, min(600, dpi))  # Force 10 <= dpi <= 600.
        color = pg.color_scheme()
        imagepath = mktemp(suffix=".tif")
        self.export_image(pos, imagepath,
                dpi=dpi, color=color, format="tiff", compress="nocompress")
        return imagepath

    def _postprocess(self, pos, imagepath):
        self.insert_image(pos, imagepath)  # Insert image page.
        self.delete(pos + 1)  # Delete original application page.
        os.remove(imagepath)

    def rasterize(self, pos):
        """Rasterize; convert an application page into DocuWorks image page."""
        pos = self._pos(pos)
        if self.page(pos).type == "APPLICATION":
            imagepath = self._preprocess(pos)
            self._postprocess(pos, imagepath)

    def rotate(self, pos, degree=0, auto=False, strategy=1):
        """Rotate page around the center.

        degree  (int) rotation angle in clockwise degree
        auto    (bool) automatic rotation for OCR

        Resolution of converted page is <= 600 dpi even for more precise page,
        as far as degree is neither 0, 90, 180 or 270.

        CAUTION: If degree is not 0, 90, 180 or 270, Page will be replaced with
        just an image.  Visible annotations are drawn as parts of image and
        cannot be handled as effective annotations any more.  Application/OCR
        text will be lost.
        """
        pos = self._pos(pos)
        abspos = self.absolute_page(pos)
        if auto:
            XDW_RotatePageAuto(self.handle, abspos + 1)
            return
        degree %= 360
        if degree == 0:
            return
        if degree in (90, 180, 270):
            XDW_RotatePage(self.handle, abspos + 1, degree)
            return
        check_PIL()
        dpi = int(max(10, min(600, max(self.page(pos).resolution))))
        if strategy == 1:
            out = in_ = self._preprocess(pos)
        elif strategy == 2:
            in_ = StringIO(self.page_image(pos).octet_stream())
            out = mktemp(suffix=".tif")
        else:
            raise ValueError("illegal strategy id " + str(strategy))
        # To rotate naturally, we need white background with sqrt(2) times
        # wide and high to the original image.
        canvas_size = int(mm2px(max(self.page(pos).size), dpi) * 1.42)
        canvas = Image.new("RGB", (canvas_size, canvas_size), "#ffffff")
        im = Image.open(in_)
        box = tuple((canvas_size - v) / 2 for v in im.size)
        box += tuple((canvas_size - v) for v in box)
        canvas.paste(im, box[:2])  # Paste on center.
        canvas.rotate(-degree).crop(box).save(out, "TIFF", resolution=dpi)
        if not isinstance(in_, basestring):
            in_.close()
        self._postprocess(pos, out)

    def view(self, light=False, wait=True):
        """View document with DocuWorks Viewer (Light)."""
        pc = PageCollection(self)
        return pc.view(combine=True, light=light, wait=wait)

    def content_text(self, type=None):
        """Get all content text.

        type    None | "IMAGE" | "APPLICATION"
                None means both.
        """
        return joinf(PSEP, [pg.content_text(type=type) for pg in self])

    def annotation_text(self):
        """Get all text in annotations."""
        return joinf(PSEP, [pg.annotation_text() for pg in self])

    def fulltext(self):
        """Get all content and annotation text."""
        return joinf(PSEP, [
                joinf(ASEP, [pg.content_text(), pg.annotation_text()])
                for pg in self])

    def find_content_text(self, pattern, type=None):
        """Find given pattern (text or regex) in all content text.

        type    None | "IMAGE" | "APPLICATION"
                None means both.
        """
        func = lambda pg: pg.content_text(type=type)
        return self.find(pattern, func=func)

    def find_annotation_text(self, pattern):
        """Find given pattern (text or regex) in all annotation text."""
        func = lambda pg: pg.annotation_text()
        return self.find(pattern, func=func)

    def find_fulltext(self, pattern):
        """Find given pattern in all content and annotation text."""
        return self.find(pattern)

    def find(self, pattern, func=None):
        """Find given pattern (text or regex) through document.

        pattern     (str/unicode or regexp supported by re module)
        func        a function which takes a page and returns text in it
                    (default) lambda pg: pg.fulltext()
        """
        func = func or (lambda pg: pg.fulltext())
        if isinstance(pattern, (str, unicode)):
            f = lambda pg: pattern in func(pg)
        else:
            f = lambda pg: pattern.search(func(pg))
        return PageCollection(filter(f, self))

    def dirname(self):
        """Abstract method for concrete dirname()."""
        raise NotImplementedError()
