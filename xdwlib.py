#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""xdwlib.py -- DocuWorks library for Python.

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import sys
from os.path import splitext, basename
import datetime

from xdwapi import *

__all__ = (
    "XDWDocument", "XDWDocumentInBinder", "XDWBinder", "XDWError",
    "environ", "xdwopen", "create", "create_binder",
    "PSEP", "ASEP",
    )

CP = 932
PSEP = "\f"
ASEP = "\v"

try:
    VALID_DOCUMENT_HANDLES
except NameError:
    VALID_DOCUMENT_HANDLES = []


def environ(name=None):
    """DocuWorks environment information"""
    if name:
        value = XDW_GetInformation(XDW_ENVIRON.normalize(name))
        if name == XDW_ENVIRON[XDW_GI_DWDESK_FILENAME_DIGITS]:
            value = ord(value)
        return value
    values = dict()
    for k, v in XDW_ENVIRON.items():
        try:
            value = XDW_GetInformation(k)
            if k == XDW_GI_DWDESK_FILENAME_DIGITS:
                value = ord(value)
            values[v] = value
        except XDWError as e:
            if e.error_code == XDW_E_INFO_NOT_FOUND:
                continue
            else:
                raise
    return values


def xdwopen(path, readonly=False, authenticate=True):
    """General opener"""
    types = {
            ".XDW": XDWDocument,
            ".XBD": XDWBinder,
            }
    ext = splitext(basename(path))[1].upper()
    if ext in types:
        return types[ext](path, readonly=readonly, authenticate=authenticate)
    raise XDWError(XDW_E_INVALIDARG)


