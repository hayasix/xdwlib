#!/usr/bin/env python2.6
#vim:fileencoding=cp932:fileformat=dos

"""basedocument.py -- DocuWorks library for Python.

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

from common import *
from page import Page, PageCollection


__all__ = ("BaseDocument",)


class BaseDocument(Subject):

    """DocuWorks document base class.

    This class is a base class, which is expected to be inherited by Document
    or DocumentInBinder class.

    Each BaseDocument instance has an observer dict.  This dict holds
    (page_number, Page_object) pairs, and is used to notify page insertion
    or deletion.  Receiving this notification, every Page object should adjust
    its memorized page number.
    """

    def __init__(self):
        Subject.__init__(self)

    def __repr__(self):  # abstract
        raise NotImplementedError()

    def __str__(self):  # abstract
        raise NotImplementedError()

    def __len__(self):
        return self.pages

    def __getitem__(self, pos):
        return self.page(pos)

    def __setitem__(self, pos, val):
        raise NotImplementedError()

    def __iter__(self):
        for pos in xrange(self.pages):
            yield self.page(pos)

    def absolute_page(self, pos):  # abstract
        """Get absolute page number in binder/document."""
        raise NotImplementedError()

    def page(self, pos):
        """Get a Page object."""
        if self.pages <= pos:
            raise IndexError("Page number must be < %d, %d given" % (
                    self.pages, pos))
        if pos not in self.observers:
            self.observers[pos] = Page(self, pos)
        return self.observers[pos]

    def append_page(self, page):
        """Append a page on the tail of document."""
        self.insert_page(-1, page)

    def insert_page(self, pos, page):
        """Insert a page."""
        raise NotImplementedError()
        # (.. some code to insert a page ..)
        self.attach(page, EV_PAGE_INSERTED)
        self.pages += 1

    def delete_page(self, pos):
        """Delete a page."""
        page = self.page(pos)
        XDW_DeletePage(self.handle, self.absolute_page(pos) + 1)
        self.detach(page, EV_PAGE_REMOVED)
        self.pages -= 1

    def content_text(self):
        """Get all content text."""
        return joinf(PSEP, [page.content_text() for page in self])

    def annotation_text(self):
        """Get all text in annotations."""
        return joinf(PSEP, [page.annotation_text() for page in self])

    def fulltext(self):
        """Get all content text and annotation text."""
        return joinf(PSEP, [
                joinf(ASEP, [page.content_text(), page.annotation_text()])
                for page in self])

    def find_fulltext(self, pattern):
        """Find given pattern (text or regex) throughout document.

        Returns a PageCollection object, each of which contains the given
        pattern in its content text or annotations.
        """
        if isinstance(pattern, (str, unicode)):
            f = lambda page: pattern in page.fulltext()
        else:
            f = lambda page: pattern.search(page.fulltext())
        return PageCollection(filter(f, self))

    def dirname(self):  # abstract
        raise NotImplementedError()
