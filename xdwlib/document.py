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

import sys
from os.path import splitext, basename
import datetime

from common import *
from page import Page


__all__ = ("Document", "DocumentInBinder", "Binder",
           "xdwopen", "create", "create_binder")


# The last resort to close documents in interactive session.
try:
    VALID_DOCUMENT_HANDLES
except NameError:
    VALID_DOCUMENT_HANDLES = []


def xdwopen(path, readonly=False, authenticate=True):
    """General opener"""
    types = {
            ".XDW": Document,
            ".XBD": Binder,
            }
    ext = splitext(basename(path))[1].upper()
    if ext not in types:
        raise XDWError(XDW_E_INVALIDARG)
    return types[ext](path, readonly=readonly, authenticate=authenticate)


def create(
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
    """A XDW generator"""
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


def create_binder(path, color=XDW_BINDER_COLOR_0, size=XDW_SIZE_FREE):
    """The XBD generator"""
    XDW_CreateBinder(path, color, size)


class Document(Subject):

    """DocuWorks document"""

    @staticmethod
    def all_types():
        return XDW_DOCUMENT_TYPE

    @staticmethod
    def all_attributes():
        return [outer_attribute_name(k) for k in XDW_DOCUMENT_ATTRIBUTE_W]

    def register(self):
        VALID_DOCUMENT_HANDLES.append(self.handle)

    def free(self):
        VALID_DOCUMENT_HANDLES.remove(self.handle)

    def __init__(self, path, readonly=False, authenticate=True):
        Subject.__init__(self)
        open_mode = XDW_OPEN_MODE_EX()
        if readonly:
            open_mode.nOption = XDW_OPEN_READONLY
        else:
            open_mode.nOption = XDW_OPEN_UPDATE
        if authenticate:
            open_mode.nAuthMode = XDW_AUTH_NODIALOGUE
        else:
            open_mode.nAuthMode = XDW_AUTH_NONE
        if isinstance(path, str):
            path = unicode(path, CODEPAGE)
        self.handle = XDW_OpenDocumentHandle(path, open_mode)
        self.register()
        self.name = splitext(basename(path))[0]
        # Set document properties.
        document_info = XDW_GetDocumentInformation(self.handle)
        self.pages = document_info.nPages
        self.version = document_info.nVersion - 3  # DocuWorks version
        self.original_data = document_info.nOriginalData
        self.type = document_info.nDocType
        self.editable = bool(document_info.nPermission & XDW_PERM_DOC_EDIT)
        self.annotatable = bool(document_info.nPermission & XDW_PERM_ANNO_EDIT)
        self.printable = bool(document_info.nPermission & XDW_PERM_PRINT)
        self.copyable = bool(document_info.nPermission & XDW_PERM_COPY)
        self.show_annotations = bool(document_info.nShowAnnotations)
        # Followings are effective only for binders.
        self.documents = document_info.nDocuments
        self.binder_color = document_info.nBinderColor
        self.binder_size = document_info.nBinderSize
        # Document attributes.
        self.attributes = XDW_GetDocumentAttributeNumber(self.handle)
        # Remember if this must be finalized.
        self.finalize = False

    def __str__(self):
        return "Document(%s: %d pages, %d files attached)" % (
                self.name, self.pages, self.documents)

    def __getattr__(self, name):
        name = unicode(name)
        attribute_name = inner_attribute_name(name)
        try:
            return XDW_GetDocumentAttributeByNameW(
                    self.handle, attribute_name, codepage=CP)[1]
        except XDWError as e:
            if e.error_code != XDW_E_INVALIDARG:
                raise
        return self.__dict__[name]

    def __setattr__(self, name, value):
        name = unicode(name)
        attribute_name = inner_attribute_name(name)
        if isinstance(value, basestring):
            attribute_type = XDW_ATYPE_STRING
        elif isinstance(value, bool):
            attribute_type = XDW_ATYPE_BOOL
        elif isinstance(value, datetime.datetime):
            attribute_type = XDW_ATYPE_DATE
            if not value.tzinfo:
                value = value.replace(tzinfo=DEFAULT_TZ)  # TODO: Care locale.
            value = unixtime(value)
        else:
            attribute_type = XDW_ATYPE_INT  # TODO: Scaling may be required.
        # TODO: XDW_ATYPE_OTHER should also be valid.
        if attribute_name in XDW_DOCUMENT_ATTRIBUTE_W:
            XDW_SetDocumentAttributeW(
                    self.handle, attribute_name, attribute_type, value,
                    XDW_TEXT_MULTIBYTE, codepage=CP)
            return
        self.__dict__[name] = value

    def __len__(self):
        return self.pages

    def __iter__(self):
        self.current_pos = 0
        return self

    def next(self):
        if self.pages <= self.current_pos:
            raise StopIteration
        pos = self.current_pos
        self.current_pos += 1
        return self.page(pos)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def typename(self):
        return XDW_DOCUMENT_TYPE[self.type]

    def save(self):
        """Save document regardless of whether it is modified or not."""
        XDW_SaveDocument(self.handle)

    def close(self):
        """Finalize document if neccesary, and close document."""
        if self.finalize:
            XDW_Finalize(self.handle)
        XDW_CloseDocumentHandle(self.handle)
        self.free()

    def is_document(self):
        """Always True."""
        return True

    def is_binder(self):
        """Always False."""
        return False

    def page(self, pos):
        """page(pos) --> Page"""
        if pos not in self.observers:
            self.observers[pos] = Page(self, pos)
        return self.observers[pos]

    def add_page(self, *args):
        raise NotImplementedError()

    def delete_page(self, pos):
        """Delete a page given by pos.

        delete_page(pos)
        """
        page = self.page(pos)
        XDW_DeletePage(self.handle, page.pos + 1)
        self.detach(page, EV_PAGE_REMOVED)
        self.pages -= 1

    def content_text(self):
        return joinf(PSEP, [page.content_text() for page in self])

    def annotation_text(self):
        return joinf(PSEP, [page.annotation_text() for page in self])

    def fulltext(self):
        return joinf(PSEP, [
                joinf(ASEP, [page.content_text(), page.annotation_text()])
                for page in self])


class DocumentInBinder(Subject, Observer):

    """Document part of DocuWorks binder"""

    def __init__(self, binder, pos):
        self.pos = pos
        Subject.__init__(self)
        Observer.__init__(self, binder, EV_DOC_INSERTED)
        self.binder = binder
        self.page_offset = sum(binder.document_pages[:pos])
        self.name = XDW_GetDocumentNameInBinderW(
                self.binder.handle, pos + 1, codepage=CP)[0]
        document_info = XDW_GetDocumentInformationInBinder(
                self.binder.handle, pos + 1)
        self.pages = document_info.nPages
        self.original_data = document_info.nOriginalData

    def __str__(self):
        return "DocumentInBinder(" \
                "%s = %s[%d]: %d pages, %d attachments)" % (
                self.name,
                self.binder.name, self.pos,
                self.pages,
                self.original_data,
                )

    def __len__(self):
        return self.pages

    def __iter__(self):
        self.current_pos = 0
        return self

    def next(self):
        if self.pages <= self.current_pos:
            raise StopIteration
        pos = self.page_offset + self.current_pos
        self.current_pos += 1
        return self.binder.page(pos)

    def update(self, event):
        if not isinstance(event, Notification):
            raise TypeError("not an instance of Notification class")
        if event.type == EV_PAGE_REMOVED and event.para[0] < self.page_offset:
                self.page_offset -= 1
        if event.type == EV_PAGE_INSERTED and event.para[0] < self.page_offset:
                self.page_offset += 1
        else:
            raise ValueError("illegal event type")

    def is_document(self):
        """Always False."""
        return False

    def is_binder(self):
        """Always False."""
        return False

    def page(self, pos):
        """page(pos) --> Page"""
        if page in self.observers:
            return self.observers[pos]
        self.observers[pos] = Page(self.binder, self.page_offset + pos)

    def delete_page(self, pos):
        """Delete a page given by pos.

        delete_page(pos)
        """
        page = self.page(pos)
        XDW_DeletePage(self.binder.handle, page.pos)
        self.detach(page, EV_PAGE_REMOVED)
        self.binder.notify(Notification(EV_PAGE_REMOVED, page.pos))
        # TODO: avoid duplicate notification and self-position-shift.
        self.pages -= 1

    def update(self, event):
        if not isinstance(event, Notification):
            raise TypeError("not an instance of Notification class")
        if event.type == EV_PAGE_REMOVED:
            if event.para[0] < self.page_offset:
                self.page_offset -= 1
        if event.type == EV_PAGE_INSERTED:
            if event.para[0] < self.page_offset:
                self.page_offset += 1
        else:
            raise ValueError("illegal event type: %d" % event.type)

    def add_page(self, *args):
        raise NotImplementedError()

    def content_text(self):
        return joinf(PSEP, [page.content_text() for page in self])

    def annotation_text(self):
        return joinf(PSEP, [page.annotation_text() for page in self])

    def fulltext(self):
        return joinf(PSEP, [
                joinf(ASEP, [page.content_text(), page.annotation_text()])
                for page in self])


class Binder(Document):

    """A DocuWorks Binder"""

    def __init__(self, path, readonly=False, authenticate=True):
        Document.__init__(self,
                path=path, readonly=readonly, authenticate=authenticate)
        assert self.type == XDW_DT_BINDER
        self.document_pages = self.document_pages()

    def __str__(self):
        return "Binder(%s: %d documents, %d pages, %d attachments)" % (
                self.name,
                self.documents,
                self.pages,
                self.original_data,
                )

    def __len__(self):
        return self.documents

    def __iter__(self):
        self.current_pos = 0
        return self

    def next(self):
        if self.documents <= self.current_pos:
            raise StopIteration
        pos = self.current_pos
        self.current_pos += 1
        return self.document(pos)

    def is_document(self):
        """Always False."""
        return False

    def is_binder(self):
        """Always True."""
        return True

    def document(self, pos):
        """document(pos) --> DocumentInBinder"""
        if pos not in self.observers:
            self.observers[pos] = DocumentInBinder(self, pos)
        return self.observers[pos]

    def document_and_page(self, pos):
        """document_and_page(pos) --> (DocumentInBinder, Page)"""
        if self.pages <= pos:
            raise IndexError("page %d exceeds total pages of binder" % pos)
        acc = 0
        for docnum, pages in enumerate(self.document_pages()):
            acc += pages
            if pos < acc:
                doc = self.document(docnum)
                page = doc.page(pos - (acc - pages))
                return (doc, page)

    def page(self, pos):
        """page(pos) --> Page"""
        return self.document_and_page(self, pos)[1]

    def document_pages(self):
        """Get list of page count for each document in binder. """
        pages = []
        for pos in range(self.documents):
            docinfo = XDW_GetDocumentInformationInBinder(
                    self.handle, pos + 1)
            pages.append(docinfo.nPages)
        return pages

    def delete_document(self, pos):
        """Delete a document in binder given by pos.

        delete_document(pos)
        """
        doc = self.document(pos)
        XDW_DeleteDocumentInBinder(self.handle, doc.pos + 1)
        self.detach(doc, EV_DOC_REMOVED)
        self.documents -= 1

    def content_text(self):
        return joinf(PSEP, [doc.content_text() for doc in self])

    def annotation_text(self):
        return joinf(PSEP, [doc.annotation_text() for doc in self])

    def fulltext(self):
        return joinf(PSEP, [
                joinf(ASEP, [doc.content_text(), doc.annotation_text()])
                for doc in self])
