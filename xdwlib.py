#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""xdwlib.py -- DocuWorks Library

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE. 
"""

from os.path import basename, splitext

from xdwapi import *


CODEPAGE = 932

try:
    VALID_DOCUMENT_HANDLES
except NameError:
    VALID_DOCUMENT_HANDLES = []
 

XDW_DOCUMENT_TYPE = {
    XDW_DT_DOCUMENT:        "DOCUMENT",
    XDW_DT_BINDER:          "BINDER",
    }
XDW_DOCUMENT_TYPE_R = dict([(v, k) for (k, v) in XDW_DOCUMENT_TYPE.items()])
def normalize_document_type(document_type):
    if isinstance(document_type, basestring):
        return XDW_DOCUMENT_TYPE_R.get(str(document_type).upper(), XDW_DT_DOCUMENT)
    return document_type


XDW_TEXT_TYPE = {
    XDW_TEXT_UNKNOWN:       "UNKNOWN",
    XDW_TEXT_MULTIBYTE:     "MULTIBYTE",
    XDW_TEXT_UNICODE:       "UNICODE",
    }
XDW_TEXT_TYPE_R = dict([(v, k) for (k, v) in XDW_TEXT_TYPE.items()])
def normalize_text_type(text_type):
    if isinstance(text_type, basestring):
        return XDW_TEXT_TYPE_R.get(str(text_type).upper, XDW_TEXT_UNICODE)
    return text_type


XDW_BINDER_COLOR = {  # 0xBBGGRR, neutral colors applied only for binders.
    XDW_BINDER_COLOR_0:     0x663300,   # neutral navy (??)
    XDW_BINDER_COLOR_1:     0x336600,   # neutral green (??)
    XDW_BINDER_COLOR_2:     0xff6633,   # neutral bule (??)
    XDW_BINDER_COLOR_3:     0x66ffff,   # neutral yellow (??)
    XDW_BINDER_COLOR_4:     0x3366ff,   # neutral orange (?I?????W)
    XDW_BINDER_COLOR_5:     0x6633ff,   # neutral red (??)
    XDW_BINDER_COLOR_6:     0xff00ff,   # fuchsia (?Ԏ?)
    XDW_BINDER_COLOR_7:     0xffccff,   # neutral pink (?s???N)
    XDW_BINDER_COLOR_8:     0xff99cc,   # neutral purple (??)
    XDW_BINDER_COLOR_9:     0x333366,   # neutral brown (??)
    XDW_BINDER_COLOR_10:    0x339999,   # neutral olive (?I???[?u)
    XDW_BINDER_COLOR_11:    0x00ff00,   # lime (????)
    XDW_BINDER_COLOR_12:    0xffff00,   # aqua (???F)
    XDW_BINDER_COLOR_13:    0xccffff,   # neutral lightyellow (?N???[??)
    XDW_BINDER_COLOR_14:    0xbbbbbb,   # neutral silver (?D?F)
    XDW_BINDER_COLOR_15:    0xffffff,   # white (??)
    }
XDW_BINDER_COLOR_R = dict([(v, k) for (k, v) in XDW_BINDER_COLOR.items()])
def normalize_binder_color(color):
    if 0x100 <= color:
        return XDW_BINDER_COLOR_R.get(color, XDW_BINDER_COLOR_5)
    return color
 

XDW_PAGE_TYPE = {
    XDW_PGT_FROMIMAGE:      "IMAGE",
    XDW_PGT_FROMAPPL:       "APPLICATION",
    XDW_PGT_NULL:           "UNKNOWN",
    }
XDW_PAGE_TYPE_R = dict([(v, k) for (k, v) in XDW_PAGE_TYPE.items()])
def normalize_page_type(page_type):
    if isinstance(page_type, basestring):
        return XDW_PAGE_TYPE_R.get(str(page_type).upper, XDW_PGT_NULL)
    return page_type


XDW_BINDER_SIZE = {
    XDW_SIZE_FREE:          "FREE",
    XDW_SIZE_A3_PORTRAIT:   "A3R",
    XDW_SIZE_A3_LANDSCAPE:  "A3",
    XDW_SIZE_A4_PORTRAIT:   "A4R",
    XDW_SIZE_A4_LANDSCAPE:  "A4",
    XDW_SIZE_A5_PORTRAIT:   "A5R",
    XDW_SIZE_A5_LANDSCAPE:  "A5",
    XDW_SIZE_B4_PORTRAIT:   "B4R",
    XDW_SIZE_B4_LANDSCAPE:  "B4",
    XDW_SIZE_B5_PORTRAIT:   "B5R",
    XDW_SIZE_B5_LANDSCAPE:  "B5",
    }
XDW_BINDER_SIZE_R = dict([(v, k) for (k, v) in XDW_BINDER_SIZE.items()])
def normalize_binder_size(size):
    if isinstance(size, basestring):
        return XDW_BINDER_SIZE_R.get(str(size).upper(), XDW_SIZE_A4_PORTRAIT)
    return size


def open(path, readonly=False, authenticate=True):
    doctype = {".XDW": XDWDocument, ".XBD": XDWBinder}[splitext(basename(path))[1].upper]
    return doctype(path, readonly=readonly, authenticate=authenticate)


def create_document_from_image(
        inputPath,
        outputPath,
        size=XDW_SIZE_A4_PORTRAIT,
        fit_image=XDW_CREATE_FIT,
        compress=XDW_COMPRESS_LOSSLESS,
        zoom=100,
        width=0, height=0,
        horizontal_position=XDW_CREATE_HCENTER,
        vertical_position=XDW_CREATE_VCENTER,
        ):
    create_option = XDW_CREATE_OPTION()
    create_option.nSize = normalize_binder_size(size)
    create_option.nFitImage = fit_image
    create_option.nCompress = compress
    create_option.nZoom = zoom
    create_option.nWidth = width
    create_option.nHeight = height
    create_option.nHorPos = horizontal_position
    create_option.nVerPos = vertical_position
    XDW_CreateXdwFromImageFile(inputPath, outputPath, create_option)


def create_binder(path, color=XDW_BINDER_COLOR_0, size=XDW_SIZE_FREE):
    XDW_CreateBinder(path, color, size)


class XDWPage(object):
    
    @staticmethod
    def normalize_resolution(n):
        if n <= 6:
            return (100, 200, 400, 200, 300, 400, 200)[n]
        return n

    def __init__(self, xdw, page):
        self.xdw = xdw
        self.page = page
        page_info = XDW_GetPageInformation(xdw.document_handle, page+1, extend=True)
        self.width = page_info.nWidth  # 1/100 mm
        self.height = page_info.nHeight  # 1/100 mm
        self.page_type = page_info.nPageType  # XDW_PGT_FROMIMAGE/FROMAPPL/NULL
        self.horizontal_resolution = XDWPage.normalize_resolution(page_info.nHorRes)  # dpi
        self.vertical_resolution = XDWPage.normalize_resolution(page_info.nVerRes)  # dpi
        self.compress_type = page_info.nCompressType
        self.annotations = page_info.nAnnotations
        self.degree = page_info.nDegree
        self.original_width = page_info.nOrgWidth  # 1/100 mm
        self.original_height = page_info.nOrgHeight  # 1/100 mm
        self.original_horizontal_resolution = XDWPage.normalize_resolution(page_info.nOrgHorRes)  # dpi
        self.original_vertical_resolution = XDWPage.normalize_resolution(page_info.nOrgVerRes)  # dpi
        self.image_width = page_info.nImageWidth  # px
        self.image_height = page_info.nImageHeight  # px

    def __getattr__(self, attr):
        if attr == "text":
            return XDW_GetPageTextToMemoryW(self.xdw.document_handle, self.page+1)
        return getattr(self.xdw, attr)

    def __str__(self):
        return "XDWPage(page %d: %.2f*%.2fmm, %s, %d annotations)" % (
                self.page,
                self.width / 100.0, self.height / 100.0,
                XDW_PAGE_TYPE[self.page_type],
                self.annotations,
                )

class XDWDocument(object):

    def register(self):
        VALID_DOCUMENT_HANDLES.append(self.document_handle)

    def free(self):
        VALID_DOCUMENT_HANDLES.remove(self.document_handle)

    def __init__(self, path, readonly=False, authenticate=True):
        open_mode = XDW_OPEN_MODE_EX()
        open_mode.nOption = XDW_OPEN_READONLY if readonly else XDW_OPEN_UPDATE
        open_mode.nAuthMode = XDW_AUTH_NODIALOGUE if authenticate else XDW_AUTH_NONE
        self.document_handle = XDW_OpenDocumentHandle(path, open_mode)
        self.register()
        self.name = splitext(basename(path))[0]
        try:
            self.name = self.name.decode("cp%d" % CODEPAGE)
        except:
            pass
        # Set document properties.
        document_info = XDW_GetDocumentInformation(self.document_handle)
        self.pages = document_info.nPages
        self.version = document_info.nVersion - 3  # DocuWorks version number
        self.original_data = document_info.nOriginalData
        self.document_type = document_info.nDocType
        self.editable = bool(document_info.nPermission & XDW_PERM_DOC_EDIT)
        self.annotatable = bool(document_info.nPermission & XDW_PERM_ANNO_EDIT)
        self.printable = bool(document_info.nPermission & XDW_PERM_PRINT)
        self.copyable = bool(document_info.nPermission & XDW_PERM_COPY)
        self.show_annotations = bool(document_info.nShowAnnotations)
        # Followings are effective only for binders.
        self.documents = document_info.nDocuments
        self.binder_color = document_info.nBinderColor
        self.binder_size = document_info.nBinderSize

    def close(self):
        XDW_CloseDocumentHandle(self.document_handle)
        self.free()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
 
    def __iter__(self):
        self.current_page = 0
        return self

    def next(self):
        if self.pages <= self.current_page:
            raise StopIteration
        page = self.current_page
        self.current_page += 1
        return XDWPage(self, page)

    def __str__(self):
        return "XDWDocument(%s: %d pages, %d files attached)" % (
                self.name,
                self.pages,
                self.documents,
                )

    def page(self, n):
        return XDWPage(self, n)

    def __len__(self):
        return self.pages

    def is_document(self):
        return True
    
    def is_binder(self):
        return False


class XDWDocumentInBinder(object):

    def __init__(self, binder, position):
        self.binder = binder 
        self.position = position
        self.start_page = sum(binder.document_pages[:position])
        self.name = XDW_GetDocumentNameInBinderW(self.binder.document_handle, position+1, CODEPAGE)[0]
        document_info = XDW_GetDocumentInformationInBinder(self.binder.document_handle, position+1)
        self.pages = document_info.nPages
        self.original_data = document_info.nOriginalData

    def __iter__(self):
        self.current_page = 0
        return self

    def next(self):
        if self.pages <= self.current_page:
            raise StopIteration
        n = self.start_page + self.current_page
        self.current_page += 1
        return XDWPage(self.binder, n)

    def __str__(self):
        return "XDWDocumentInBinder(%s, Chap.%d: %d pages, %d files attached)" % (
                self.binder.name,
                self.position + 1,
                self.pages,
                self.original_data,
                )

    def page(n):
        return XDWPage(self.binder, self.start_page + n)

    def __len__(self):
        return self.pages


class XDWBinder(XDWDocument):

    def is_document(self):
        return False
    
    def is_binder(self):
        return True

    def __init__(self, path, readonly=False, authenticate=True):
        XDWDocument.__init__(self, path=path, readonly=readonly, authenticate=authenticate)
        assert self.document_type == XDW_DT_BINDER
        self.document_pages = self.document_pages()

    def __str__(self):
        return "XDWBinder(%s: %d documents, %d pages, %d files attached)" % (
                self.name,
                self.documents,
                self.pages,
                self.original_data,
                )
    
    def document_pages(self):
        pages = []
        for pos in range(self.documents):
            docinfo = XDW_GetDocumentInformationInBinder(self.document_handle, pos+1)
            pages.append(docinfo.nPages)
        return pages

    def document(self, position):
        return XDWDocumentInBinder(self, position)

    def page(self, n):
        return XDWPage(self, n)

    def __iter__(self):
        self.current_position = 0
        return self

    def next(self):
        if self.documents <= self.current_position:
            raise StopIteration
        pos = self.current_position
        self.current_position += 1
        return  XDWDocumentInBinder(self, pos)

    def __len__(self):
        return self.documents

