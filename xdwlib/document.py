#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""document.py -- DocuWorks library for Python.

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
from struct import Point
from xdwfile import XDWFile
from basedocument import BaseDocument


__all__ = ("Document",
        "create",
        "create_from_image",
        "create_from_pdf",
        "merge",
        )


def create(input_path=None, output_path=None, **kw):
    """The XDW generator."""
    output_path = cp(output_path)
    if isinstance(input_path, basestring):
        input_path = cp(input_path)
        root, ext = os.path.splitext(input_path)[1].lstrip(".").upper()
        if not output_path:
            output_path = root + ".xdw"
        if ext in ("PDF",):
            create_from_pdf(input_path, output_path)  # no fallthru
            return output_path
        if ext in ("BMP", "JPG", "JPEG", "TIF", "TIFF"):
            try:
                create_from_image(input_path, output_path, **kw)
                return output_path
            except Exception as e:
                pass  # fall through; processed by respective apps.
        create_from_app(input_path, output_path)
        return output_path
    # input_path==None means generating single blank page.
    with open(output_path, "wb") as f:
        f.write(BLANKPAGE)
    return output_path


def create_from_image(input_path, output_path=None,
        fitimage=XDW_CREATE_FITDEF,
        compress=XDW_COMPRESS_NORMAL,
        zoom=0,  # %; 0=100%
        size=Point(0, 0),  # Point (in mm), int or str; 1,2..10=A3R,A3..B5
        align=("center", "center"),  # left/center/right, top/center/bottom
        maxpapersize=XDW_CREATE_DEFAULT_SIZE,
        ):
    """XDW generator from image file.

    size: (Point/str/int) valid if fitimage in ("userdef", "userdef_fit")
          1=A3R, 2=A3, 3=A4R, 4=A4, 5=A5R, 6=A5, 7=B4R, 8=B4, 9=B5R, 10=B5
    """
    input_path, output_path = cp(input_path), cp(output_path)
    root, ext = os.path.split(input_path)
    if not output_path:
        output_path = root + ".xdw"
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
    XDW_CreateXdwFromImageFile(input_path, output_path, opt)
    return output_path


def create_from_pdf(input_path, output_path=None):
    """XDW generator from image PDF file."""
    input_path, output_path = cp(input_path), cp(output_path)
    root, ext = os.path.split(input_path)
    if not output_path:
        output_path = root + ".xdw"
    try:
        XDW_CreateXdwFromImagePdfFile(input_path, output_path)
    except Exception as e:
        create_from_app(input_path, output_path, timeout=3600)
    return output_path


def create_from_app(input_path, output_path=None,
        attachment=False, timeout=0):
    """Create document through other app with optional attachment.

    create_from_app(input_path, output_path=None,
            attachment=False, timeout=0) --> generated_pages or None

    attachment: (bool) attach original data file (given by input_path) or not
    timeout: (int) max seconds to wait until application printing is done
    """
    import time
    input_path, output_path = cp(input_path), cp(output_path)
    root, ext = os.path.split(input_path)
    if not output_path:
        output_path = root + ".xdw"
    handle = XDW_BeginCreationFromAppFile(
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
    return status.nTotalPage if status.phase == XDW_CRTP_FINISHED else None


def merge(input_paths, output_path=None):
    """Merge XDW's into a new XDW.

    Returns pathname of merged document file.
    """
    input_paths = [cp(path) for path in input_paths]
    if output_path:
        root, ext = os.path.splitext(output_path)
    else:
        root, ext = os.path.splitext(input_paths[0])
        root += "-Merged"
        output_path = root + ext
    n = 1  # not 0
    while n < 100:
        if not os.path.exists(output_path):
            break
        n += 1
        output_path = "%s-%d%s" % (root, n, ext)
    else:
        raise FileExistsError()
    XDW_MergeXdwFiles(input_paths, output_path)
    return output_path


class Document(BaseDocument, XDWFile):

    """DocuWorks document (XDW)."""

    __type__ = "DOCUMENT"

    def __init__(self, path, readonly=False, authenticate=True):
        BaseDocument.__init__(self)
        XDWFile.__init__(self, path,
                readonly=readonly, authenticate=authenticate)

    def __repr__(self):
        return u"Document(%s)" % self.name

    def __str__(self):
        return u"Document(%s: %d pages, %d attachments)" % (
                self.name, self.pages, self.original_data)

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
