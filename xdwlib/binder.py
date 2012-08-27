#!/usr/bin/env python2.6
#vim:fileencoding=cp932:fileformat=dos

"""binder.py -- Binder

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

from xdwapi import *
from common import *
from observer import *
from xdwfile import XDWFile
from documentinbinder import DocumentInBinder
from page import Page, PageCollection


__all__ = ("Binder", "create_binder")


def create_binder(path, color="RED", size="FREE", coding=CODEPAGE):
    """The XBD generator.

    Returns actual pathname.
    """
    path = derivative_path(uc(path))
    data = XDW_BINDER_INITIAL_DATA()
    data.nBinderColor = XDW_BINDER_COLOR.normalize(color)
    data.nBinderSize = XDW_BINDER_SIZE.normalize(size)
    XDW_CreateBinder(cp(path), data)
    return path


class Binder(Subject, XDWFile):

    """DocuWorks Binder."""

    def _pos(self, pos, append=False):
        append = 1 if append else 0
        if not (-self.documents <= pos < self.documents + append):
            raise IndexError(
                    "Document number must be in [{0}, {1}), {2} given".format(
                    -self.documents, self.documents + append, pos))
        if pos < 0:
            pos += self.documents
        return pos

    def _pagepos(self, pos, append=False):
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
                self.documents if pos.stop is None else pos.stop,
                1 if pos.step is None else pos.step,
                )

    def __init__(self, path):
        Subject.__init__(self)
        XDWFile.__init__(self, path)

    def __repr__(self):
        return u"{cls}({name}{sts})".format(
                cls=self.__class__.__name__,
                name=self.name,
                sts="" if self.handle else "; CLOSED")

    def __str__(self):
        return u"{cls}({name}: {docs} documents{sts})".format(
                cls=self.__class__.__name__,
                name=self.name,
                docs=self.documents,
                sts="" if self.handle else "; CLOSED")

    def __len__(self):
        return self.documents

    def __getitem__(self, pos):
        if isinstance(pos, slice):
            pos = self._slice(pos)
            return tuple(self.document(p)
                    for p in range(pos.start, pos.stop, pos.step))
        return self.document(pos)

    def __setitem__(self, pos, value):
        raise NotImplementError()

    def __delitem__(self, pos):
        if isinstance(pos, slice):
            for p in range(pos.start, pos.stop, pos.step):
                self.delete(p)
        else:
            self.delete(pos)

    def __iter__(self):
        for pos in xrange(self.documents):
            yield self.document(pos)

    @staticmethod
    def all_colors():
        """Returns all colors available."""
        return tuple(sorted(
                (XDW_BINDER_COLOR).values()))

    def document(self, pos):
        """Get a DocumentInBinder."""
        pos = self._pos(pos)
        return DocumentInBinder(self, pos)

    def page(self, pos):
        """Get a Page for absolute page number."""
        pos = self._pagepos(pos)
        return self.document_and_page(pos)[1]

    def document_pages(self):
        """Get the list of page count for each document. """
        return [XDW_GetDocumentInformationInBinder(self.handle, pos + 1).nPages
                for pos in range(self.documents)]

    def document_and_page(self, pos):
        """Get (DocumentInBinder, Page) for absolute page number."""
        pos = self._pagepos(pos)
        acc = 0
        for docpos, pages in enumerate(self.document_pages()):
            acc += pages
            if pos < acc:
                doc = self.document(docpos)
                page = doc.page(pos - (acc - pages))
                return (doc, page)

    def append(self, path):
        """Append a document by path at the end of binder."""
        self.insert(self.documents, path)

    def insert(self, pos, path):
        """Insert a document by path ."""
        pos = self._pos(pos, append=True)
        XDW_InsertDocumentToBinder(self.handle, pos + 1, cp(path))
        self.documents += 1
        doc = self.document(pos)
        self.attach(doc, EV_DOC_INSERTED)

    def delete(self, pos):
        """Delete a document."""
        pos = self._pos(pos)
        doc = self.document(pos)
        XDW_DeleteDocumentInBinder(self.handle, doc.pos + 1)
        self.detach(doc, EV_DOC_REMOVED)
        self.documents -= 1

    def view(self, light=False, wait=True, *options):
        """View binder with DocuWorks Viewer (Light)."""
        pc = PageCollection()
        for doc in self:
            pc += PageCollection(doc)
        return pc.view(
                light=light, wait=wait, flat=False, group=True, *options)

    def content_text(self, type=None):
        """Get all content text.

        type    None | "IMAGE" | "APPLICATION"
                None means both.
        """
        return joinf(PSEP, [doc.content_text(type=type) for doc in self])

    def annotation_text(self):
        """Get all text in annotations."""
        return joinf(PSEP, [doc.annotation_text() for doc in self])

    def fulltext(self):
        """Get all content text and annotation text."""
        return joinf(PSEP, [doc.fulltext() for doc in self])

    def find_fulltext(self, pattern):
        """Find given pattern (text or regex) throughout binder.

        Returns a PageCollection object, each of which contains the given
        pattern in its content text or annotations.
        """
        return joinf("", [doc.find_fulltext(pattern) for doc in self])
