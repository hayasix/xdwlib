#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix expandtab :

"""binder.py -- Binder

Copyright (C) 2010 HAYASHI Hideki <hideki@hayasix.com>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

from .xdwapi import *
from .common import *
from .observer import *
from .xdwfile import XDWFile
from .documentinbinder import DocumentInBinder
from .page import Page, PageCollection


__all__ = ("Binder", "create", "create_binder")


def create(path, color="RED", size="FREE", coding=CODEPAGE):
    """The XBD generator.

    Returns the created pathname which may differ from path.
    """
    path = derivative_path(path)
    data = XDW_BINDER_INITIAL_DATA()
    data.nBinderColor = XDW_BINDER_COLOR.normalize(color)
    data.nBinderSize = XDW_BINDER_SIZE.normalize(size)
    if XDWVER < 8:
        XDW_CreateBinder(cp(path), data)
    else:
        XDW_CreateBinderW(path, data)
    return path


create_binder = create  # for compatibility


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
        # By default, DW 8+ store document names in binder in Unicode.
        self.unicode = (8 <= XDWVER)

    def __repr__(self):
        return "{cls}({name}{sts})".format(
                cls=self.__class__.__name__,
                name=self.name,
                sts="" if self.handle else "; CLOSED")

    def __str__(self):
        return "{cls}({name}: {docs} documents{sts})".format(
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
            deleted = 0
            for p in range(pos.start, pos.stop, pos.step):
                self.delete(p - deleted)
                deleted += 1
        else:
            self.delete(pos)

    def __iter__(self):
        for pos in range(self.documents):
            yield self.document(pos)

    @staticmethod
    def all_colors():
        """Returns all colors available."""
        return tuple(sorted(
                (XDW_BINDER_COLOR).values()))

    def document(self, pos):
        """Get a DocumentInBinder.

        pos     (int) document number; starts with 0

        Returns a DocumentInBinder object.
        """
        pos = self._pos(pos)
        if pos not in self.observers:
            self.observers[pos] = DocumentInBinder(self, pos)
        return self.observers[pos]

    def page(self, pos):
        """Get a Page for absolute page number.

        pos     (int) absolute page number; starts with 0

        Returns a Page object.
        """
        pos = self._pagepos(pos)
        return self.document_and_page(pos)[1]

    def document_pages(self):
        """Get the list of page count for each document. """
        return [XDW_GetDocumentInformationInBinder(self.handle, pos + 1).nPages
                for pos in range(self.documents)]

    def document_and_page(self, pos):
        """Get (DocumentInBinder, Page) for absolute page number.

        pos     (int) absolute page number; starts with 0

        returns a tuple.
        """
        pos = self._pagepos(pos)
        acc = 0
        for docpos, pages in enumerate(self.document_pages()):
            acc += pages
            if pos < acc:
                doc = self.document(docpos)
                page = doc.page(pos - (acc - pages))
                return (doc, page)

    def append(self, path):
        """Append a document by path at the end of binder.

        path    (str) path to file to add
        """
        self.insert(self.documents, path)

    def insert(self, pos, path):
        """Insert a document by path.

        pos     (int) position to insert; starts with 0
        path    (str) path to file to insert
        """
        pos = self._pos(pos, append=True)
        XDW_InsertDocumentToBinder(self.handle, pos + 1, cp(path))
        self.documents += 1
        doc = self.document(pos)
        self.attach(doc, EV_DOC_INSERTED)

    def delete(self, pos):
        """Delete a document.

        pos     (int) position to delete; starts with 0
        """
        pos = self._pos(pos)
        doc = self.document(pos)
        XDW_DeleteDocumentInBinder(self.handle, doc.pos + 1)
        self.detach(doc, EV_DOC_REMOVED)
        self.documents -= 1

    def export(self, pos, path=None):
        """Export a document in binder.

        pos     (int) position to export; starts with 0
        path    (str) export to {path};
                      with no dir, export to {binder dir}/{path}
                (None) export to {binder dir}/{document name}

        Returns the exported pathname which may differ from path.
        """
        pos = self._pos(pos)
        path = newpath(path or self.document(pos).name + ".xdw", dir=self.dir)
        if XDWVER < 8:
            XDW_GetDocumentFromBinder(self.handle, pos + 1, cp(path))
        else:
            XDW_GetDocumentFromBinderW(self.handle, pos + 1, path)
        return path

    def view(self, light=False, wait=True, page=0, fullscreen=False, zoom=0):
        """View binder with DocuWorks Viewer (Light).

        light       (bool) force to use DocuWorks Viewer Light.
                    Note that DocuWorks Viewer is used if Light version is
                    not avaiable.
        wait        (bool) wait until viewer stops and get annotation info
        page        (int) page number to view
        fullscreen  (bool) view in full screen (presentation mode)
        zoom        (int) in 10-1600 percent; 0 means 100%
                    (str) 'WIDTH' | 'HEIGHT' | 'PAGE'

        If wait is True, returns a dict, each key of which is the absolute
        page pos and the value is a list of AnnotationCache objects i.e.:

            {0: [ann_cache, ann_cache, ...], 1: [...], ...}

        Note that pages without annotations are ignored.

        If wait is False, returns (proc, path) where:

                proc    subprocess.Popen object
                path    pathname of temporary file being viewed

        In this case, you should remove temp and its parent dir after use.

        NB. Attachments are not shown.
        NB. Viewing signed pages will raise AccessDeniedError.
        """
        pc = PageCollection()
        for doc in self:
            pc += PageCollection(doc)
        return pc.view(light=light, wait=wait, flat=False, group=True,
                       page=page, fullscreen=fullscreen, zoom=zoom)

    def content_text(self, type=None):
        """Get all content text.

        type    None | 'IMAGE' | 'APPLICATION'
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

        pattern     (str or regexp supported by re module)

        Returns a PageCollection object, each of which contains the given
        pattern in its content text or annotations.
        """
        return joinf("", [doc.find_fulltext(pattern) for doc in self])
