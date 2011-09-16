#!/usr/bin/env python2.6
#vim:fileencoding=cp932:fileformat=dos

"""binder.py -- DocuWorks library for Python.

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

from common import *
from xdwfile import XDWFile
from documentinbinder import DocumentInBinder
from page import Page, PageCollection


__all__ = ("Binder", "create_binder")


def create_binder(path, color=XDW_BINDER_COLOR_0, size=XDW_SIZE_FREE,
        coding=CODEPAGE):
    """The XBD generator"""
    data = XDW_BINDER_INITIAL_DATA()
    data.nBinderColor = color
    data.nBinderSize = size
    XDW_CreateBinder(path.encode(coding), data)


class Binder(Subject, XDWFile):

    """DocuWorks Binder"""

    def __init__(self, path, readonly=False, authenticate=True):
        Subject.__init__(self)
        XDWFile.__init__(self, path,
                readonly=readonly, authenticate=authenticate)
        assert self.type == XDW_DT_BINDER

    def __repr__(self):
        return u"Binder(%s)" % self.name

    def __str__(self):
        return u"Binder(%s: %d documents)" % (self.name, self.documents)

    def __len__(self):
        return self.documents

    def __getitem__(self, pos):
        return self.document(pos)

    def __setitem__(self, pos):
        raise NotImplementError()

    def __iter__(self):
        for pos in xrange(self.documents):
            yield self.document(pos)

    def document(self, pos):
        """Get DocumentInBinder object for given position."""
        if self.documents <= pos:
            raise IndexError(
                    "Document number must be < %d, %d given" % (
                    self.documents, pos))
        return DocumentInBinder(self, pos)

    def page(self, pos):
        """Get Page object for absolute page number."""
        return self.document_and_page(pos)[1]

    def document_pages(self):
        """Get list of page count for each document. """
        return [XDW_GetDocumentInformationInBinder(self.handle, pos + 1).nPages
                for pos in range(self.documents)]

    def document_and_page(self, pos):
        """Get (DocumentInBinder, Page) for absolute page number."""
        if self.pages <= pos:
            raise IndexError("Page number must be < %d, %d given" % (
                    self.pages, pos))
        acc = 0
        for docpos, pages in enumerate(self.document_pages()):
            acc += pages
            if pos < acc:
                doc = self.document(docpos)
                page = doc.page(pos - (acc - pages))
                return (doc, page)

    def append_document(self, path):
        """Append a document at the last position."""
        self.insert_document(self.documents, path)

    def insert_document(self, pos, path):
        """Insert a document."""
        XDW_InsertDocumentToBinder(self.handle, pos + 1, path)
        self.attach(doc, EV_DOC_INSERTED)
        self.documents += 1

    def delete_document(self, pos):
        """Delete a document."""
        doc = self.document(pos)
        XDW_DeleteDocumentInBinder(self.handle, doc.pos + 1)
        self.detach(doc, EV_DOC_REMOVED)
        self.documents -= 1

    def content_text(self):
        """Get all content text."""
        return joinf(PSEP, [doc.content_text() for doc in self])

    def annotation_text(self):
        """Get all text in annotations."""
        return joinf(PSEP, [doc.annotation_text() for doc in self])

    def fulltext(self):
        """Get all content text and annotation text."""
        return joinf(PSEP, [
                joinf(ASEP, [doc.content_text(), doc.annotation_text()])
                for doc in self])

    def find_fulltext(self, pattern):
        """Find given pattern (text or regex) throughout binder.

        Returns a PageCollection object, each of which contains the given
        pattern in its content text or annotations.
        """
        from operator import add
        return reduce(add, [doc.find_fulltext(pattern) for doc in self])
