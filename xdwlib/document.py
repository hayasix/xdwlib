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

from os.path import abspath, dirname, join

from xdwapi import *
from common import *
from struct import Point
from xdwfile import XDWFile
from basedocument import BaseDocument


__all__ = ("Document",
        "create_document",
        "create_document_from_image",
        "create_document_from_pdf",
        )


def create_document(path, source=None, **kw):
    """The XDW generator."""
    if isinstance(source, basestring):
        if source.upper().endswith(".PDF"):
            return create_document_from_pdf(source, path)
        elif source.upper().endswith((".BMP", "JPG", "JPEG", "TIF", "TIFF")):
            return create_document_from_image(source, path, **kw)
    with open(path, "wb") as f:
        f.write(BLANKPAGE)
    return path


def create_document_from_image(input_path, output_path=None,
        fitimage=XDW_CREATE_FITDEF,
        compress=XDW_COMPRESS_NORMAL,
        zoom=0,  # %; 0=100%
        size=Point(0, 0),  # Point(width, height); 0=A4R
        align=("center", "center"),  # left/center/right, top/center/bottom
        maxpapersize=XDW_CREATE_DEFAULT_SIZE,
        ):
    """XDW generator from image file."""
    if not output_path:
        output_path = input_path + ".xdw"
    opt = XDW_CREATE_OPTION_EX2()
    opt.nFitImage = XDW_CREATE_FITIMAGE.normalize(fitimage)
    opt.nCompress = XDW_COMPRESS.normalize(compress)
    #opt.nZoom = int(zoom)
    opt.nZoomDetail = int(zoom * 1000)  # .3f
    # NB. Width and height are valid only for XDW_CREATE_USERDEF(_FIT).
    opt.nWidth, opt.nHeight = int(size * 100)  # .2f;
    opt.nHorPos = XDW_CREATE_HPOS.normalize(align[0])
    opt.nVerPos = XDW_CREATE_VPOS.normalize(align[1])
    opt.nMaxPaperSize = XDW_CREATE_MAXPAPERSIZE.normalize(maxpapersize)
    XDW_CreateXdwFromImageFile(input_path, output_path, opt)
    return output_path


def create_document_from_pdf(input_path, output_path):
    """XDW generator from image PDF file."""
    if not output_path:
        output_path = input_path + ".xdw"
    XDW_CreateXdwFromImagePdfFile(input_path, output_path)
    return output_path


class Document(BaseDocument, XDWFile):

    """DocuWorks document (XDW)."""

    def __init__(self, path, readonly=False, authenticate=True):
        BaseDocument.__init__(self)
        XDWFile.__init__(self, path,
                readonly=readonly, authenticate=authenticate)
        assert self.type == XDW_DT_DOCUMENT

    def __repr__(self):
        return u"Document(%s)" % self.name

    def __str__(self):
        return u"Document(%s: %d pages, %d attachments)" % (
                self.name, self.pages, self.original_data)

    def absolute_page(self, pos):
        """Concrete method over absolute_page()."""
        return pos

    def dirname(self):
        """Concrete method over dirname()."""
        return self.dir
