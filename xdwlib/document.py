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
from shutil import copyfile

from common import *
from xdwfile import XDWFile
from basedocument import BaseDocument


__all__ = ("Document", "create_document", "create_document_from_image")


def create_document(path):
    """The XDW generator, preparing dummy A4 white page."""
    blank = join(dirname(abspath(__file__)), "__blank__.xdw")
    copyfile(blank, path)


def create_document_from_image(
        inputPath,
        outputPath,
        size=XDW_SIZE_A4_PORTRAIT,
        fit_image=XDW_CREATE_FIT,
        compress=XDW_COMPRESS_LOSSLESS,
        zoom=100,
        width=0.0, height=0.0,
        horizontal_position=XDW_CREATE_HCENTER,
        vertical_position=XDW_CREATE_VCENTER,
        ):
    """XDW generator from image file."""
    opt = XDW_CREATE_OPTION()
    opt.nSize = normalize_binder_size(size)
    opt.nFitImage = fit_image
    opt.nCompress = compress
    opt.nZoom = int(zoom)
    opt.nWidth = int(width * 100)
    opt.nHeight = int(height * 100)
    opt.nHorPos = int(horizontal_position * 100)
    opt.nVerPos = int(vertical_position * 100)
    XDW_CreateXdwFromImageFile(inputPath, outputPath, opt)


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

    def require_finalization(self):
        """Set `finalize' flag to invoke finalization process on exit."""
        self.finalize = True

    def absolute_page(self, pos):
        """Concrete method over absolute_page()."""
        return pos

    def dirname(self):
        """Concrete method over dirname()."""
        return self.dir
