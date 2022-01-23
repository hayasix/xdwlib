#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix expandtab :

"""basedocument.py -- BaseDocument, base class for Document/DocumentInBinder

Copyright (C) 2010 HAYASHI Hideki <hideki@hayasix.com>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import sys
import os
from io import StringIO

from .xdwapi import *
from .common import *
from .xdwtemp import XDWTemp
from .observer import *
from .struct import Point
from .xdwfile import xdwopen
from .page import Page, PageCollection


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
            deleted = 0
            for p in range(pos.start, pos.stop, pos.step):
                self.delete(p - deleted)
                deleted += 1
        else:
            self.delete(pos)

    def __iter__(self):
        for pos in range(self.pages):
            yield self.page(pos)

    def absolute_page(self, pos, append=False):
        """Abstract method to get absolute page number in binder/document."""
        raise NotImplementedError()

    def update_pages(self):
        """Abstract method to update number of pages."""
        raise NotImplementedError()

    def page(self, pos):
        """Get a Page.

        pos     (int) page number; starts with 0

        Returns a Page object.
        """
        pos = self._pos(pos)
        if pos not in self.observers:
            self.observers[pos] = Page(self, pos)
        return self.observers[pos]

    def append(self, obj):
        """Append a Page/PageCollection/Document at the end of document.

        obj     (Page, PageCollection or Document)
        """
        self.insert(self.pages, obj)

    def insert(self, pos, obj):
        """Insert a Page/PageCollection/Document.

        pos     (int) position to insert; starts with 0
        obj     (Page, PageCollection, BaseDocument or str)
        """
        pos = self._pos(pos, append=True)
        if isinstance(obj, Page):
            temp = XDWTemp()
            obj.export(temp.path)
        elif isinstance(obj, PageCollection):
            temp = XDWTemp()
            obj.export(temp.path, flat=True)
        elif isinstance(obj, BaseDocument):
            temp = XDWTemp()
            pc = PageCollection(obj)
            pc.export(temp.path, flat=True)
        elif isinstance(obj, str):  # XDW path
            temp = obj
            if not temp.lower().endswith(".xdw"):
                raise TypeError("binder is not acceptable")
        else:
            raise ValueError(f"can't insert {obj.__class__} object")
        if XDWVER < 8:
            XDW_InsertDocument(
                    self.handle,
                    self.absolute_page(pos, append=True) + 1,
                    cp(temp if isinstance(temp, str) else temp.path))
        else:
            XDW_InsertDocumentW(
                    self.handle,
                    self.absolute_page(pos, append=True) + 1,
                    temp if isinstance(temp, str) else temp.path)
        inslen = XDW_GetDocumentInformation(self.handle).nPages - self.pages
        self.pages += inslen
        if not isinstance(obj, str):
            temp.close()
        # Check inserted pages in order to attach them to this document and
        # shift observer entries appropriately.
        for p in range(pos, pos + inslen):
            Page(self, p)

    def append_image(self, *args, **kw):
        """Append a page created from image file(s).

        See insert_image() for description on arguments.
        """
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

        fitimage        'FITDEF' | 'FIT' | 'FITDEF_DIVIDEBMP' |
                        'USERDEF' | 'USERDEF_FIT'
        compress        'NORMAL' | 'LOSSLESS' |
                        'HIGHQUALITY' | 'HIGHCOMPRESS' |
                        'MRC_NORMAL' | 'MRC_HIGHQUALITY' | 'MRC_HIGHCOMPRESS'
        zoom            (float) in percent; 0 means 100%.  < 1/1000 is ignored.
        size            (Point) in mm; for fitimange 'userdef' or 'userdef_fit'
                        (int)   1=A3R, 2=A3, 3=A4R, 4=A4, 5=A5R, 6=A5,
                                7=B4R, 8=B4, 9=B5R, 10=B5
                        (str) 'A3R' | 'A3' | 'A4R' | 'A4' | 'A5R' |
                                'A5' | 'B4R' | 'B4' | 'B5R' | 'B5'
        align           (horiz, vert) where:
                            horiz   'CENTER' | 'LEFT' | 'RIGHT'
                            vert    'CENTER' | 'TOP' | 'BOTTOM'
        maxpapersize    'DEFAULT' | 'A3' | '2A0'
        """
        prev_pages = self.pages
        pos = self._pos(pos, append=True)
        opt = XDW_CREATE_OPTION_EX2()
        opt.nFitImage = XDW_CREATE_FITIMAGE.normalize(fitimage)
        opt.nCompress = XDW_COMPRESS.normalize(compress)
        if opt.nCompress in (
                XDW_COMPRESS_NOCOMPRESS,
                XDW_COMPRESS_JPEG,
                XDW_COMPRESS_PACKBITS,
                XDW_COMPRESS_G4,
                XDW_COMPRESS_MRC,
                XDW_COMPRESS_JPEG_TTN2,
                ):
            raise ValueError("invalid compression method `{0}'".format(
                    XDW_COMPRESS[opt.nCompress]))
        #opt.nZoom = 0
        opt.nZoomDetail = int(zoom * 1000)  # .3f
        # NB. Width and height are valid only for XDW_CREATE_USERDEF(_FIT).
        if isinstance(size, (int, float, str)):
            size = Point(*XDW_SIZE_MM[XDW_SIZE.normalize(size)])
        opt.nWidth, opt.nHeight = list(map(int, size * 100))  # .2f;
        opt.nHorPos = XDW_CREATE_HPOS.normalize(align[0])
        opt.nVerPos = XDW_CREATE_VPOS.normalize(align[1])
        opt.nMaxPaperSize = XDW_CREATE_MAXPAPERSIZE.normalize(maxpapersize)
        if XDWVER < 8:
            XDW_CreateXdwFromImageFileAndInsertDocument(
                    self.handle,
                    self.absolute_page(pos, append=True) + 1,
                    cp(input_path),
                    opt)
        else:
            XDW_CreateXdwFromImageFileAndInsertDocumentW(
                    self.handle,
                    self.absolute_page(pos, append=True) + 1,
                    input_path,
                    opt)
        self.update_pages()
        # Check inserted pages in order to attach them to this document and
        # shift observer entries appropriately.
        for p in range(pos, pos + (self.pages - prev_pages)):
            Page(self, p)

    def export(self, pos, path=None):
        """Export page to another document.

        pos     (int) page number; starts with 0
        path    (str) export to {path};
                      with no dir, export to {document/binder dir}/{path}
                (None) export to
                      {document/binder dir}/{document name}_P{num}.xdw

        Returns the exported pathname which may differ from path.
        """
        path = newpath(path or f"{self.name}_P{pos + 1}.xdw", dir=self.dirname())
        if XDWVER < 8:
            XDW_GetPage(self.handle, self.absolute_page(pos) + 1, cp(path))
        else:
            XDW_GetPageW(self.handle, self.absolute_page(pos) + 1, path)
        return path

    def export_image(self, pos, path=None,
            pages=1, dpi=600, color="COLOR", format=None, compress="NORMAL",
            direct=False):
        """Export page(s) to image file.

        pos         (int or tuple (start stop) in half-open style like slice)
        path        (str) export to {path};
                          with no dir, export to {document/binder dir}/{path}
                    (None) export to
                          {document/binder dir}/{document name}_P{num}.bmp
        pages       (int)
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
                      - pos must be int; pages, dpi, color, format and
                        compress are ignored.
                      - Exported image format is recognized with the
                        extension of returned pathname, which is either
                        'tiff', 'jpeg' or 'pdf'.
                      - Annotations and page forms are not included in
                        the exported image.  Image orientation depends
                        on the internal state, so check 'degree' attribute
                        of the page if needed.

        Returns the exported pathname which may differ from path.
        """
        if direct:
            return self._export_direct_image(pos, path)
        if isinstance(pos, (list, tuple)):
            pos, pages = pos
            pages -= pos
        pos = self._pos(pos)
        if not format:
            ext = os.path.splitext(path or "_.bmp")[1].lstrip(".").lower()
            format = {"dib": "bmp", "tif": "tiff", "jpg": "jpeg"}.get(ext, ext)
        if format.lower() not in ("bmp", "tiff", "jpeg", "pdf"):
            raise TypeError("image type must be BMP, TIFF, JPEG or PDF.")
        path = newpath(path or (
                       f"{self.name}_P{pos + 1}.{format}" if pages == 1 else
                       f"{self.name}_P{pos + 1}-{pos + pages}.{format}"),
                       dir=self.dirname())
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
        if XDWVER < 8:
            XDW_ConvertPageToImageFile(
                    self.handle, self.absolute_page(pos) + 1, cp(path), opt)
        else:
            XDW_ConvertPageToImageFileW(
                    self.handle, self.absolute_page(pos) + 1, path, opt)
        return path

    def _export_direct_image(self, pos, path=None):
        pos = self._pos(pos)
        path = newpath(path or f"{self.name}_P{pos + 1}", dir=self.dirname())
        path, _ = os.path.splitext(path)
        if XDWVER < 8:
            fmt = XDW_GetCompressedPageImage(
                    self.handle, self.absolute_page(pos) + 1, cp(path))
        else:
            fmt = XDW_GetCompressedPageImageW(
                    self.handle, self.absolute_page(pos) + 1, path)
        new_path = path + "." + XDW_IMAGE_FORMAT[fmt].lower()
        os.rename(path, new_path)
        return new_path

    def bitmap(self, pos):
        """Get page image with annotations as a Bitmap object.

        pos     (int) page number; starts with 0
        """
        return self.page(pos).bitmap()

    def delete(self, pos):
        """Delete a page.

        pos     (int) page number; starts with 0
        """
        pos = self._pos(pos)
        pg = self.page(pos)
        XDW_DeletePage(self.handle, self.absolute_page(pos) + 1)
        self.detach(pg, EV_PAGE_REMOVED)
        self.pages -= 1

    def _preprocess(self, pos, direct=False):
        pg = self.page(pos)
        dpi = int(max(pg.resolution))
        dpi = max(10, min(600, dpi))  # Force 10 <= dpi <= 600.
        color = pg.color_scheme()
        temp = XDWTemp(suffix=".tif")
        temp.path = self.export_image(pos, temp.path,
                dpi=dpi, color=color, format="tiff", compress="nocompress",
                direct=direct)
        return (temp, pg.degree if direct else 0)

    def _postprocess(self, pos, temp, degree=0):
        self.insert_image(pos, temp.path)  # Insert image page.
        if degree:
            self.rotate(pos, degree=degree)
        self.page(pos).reset_attr()
        self.delete(pos + 1)  # Delete original application page.
        temp.close()

    def rasterize(self, pos, direct=False):
        """Rasterize; convert an application page into DocuWorks image page.

        pos     (int) page number; starts with 0
        """
        pos = self._pos(pos)
        if self.page(pos).type != "APPLICATION":
            return
        temp, degree = self._preprocess(pos, direct=direct)
        self._postprocess(pos, temp, degree)
        self.page(pos).reset_attr()

    def rotate(self, pos, degree=0, auto=False, direct=False, strategy=1):
        """Rotate page around the center.

        pos     (int) page number; starts with 0
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
        # Angle other than 90, 180 or 270 requires some imaging library.
        if not PIL_ENABLED:
            raise NotImplementedError("missing PIL (Python Imaging Library)")
        dpi = int(max(10, min(600, max(self.page(pos).resolution))))
        if strategy == 1:
            out, orig_degree = self._preprocess(pos, direct=direct)
            in_ = out.path
        elif strategy == 2:
            in_ = StringIO(self.bitmap(pos).octet_stream())
            orig_degree = 0
            out = XDWTemp(suffix=".tif")
        else:
            raise ValueError("illegal strategy id " + str(strategy))
        # To rotate naturally, we need white background with sqrt(2) times
        # wide and high to the original image.
        canvas_size = int(mm2px(max(self.page(pos).size), dpi) * 1.42)
        canvas = Image.new("RGB", (canvas_size, canvas_size), "#ffffff")
        if strategy == 1:
            with open(in_, "rb") as f:
                im = Image.open(f)
                im.load()
        else:
            im = Image.open(in_)
        box = tuple(round((canvas_size - v) / 2) for v in im.size)
        box += tuple((canvas_size - v) for v in box)
        while True:  # Quick hack for PIL lazy reading from file.
            try:
                canvas.paste(im, box[:2])  # Paste on center.
            except IOError:
                continue
            break
        canvas.rotate(-degree).crop(box).save(out.path, "TIFF", resolution=dpi)
        if strategy == 2:
            in_.close()
        self._postprocess(pos, out, orig_degree)

    def view(self, light=False, wait=True, page=0, fullscreen=False, zoom=0):
        """View document with DocuWorks Viewer (Light).

        light       (bool) force to use DocuWorks Viewer Light.
                    Note that DocuWorks Viewer is used if Light version is
                    not avaiable.
        wait        (bool) wait until viewer stops and get annotation info
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
        pc = PageCollection(self)
        return pc.view(light=light, wait=wait, flat=True,
                        page=page, fullscreen=fullscreen, zoom=zoom)

    def content_text(self, type=None):
        """Get all content text.

        type    None | 'IMAGE' | 'APPLICATION'
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

        pattern     (str or regexp supported by re module)
        type        None | 'IMAGE' | 'APPLICATION'
                    None means both.

        Returns a PageCollection object.
        """
        func = lambda pg: pg.content_text(type=type)
        return self.find(pattern, func=func)

    def find_annotation_text(self, pattern):
        """Find given pattern (text or regex) in all annotation text.

        pattern     (str or regexp supported by re module)

        Returns a PageCollection object.
        """
        func = lambda pg: pg.annotation_text()
        return self.find(pattern, func=func)

    def find_fulltext(self, pattern):
        """Find given pattern in all content and annotation text.

        pattern     (str or regexp supported by re module)

        Returns a PageCollection object."""
        return self.find(pattern)

    def find(self, pattern, func=None):
        """Find given pattern (text or regex) through document.

        pattern     (str or regexp supported by re module)
        func        a function which takes a page and returns text in it
                    (default) lambda pg: pg.fulltext()

        Returns a PageCollection object.
        """
        func = func or (lambda pg: pg.fulltext())
        if isinstance(pattern, str):
            f = lambda pg: pattern in func(pg)
        else:
            f = lambda pg: pattern.search(func(pg))
        return PageCollection(filter(f, self))

    def dirname(self):
        """Abstract method for concrete dirname()."""
        raise NotImplementedError()
