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
 

class XDWConstants(object):

    """DocuWorks constant (internal ID) table with reverse lookup"""

    def __init__(self, constants, default=None):
        self.constants = constants
        self.reverse = dict([(v, k) for (k, v) in constants.items()])
        self.default = default

    def __getitem__(self, key):
        return self.constants[key]  # Invalid key should raise exception.

    def inner(self, value):
        return self.reverse.get(value, self.default)
 
    def normalize(self, key_or_value):
        if isinstance(key_or_value, basestring):
            return self.reverse.get(str(key_or_value).upper(), self.default)
        return key_or_value


XDW_DOCUMENT_TYPE = XDWConstants({
        XDW_DT_DOCUMENT:        "DOCUMENT",
        XDW_DT_BINDER:          "BINDER",
        }, default=XDW_DT_DOCUMENT)
XDW_TEXT_TYPE = XDWConstants({
        XDW_TEXT_UNKNOWN:       "UNKNOWN",
        XDW_TEXT_MULTIBYTE:     "MULTIBYTE",
        XDW_TEXT_UNICODE:       "UNICODE",
        }, default=XDW_TEXT_UNKNOWN)
XDW_PAGE_TYPE = XDWConstants({
        XDW_PGT_FROMIMAGE:      "IMAGE",
        XDW_PGT_FROMAPPL:       "APPLICATION",
        XDW_PGT_NULL:           "UNKNOWN",
        }, default=XDW_PGT_NULL)
XDW_BINDER_SIZE = XDWConstants({
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
        }, default=XDW_SIZE_FREE)
XDW_BINDER_COLOR = XDWConstants({
        # Here we describe colors in RRGGBB format, though DocuWorks
        # inner color representation is BBGGRR.
        XDW_BINDER_COLOR_0:     "003366",   # neutral navy (紺)
        XDW_BINDER_COLOR_1:     "006633",   # neutral green (緑)
        XDW_BINDER_COLOR_2:     "3366FF",   # neutral bule (青)
        XDW_BINDER_COLOR_3:     "FFFF66",   # neutral yellow (黄)
        XDW_BINDER_COLOR_4:     "FF6633",   # neutral orange (オレンジ)
        XDW_BINDER_COLOR_5:     "FF3366",   # neutral red (赤)
        XDW_BINDER_COLOR_6:     "FF00FF",   # fuchsia (赤紫)
        XDW_BINDER_COLOR_7:     "FFCCFF",   # neutral pink (ピンク)
        XDW_BINDER_COLOR_8:     "CC99FF",   # neutral purple (紫)
        XDW_BINDER_COLOR_9:     "663333",   # neutral brown (茶)
        XDW_BINDER_COLOR_10:    "999933",   # neutral olive (オリーブ)
        XDW_BINDER_COLOR_11:    "00FF00",   # lime (緑)
        XDW_BINDER_COLOR_12:    "00FFFF",   # aqua (水色)
        XDW_BINDER_COLOR_13:    "FFFFCC",   # neutral lightyellow (クリーム)
        XDW_BINDER_COLOR_14:    "BBBBBB",   # neutral silver (灰色)
        XDW_BINDER_COLOR_15:    "FFFFFF",   # white (白)
        }, default=XDW_BINDER_COLOR_5)
XDW_ANNOTATION_TYPE = XDWConstants({
        XDW_AID_FUSEN:          "FUSEN",
        XDW_AID_TEXT:           "TEXT",
        XDW_AID_STAMP:          "STAMP",
        XDW_AID_STRAIGHTLINE:   "STRAIGHTLINE",
        XDW_AID_RECTANGLE:      "RECTANGLE",
        XDW_AID_ARC:            "ARC",
        XDW_AID_POLYGON:        "POLYGON",
        XDW_AID_MARKER:         "MARKER",
        XDW_AID_LINK:           "LINK",
        XDW_AID_PAGEFORM:       "PAGEFORM",
        XDW_AID_OLE:            "OLE",
        XDW_AID_BITMAP:         "BITMAP",
        XDW_AID_RECEIVEDSTAMP:  "RECEIVEDSTAMP",
        XDW_AID_CUSTOM:         "CUSTOM",
        XDW_AID_TITLE:          "TITLE",
        XDW_AID_GROUP:          "GROUP",
        }, default=XDW_AID_TEXT)
 

def open(path, readonly=False, authenticate=True):
    """General opener"""
    doctype = {".XDW": XDWDocument, ".XBD": XDWBinder}[splitext(basename(path))[1].upper()]
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
    """A XDW generator"""
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
    """The XBD generator"""
    XDW_CreateBinder(path, color, size)


