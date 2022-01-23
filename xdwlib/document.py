#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix expandtab :

"""document.py -- Document

Copyright (C) 2010 HAYASHI Hideki <hideki@hayasix.com>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import os
import time

from .xdwapi import *
from .common import *
from .struct import Point
from .xdwfile import XDWFile
from .basedocument import BaseDocument


__all__ = (
        "Document",
        "create",
        "create_from_image",
        "create_from_pdf",
        "merge",
        "Container",
        )


def create(input_path=None, output_path=None, **kw):
    """The XDW generator.

    Returns the created pathname which may differ from output_path.
    """
    input_path = adjust_path(input_path)
    root, ext = os.path.splitext(input_path)
    output_path = adjust_path(output_path or root, ext=".xdw")
    if input_path:
        output_path = derivative_path(output_path)
        if ext.upper() == ".PDF":
            return create_from_pdf(input_path, output_path, **kw)
        if ext.upper() in (".BMP", ".JPG", ".JPEG", ".TIF", ".TIFF"):
            try:
                return create_from_image(input_path, output_path, **kw)
            except Exception as e:
                pass  # fall through; processed by respective apps.
        return create_from_app(input_path, output_path, **kw)
    # input_path==None means generating single blank page.
    output_path = derivative_path(adjust_path(output_path or "blank.xdw"))
    with open(output_path, "wb") as f:
        f.write(BLANKPAGE)
    return output_path


def create_from_image(input_path, output_path=None,
        fitimage="FITDEF",
        compress="NORMAL",
        zoom=0,  # %; 0=100%
        size=Point(0, 0),  # Point (in mm), int or str; 1,2..10=A3R,A3..B5
        align=("CENTER", "CENTER"),  # LEFT/CENTER/RIGHT, TOP/CENTER/BOTTOM
        maxpapersize="DEFAULT",
        ):
    """XDW generator from image file.

    fitimage        'FITDEF' | 'FIT' | 'FITDEF_DIVIDEBMP' |
                    'USERDEF' | 'USERDEF_FIT'
    compress        'NORMAL' | 'LOSSLESS' | 'NOCOMPRESS' |
                    'HIGHQUALITY' | 'HIGHCOMPRESS' |
                    'JPEG' | 'JPEG_TTN2' | 'PACKBITS' | 'G4' |
                    'MRC_NORMAL' | 'MRC_HIGHQUALITY' | 'MRC_HIGHCOMPRESS'
    zoom            (float) in percent; 0 means 100%.  < 1/1000 is ignored.
    size            (Point) in mm; for fitimange 'userdef' or 'userdef_fit'
                    (int)   1=A3R, 2=A3, 3=A4R, 4=A4, 5=A5R, 6=A5,
                            7=B4R, 8=B4, 9=B5R, 10=B5
    align           (horiz, vert) where:
                        horiz   'CENTER' | 'LEFT' | 'RIGHT'
                        vert    'CENTER' | 'TOP' | 'BOTTOM'
    maxpapersize    'DEFAULT' | 'A3' | '2A0'

    Returns the created pathname which may differ from output_path.
    """
    input_path = adjust_path(input_path)
    root, ext = os.path.splitext(input_path)
    output_path = adjust_path(output_path or root, ext=".xdw")
    output_path = derivative_path(output_path)
    opt = XDW_CREATE_OPTION_EX2()
    opt.nFitImage = XDW_CREATE_FITIMAGE.normalize(fitimage)
    opt.nCompress = XDW_COMPRESS.normalize(compress)
    #opt.nZoom = int(zoom)
    opt.nZoomDetail = int(zoom * 1000)  # .3f
    # NB. Width and height are valid only for XDW_CREATE_USERDEF(_FIT).
    if not isinstance(size, Point):
        size = XDW_SIZE.normalize(size)
        size = XDW_SIZE_MM[size or 3]  # default=A4R
        size = Point(*size)
    opt.nWidth = int(size.x * 100)  # .2f
    opt.nHeight = int(size.y * 100)  # .2f;
    opt.nHorPos = XDW_CREATE_HPOS.normalize(align[0])
    opt.nVerPos = XDW_CREATE_VPOS.normalize(align[1])
    opt.nMaxPaperSize = XDW_CREATE_MAXPAPERSIZE.normalize(maxpapersize)
    if XDWVER < 8:
        XDW_CreateXdwFromImageFile(cp(input_path), cp(output_path), opt)
    else:
        XDW_CreateXdwFromImageFileW(input_path, output_path, opt)
    return output_path


def create_from_pdf(input_path, output_path=None):
    """XDW generator from image PDF file.

    Returns the created pathname which may differ from output_path.
    """
    input_path = adjust_path(input_path)
    root, ext = os.path.splitext(input_path)
    output_path = adjust_path(output_path or root, ext=".xdw")
    output_path = derivative_path(output_path)
    try:
        XDW_CreateXdwFromImagePdfFile(cp(input_path), cp(output_path))
    except Exception as e:
        # If PDF is not compatible with DocuWorks, try to handle it
        # with the system-defined application program.
        create_from_app(input_path, output_path, timeout=3600)
    return output_path


def create_from_app(input_path, output_path=None,
        attachment=False, timeout=0):
    """Create document through other app with optional attachment.

    attachment  (bool) attach original data file (given by input_path) or not
    timeout     (int) max seconds to wait until application printing is done

    Returns the created pathname which may differ from output_path.
    """
    input_path = adjust_path(input_path)
    root, ext = os.path.splitext(input_path)
    output_path = adjust_path(output_path or root, ext=".xdw")
    output_path = derivative_path(output_path)
    if XDWVER < 8:
        handle = XDW_BeginCreationFromAppFile(
                cp(input_path), cp(output_path), bool(attachment))
    else:
        handle = XDW_BeginCreationFromAppFileW(
                input_path, output_path, bool(attachment))
    st = time.time()
    try:
        while True:
            status = XDW_GetStatusCreationFromAppFile(handle)
            if status.phase in (XDW_CRTP_FINISHED,
                    XDW_CRTP_CANCELED, XDW_CRTP_CANCELING):
                break
            if timeout and timeout < time.time() - st:
                XDW_CancelCreationFromAppFile(handle)
                break
            time.sleep(2)
        # status.phase, status.nTotalPage, status.nPage
    finally:
        XDW_EndCreationFromAppFile(handle)
    return output_path


def merge(input_paths, output_path=None):
    """Merge XDW's into a new XDW.

    Returns the created pathname which may differ from output_path.
    """
    input_paths = [adjust_path(path) for path in input_paths]
    root, ext = os.path.splitext(input_paths[0])
    output_path = adjust_path(output_path or root, ext=".xdw")
    output_path = derivative_path(output_path)
    if XDWVER < 8:
        XDW_MergeXdwFiles([cp(path) for path in input_paths], cp(output_path))
    else:
        XDW_MergeXdwFilesW(input_paths, output_path)
    return output_path


class Document(BaseDocument, XDWFile):

    """DocuWorks document (XDW)."""

    def __init__(self, path):
        BaseDocument.__init__(self)
        XDWFile.__init__(self, path)

    def __repr__(self):
        return "{cls}({name}{sts})".format(
                cls=self.__class__.__name__,
                name=self.name,
                sts="" if self.handle else "; CLOSED")

    def __str__(self):
        return "{cls}({name}; {pgs} pages, {atts} attachments{sts})".format(
                cls=self.__class__.__name__,
                name=self.name,
                pgs=self.pages,
                atts=len(self.attachments),
                sts="" if self.handle else "; CLOSED")

    def absolute_page(self, pos, append=False):
        """Concrete method over absolute_page()."""
        pos = self._pos(pos, append=append)
        return pos

    def update_pages(self):
        """Concrete method over update_pages()."""
        XDWFile.update_pages(self)

    def dirname(self):
        """Concrete method over dirname()."""
        return self.dir


class Container(Document):

    """DocuWorks container (XCT).

    Container is a Document with only 1 page, and with attachments.
    """

    def append(self, obj):
        raise InvalidOperationError

    def insert(self, obj):
        raise InvalidOperationError

    def append_image(self, *args, **kw):
        raise InvalidOperationError

    def insert_image(self, *args, **kw):
        raise InvalidOperationError

    def export(self, pos, path=None):
        raise InvalidOperationError

    def delete(self, pos):
        raise InvalidOperationError

    def rasterize(self, pos, direct=False):
        raise InvalidOperationError

    def rotate(self, pos, degree=0, auto=False, direct=False):
        """Rotate page around the center.

        pos     0; required for compatibility
        degree  0 | 90 | 180 | 270; rotation angle in clockwise degree
        auto    ignored, only for compatibility
        direct  ignored, only for compatibility
        """
        if pos != 0:
            raise InvalidOperationError("only 0 is allowed")
        if (not auto) or direct:
            raise InvalidOperationError(
                    "only 0, 90, 180 or 270 degree is allowed")
        if (degree % 360) not in (0, 90, 180, 270):
            raise InvalidOperationError(
                    "only 0, 90, 180 or 270 degree is allowed")
        super().rotate(pos, degree=degree)

    def view(self, light=False, wait=True, page=0, fullscreen=False, zoom=0):
        raise InvalidOperationError