def create(
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


def annotation_in(annotation, rect):  # Assume rect is half-open.
    return (rect.left <= annotation.horizontal_position \
                     <= rect.right - annotation.width \
            and \
            rect.top <= annotation.vertical_position \
                     <= rect.bottom - annotation.height)


def find_annotations(object,
        recursive=False, rect=None, types=None,
        half_open=True):
    if rect and not half_open:
        rect.right += 1
        rect.bottom += 1
    if types:
        if not isinstance(types, (list, tuple)):
            types = [types]
        types = [XDW_ANNOTATION_TYPE.normalize(t) for t in types]
    annotation_list = []
    for i in range(object.annotations):
        annotation = object.annotation(i)
        sublist = []
        if recursive and annotation.annotations:
            sublist = find_annotations(annotation,
                    recursive=recursive, rect=rect, types=types,
                    half_open=half_open)
        if (not rect or annotation_in(annotation, rect)) and \
                (not types or annotation.annotation_type in types):
            if sublist:
                sublist.insert(0, annotation)
                annotation_list.append(sublist)
            else:
                annotation_list.append(annotation)
        elif sublist:
            sublist.insert(0, None)
            annotation_list.append(sublist)
    return annotation_list


class XDWAnnotation(object):

    """An annotation on DocuWorks document page"""

    def __init__(self, page, index, parent_annotation=None):
        self.page = page
        self.parent_annotation = parent_annotation
        self.index = index
        if parent_annotation:
            pah = parent_annotation.annotation_handle
        else:
            pah = None
        info = XDW_GetAnnotationInformation(
                page.xdw.document_handle,
                page.page + 1,
                pah,
                index + 1)
        self.annotation_handle = info.handle
        self.horizontal_position = info.nHorPos
        self.vertical_position = info.nVerPos
        self.width = info.nWidth
        self.height = info.nHeight
        self.annotation_type = info.nAnnotationType
        self.annotations = info.nChildAnnotations

    def __str__(self):
        return "XDWAnnotation(%s P%d: type=%s)" % (
                self.page.xdw.name,
                self.page.page,
                XDW_ANNOTATION_TYPE[self.annotation_type],
                )

    def __getattr__(self, name):
        attribute_name = "%" + name
        if attribute_name in XDW_ANNOTATION_ATTRIBUTE:
            return XDW_GetAnnotationAttributeW(
                    self.annotation_handle, unicode(attribute_name), CP)
        raise AttributeError("'%s' object has no attribute '%s'" % (
                self.__class__.__name__, name))

    def __setattr__(self, name, value):
        attribute_name = "%" + name
        if attribute_name in XDW_ANNOTATION_ATTRIBUTE:
            if isinstance(value, basestring):
                attribute_type = XDW_ATYPE_STRING
            else:
                attribute_type = XDW_ATYPE_INT
            XDW_SetAnnotationAttributeW(
                    self.page.xdw.document_handle, self.annotation_handle,
                    unicode(attribute_name), attribute_type, byref(value),
                    XDW_TEXT_MULTIBYTE, CP)
            return
        self.__dict__[name] = value

    def annotation(self, index):
        if self.annotations <= index:
            if self.annotations < 1:
                raise AttributeError("annotation object has no children")
            else:
                raise IndexError(
                        "annotation index %d out of range(0..%d)" % (
                        index, self.annotations - 1))
        return XDWAnnotation(self.page, index, parent_annotation=self)

    def find_annotations(*args, **kw):
        return find_annotations(*args, **kw)

    def text(self, recursive=True):
        ga = XDW_GetAnnotationAttributeW
        if self.annotation_type == XDW_AID_TEXT:
            s = ga(self.annotation_handle, XDW_ATN_Text, CP)[0]
        elif self.annotation_type == XDW_AID_LINK:
            s = ga(self.annotation_handle, XDW_ATN_Caption, CP)[0]
        elif self.annotation_type == XDW_AID_STAMP:
            s = "%s <DATE> %s" % (
                    ga(self.annotation_handle, XDW_ATN_TopField, CP)[0],
                    ga(self.annotation_handle, XDW_ATN_BottomField, CP)[0],
                    )
        else:
            s = None
        if recursive and self.annotations:
            s = [s]
            s.extend([self.annotation(i).text(recursive=True) \
                    for i in range(self.annotations)])
            s = ASEP.join(t for t in s if isinstance(t, basestring))
        return s


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
        page_info = XDW_GetPageInformation(
                xdw.document_handle, page + 1, extend=True)
        self.width = page_info.nWidth  # 1/100 mm
        self.height = page_info.nHeight  # 1/100 mm
        # XDW_PGT_FROMIMAGE/FROMAPPL/NULL
        self.page_type = page_info.nPageType
        self.horizontal_resolution = XDWPage.normalize_resolution(
                page_info.nHorRes)  # dpi
        self.vertical_resolution = XDWPage.normalize_resolution(
                page_info.nVerRes)  # dpi
        self.compress_type = page_info.nCompressType
        self.annotations = page_info.nAnnotations
        self.degree = page_info.nDegree
        self.original_width = page_info.nOrgWidth  # 1/100 mm
        self.original_height = page_info.nOrgHeight  # 1/100 mm
        self.original_horizontal_resolution = XDWPage.normalize_resolution(
                page_info.nOrgHorRes)  # dpi
        self.original_vertical_resolution = XDWPage.normalize_resolution(
                page_info.nOrgVerRes)  # dpi
        self.image_width = page_info.nImageWidth  # px
        self.image_height = page_info.nImageHeight  # px

    def __str__(self):
        return "XDWPage(page %d: %.2f*%.2fmm, %s, %d annotations)" % (
                self.page,
                self.width / 100.0, self.height / 100.0,
                XDW_PAGE_TYPE[self.page_type],
                self.annotations,
                )

    def annotation(self, index):
        """annotation(n) --> XDWAnnotation"""
        if self.annotations <= index:
            if self.annotations < 1:
                raise AttributeError("page object has no annotations")
            else:
                raise IndexError(
                        "annotation index %d out of range(0..%d)" % (
                        index, self.annotations - 1))
        return XDWAnnotation(self, index)

    def find_annotations(*args, **kw):
        return find_annotations(*args, **kw)

    def text(self):
        return XDW_GetPageTextToMemoryW(self.xdw.document_handle,
                self.page + 1)

    def annotation_text(self, recursive=True):
        s = [a.text(recursive=recursive) for a in self.find_annotations()]
        return ASEP.join([t for t in s if isinstance(t, basestring)])

    def rotate(self, degree=0, auto=False):
        if auto:
            XDW_RotatePageAuto(self.xdw.document_handle, self.page)
            self.xdw.finalize = True
        else:
            XDW_RotatePage(self.xdw.document_handle, self.page, degree)
    
    def reduce_noise(self, level=XDW_REDUCENOISE_NORMAL):
        level = XDW_OCR_NOISEREDUCTION.normalize(level)
        XDW_ReducePageNoise(self.document_handle, self.page, level)

    def ocr(self,
            engine=XDW_OCR_ENGINE_DEFAULT,
            strategy=XDW_OCR_ENGINE_LEVEL_SPEED,
            preprocessing=XDW_PRIORITY_SPEED,
            noise_reduction=XDW_REDUCENOISE_NONE,
            deskew=True,
            form=XDW_OCR_FORM_AUTO,
            column=XDW_OCR_COLUMN_AUTO,
            rects=None,
            language=XDW_OCR_LANGUAGE_AUTO,
            main_language=XDW_OCR_MIXEDRATE_BALANCED,
            use_ascii=True,
            insert_space=False,
            verbose=False,
            ):
        option = XDW_OCR_OPTION_V7()
        engine = XDW_OCR_ENGINE.normalize(engine)
        option.nEngineLevel = XDW_OCR_STRATEGY.normalize(strategy)
        option.nPriority = XDW_OCR_PREPROCESSING.normalize(preprocessing)
        option.nNoiseReduction = XDW_OCR_NOISEREDUCTION.normalize(noise_reduction)
        option.nAutoDeskew = bool(deskew)
        option.nForm = XDW_OCR_FORM.normalize(form)
        option.nColumn = XDW_OCR_COLUMN.normalize(column)
        option.nLanguage = XDW_OCR_LANGUAGE.normalize(language)
        option.nLanguageMixedRate = XDW_OCR_MAIN_LANGUAGE.normalize(main_language)
        option.nHalfSizeChar = bool(use_ascii)
        option.nInsertSpaceCharacter = bool(insert_space)
        option.nDisplayProcess = bool(verbose)
        if rects:
            option.nAreaNum = len(rects)
            rectlist = XDW_RECT() * len(rects)
            for r, rect in zip(rectlist, rects):
                r.left = rect[0][0]
                r.top = rect[0][1]
                r.right = rect[1][0]
                r.bottom = rect[1][1]
            option.pAreaRects = byref(rectlist)
        else:
            option.pAreaRects = NULL
        XDW_ApplyOcr(self.xdw.document_handle, self.page, engine, byref(option))
        self.finalize = True


class XDWDocument(object):

    """A DocuWorks document"""

    def register(self):
        VALID_DOCUMENT_HANDLES.append(self.document_handle)

    def free(self):
        VALID_DOCUMENT_HANDLES.remove(self.document_handle)

    def __init__(self, path, readonly=False, authenticate=True):
        open_mode = XDW_OPEN_MODE_EX()
        if readonly:
            open_mode.nOption = XDW_OPEN_READONLY
        else:
            open_mode.nOption = XDW_OPEN_UPDATE
        if authenticate:
            open_mode.nAuthMode = XDW_AUTH_NODIALOGUE
        else:
            open_mode.nAuthMode = XDW_AUTH_NONE
        self.document_handle = XDW_OpenDocumentHandle(path, open_mode)
        self.register()
        self.name = splitext(basename(path))[0]
        try:
            self.name = self.name.decode("cp%d" % CP)
        except:
            pass
        # Set document properties.
        document_info = XDW_GetDocumentInformation(self.document_handle)
        self.pages = document_info.nPages
        self.version = document_info.nVersion - 3  # DocuWorks version
        self.original_data = document_info.nOriginalData
        self.document_type = document_info.nDocType
        self.editable = bool(document_info.nPermission & XDW_PERM_DOC_EDIT)
        self.annotatable = bool(
                document_info.nPermission & XDW_PERM_ANNO_EDIT)
        self.printable = bool(document_info.nPermission & XDW_PERM_PRINT)
        self.copyable = bool(document_info.nPermission & XDW_PERM_COPY)
        self.show_annotations = bool(document_info.nShowAnnotations)
        # Followings are effective only for binders.
        self.documents = document_info.nDocuments
        self.binder_color = document_info.nBinderColor
        self.binder_size = document_info.nBinderSize
        # Document attributes.
        self.attributes = XDW_GetDocumentAttributeNumber(self.document_handle)
        # Remember if this must be finalized.
        self.finalize = False

    def __str__(self):
        return "XDWDocument(%s: %d pages, %d files attached)" % (
                self.name,
                self.pages,
                self.documents,
                )

    def __getattr__(self, name):
        attribute_name = u"%" + name
        try:
            return XDW_GetDocumentAttributeByNameW(
                    self.document_handle, attribute_name, CP)[1]
        except XDWError as e:
            if e.error_code == XDW_E_INVALIDARG:
                raise AttributeError("'%s' object has no attribute '%s'" % (
                        self.__class__.__name__, name))
            else:
                raise

    def __setattr__(self, name, value):
        attribute_name = "%" + name
        if isinstance(value, basestring):
            attribute_type = XDW_ATYPE_STRING
        elif isinstance(value, bool):
            attribute_type = XDW_ATYPE_BOOL
        elif isinstance(value, datetime.datetime):
            attribute_type = XDW_ATYPE_DATE
        else:
            attribute_type = XDW_ATYPE_INT
        # TODO: XDW_ATYPE_OTHER should also be valid.
        if attribute_name in XDW_DOCUMENT_ATTRIBUTE:
            XDW_SetDocumentAttributeW(
                    self.document_handle,
                    attribute_name, attribute_type, byref(value),
                    XDW_TEXT_MULTIBYTE, CP)
            return
        self.__dict__[name] = value

    def __len__(self):
        return self.pages

    def __iter__(self):
        self.current_page = 0
        return self

    def next(self):
        if self.pages <= self.current_page:
            raise StopIteration
        page = self.current_page
        self.current_page += 1
        return XDWPage(self, page)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        if self.finalize:
            XDW_Finalize(sefl.document_handle)
        XDW_CloseDocumentHandle(self.document_handle)
        self.free()

    def is_document(self):
        """is_document() --> True"""
        return True

    def is_binder(self):
        """is_binder() --> False"""
        return False

    def save(self):
        XDW_SaveDocument(self.document_handle)

    def page(self, n):
        """page(n) --> XDWPage"""
        return XDWPage(self, n)

    def delete_page(self, n):
        XDW_DeletePage(self.document_handle, n)

    def text(self):
        return PSEP.join(page.text() for page in self)

    def annotation_text(self):
        return PSEP.join(page.annotation_text() for page in self)

    def fulltext(self):
        return PSEP.join(
                page.text() + ASEP + page.annotation_text() for page in self)


class XDWDocumentInBinder(object):

    """A document part of DocuWorks binder"""

    def __init__(self, binder, position):
        self.binder = binder
        self.position = position
        self.page_offset = sum(binder.document_pages[:position])
        self.name = XDW_GetDocumentNameInBinderW(
                self.binder.document_handle, position + 1, CP)[0]
        document_info = XDW_GetDocumentInformationInBinder(
                self.binder.document_handle, position + 1)
        self.pages = document_info.nPages
        self.original_data = document_info.nOriginalData

    def __str__(self):
        return "XDWDocumentInBinder(" \
                "%s = %s[%d]: %d pages, %d attachments)" % (
                self.name,
                self.binder.name, self.position,
                self.position + 1,
                self.pages,
                self.original_data,
                )

    def __len__(self):
        return self.pages

    def __iter__(self):
        self.current_page = 0
        return self

    def next(self):
        if self.pages <= self.current_page:
            raise StopIteration
        n = self.page_offset + self.current_page
        self.current_page += 1
        return XDWPage(self.binder, n)

    def page(self, n):
        """page(n) --> XDWPage"""
        return XDWPage(self.binder, self.page_offset + n)

    def delete_page(self, n):
        XDW_DeletePage(self.binder.document_handle, self.page_offset + n)

    def text(self):
        return PSEP.join(page.text() for page in self)

    def annotation_text(self):
        return PSEP.join(page.annotation_text() for page in self)

    def fulltext(self):
        return PSEP.join(
                page.text() + ASEP + page.annotation_text() for page in self)


class XDWBinder(XDWDocument):

    """A DocuWorks Binder"""

    def __init__(self, path, readonly=False, authenticate=True):
        XDWDocument.__init__(self,
                path=path, readonly=readonly, authenticate=authenticate)
        assert self.document_type == XDW_DT_BINDER
        self.document_pages = self.document_pages()

    def __str__(self):
        return "XDWBinder(%s: %d documents, %d pages, %d attachments)" % (
                self.name,
                self.documents,
                self.pages,
                self.original_data,
                )

    def __len__(self):
        return self.documents

    def __iter__(self):
        self.current_position = 0
        return self

    def next(self):
        if self.documents <= self.current_position:
            raise StopIteration
        pos = self.current_position
        self.current_position += 1
        return  XDWDocumentInBinder(self, pos)

    def is_document(self):
        """is_document() --> False"""
        return False

    def is_binder(self):
        """is_binder() --> True"""
        return True

    def document(self, position):
        """document(position) --> XDWDocument"""
        return XDWDocumentInBinder(self, position)

    def document_pages(self):
        """document_pages() --> list

        Get list of page count for each document in binder
        """
        pages = []
        for pos in range(self.documents):
            docinfo = XDW_GetDocumentInformationInBinder(
                    self.document_handle, pos + 1)
            pages.append(docinfo.nPages)
        return pages

    def text(self):
        return PSEP.join([doc.text() for doc in self])