class XDWAnnotation(object):

    """An annotation on DocuWorks document page"""

    def __init__(self, page, index, parent_annotation=None):
        self.page = page
        self.parent_annotation = parent_annotation
        self.index = index
        pah = parent_annotation and parent_annotation.annotation_handle or None
        # TODO:BEGIN
        # Next line raises "WindowsError: exception: access violation reading 0xFFFFFFFF". Why???
        #info = XDW_GetAnnotationInformation(page.xdw.document_handle, page.page+1, pah, index+1)
        info = XDW_ANNOTATION_INFO()
        TRY(DLL.XDW_GetAnnotationInformation, page.xdw.document_handle, page.page+1, pah, index+1, byref(info), NULL)
        # TODO:END
        self.annotation_handle = info.handle
        self.horizontal_position = info.nHorPos
        self.vertical_position = info.nVerPos
        self.width = info.nWidth
        self.height = info.nHeight
        self.annotation_type = info.nAnnotationType
        self.child_annotations = info.nChildAnnotations

    def __str__(self):
        return "XDWAnnotation(%s P%d: type=%s)" % (
                self.page.xdw.name,
                self.page.page,
                XDW_ANNOTATION_TYPE[self.annotation_type],
                )

    def __getattr__(self, attr):
        if attr == "text":
            at = self.annotation_type
            ah = self.annotation_handle
            ga = XDW_GetAnnotationAttributeW
            if at == XDW_AID_STAMP:
                text = "%s <DATE> %s" % (
                        ga(ah, XDW_ATN_TopField, CODEPAGE)[0],
                        ga(ah, XDW_ATN_BottomField, CODEPAGE)[0],
                        )
            elif at == XDW_AID_TEXT:
                text = ga(ah, XDW_ATN_Text, CODEPAGE)[0]
            elif at == XDW_AID_LINK:
                text = ga(ah, XDW_ATN_Caption, CODEPAGE)[0]
            else:
                text = None
            text = [text]
            if self.child_annotations:
                text.extend([self.annotation(i).text \
                    for i in range(self.child_annotations)])
            return "\v".join([t for t in text if isinstance(t, basestring)])
        elif attr == "annotations":
            return self.child_annotations
        return getattr(self.page, attr)  # escalate

    def annotation(self, index):
        if self.child_annotations <= index:
            if self.child_annotations < 1:
                raise ValueError("No annotation available")
            else:
                raise ValueError(
                        "Illegal annotation index %d not in 0..%d" % (
                        index, self.child_annotations-1))
        return XDWAnnotation(self.page, index, parent_annotation=self)

    # TODO: implement collect_annotations() as well as XDWPage class.


class XDWPage(object):

    """A page of DocuWorks document"""
    
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
        if attr == "annotation_text":
            return "\r".join([ann.text for ann in self.collect_annotations() if ann.text])
        return getattr(self.xdw, attr)  # escalate

    def __str__(self):
        return "XDWPage(page %d: %.2f*%.2fmm, %s, %d annotations)" % (
                self.page,
                self.width / 100.0, self.height / 100.0,
                XDW_PAGE_TYPE[self.page_type],
                self.annotations,
                )

    def annotation(self, n):
        """annotation(n) --> XDWAnnotation"""
        return XDWAnnotation(self, n)
        
    def collect_annotations(self, rect=None, types=None, half_open=True):
        if rect and not half_open:
            self.right += 1
            self.bottom += 1
        if types:
            if not isinstance(types, (list, tuple)):
                types = [types]
            types = [XDW_ANNOTATION_TYPE.normalize(t) for t in types]
        annlist = []
        for i in range(self.annotations):
            ann = self.annotation(i)
            if rect and not (
                    rect.left <= ann.horizontal_position and
                    ann.horizontal_position + ann.width - 1 < rect.right and
                    rect.top <= ann.vertical_position and
                    ann.vertical_position + ann.height - 1 < rect.bottom):
                continue
            if types and not ann.annotation_type in types:
                continue
            annlist.append(ann)
        return annlist


class XDWDocument(object):

    """A DocuWorks document"""

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

    def __getattr__(self, attr):
        if attr == "text":
            return "\f".join([page.text for page in self])
        return None

    def page(self, n):
        """page(n) --> XDWPage"""
        return XDWPage(self, n)

    def __len__(self):
        return self.pages

    def is_document(self):
        """is_document() --> True"""
        return True
    
    def is_binder(self):
        """is_binder() --> False"""
        return False


class XDWDocumentInBinder(object):

    """A document part of DocuWorks binder"""

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
        return "XDWDocumentInBinder(%s = %s[%d]: %d pages, %d files attached)" % (
                self.name,
                self.binder.name, self.position,
                self.position + 1,
                self.pages,
                self.original_data,
                )

    def page(self, n):
        """page(n) --> XDWPage"""
        return XDWPage(self.binder, self.start_page + n)

    def __len__(self):
        return self.pages

    def __getattr__(self, attr):
        if attr == "text":
            return "\f".join([page.text for page in self])
        return None


class XDWBinder(XDWDocument):

    """A DocuWorks Binder"""

    def is_document(self):
        """is_document() --> False"""
        return False
    
    def is_binder(self):
        """is_binder() --> True"""
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
        """document_pages() --> list of page count of each document part of the binder"""
        pages = []
        for pos in range(self.documents):
            docinfo = XDW_GetDocumentInformationInBinder(self.document_handle, pos+1)
            pages.append(docinfo.nPages)
        return pages

    def document(self, position):
        """document(position) --> XDWDocument"""
        return XDWDocumentInBinder(self, position)

    def page(self, n):
        """page(n) --> XDWPage"""
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

    def __getattr__(self, attr):
        if attr == "text":
            return "\f".join([doc.text for doc in self])
        return None

