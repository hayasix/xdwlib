#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""documentinbinder.py -- DocumentInBinder

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
from basedocument import BaseDocument


__all__ = ("DocumentInBinder",)


class DocumentInBinder(BaseDocument, Observer):

    """Document part of DocuWorks binder."""

    def __init__(self, bdoc, pos):
        BaseDocument.__init__(self)
        self.pos = pos
        Observer.__init__(self, bdoc, EV_DOC_INSERTED)
        self.binder = bdoc
        self._set_page_offset()  # self.page_offset
        docinfo = XDW_GetDocumentInformationInBinder(
                self.binder.handle, pos + 1)
        self.pages = docinfo.nPages
        self.original_data = docinfo.nOriginalData  # TODO

    @property
    def handle(self):
        return self.binder.handle

    @property
    def name(self):
        return XDW_GetDocumentNameInBinderW(
                self.binder.handle, self.pos + 1, codepage=CP)[0]

    @name.setter
    def name(self, value):
        XDW_SetDocumentNameInBinderW(
                self.binder.handle, self.pos + 1, uc(value),
                XDW_TEXT_MULTIBYTE, CP)

    def update_pages(self):
        """Concrete method over update_pages()."""
        docinfo = XDW_GetDocumentInformationInBinder(
                self.binder.handle, pos + 1)
        self.pages = docinfo.nPages

    def __repr__(self):
        return u"{cls}({name} ({bdoc}[{pos}]){status})".format(
                cls=self.__class__.__name__,
                name=self.name,
                bdoc=self.binder.name,
                pos=self.pos,
                status="" if self.binder.handle else "; CLOSED")

    def __str__(self):
        return (u"{cls}({name} ({bdoc}[{pos}]): "
                u"{pages} pages, {atts} attachments{status})").format(
                cls=self.__class__.__name__,
                name=self.name,
                bdoc=self.binder.name,
                pos=self.pos,
                pages=self.pages,
                atts=self.original_data,
                status="" if self.binder.handle else "; CLOSED")

    def update(self, event):
        if not isinstance(event, Notification):
            raise TypeError("not an instance of Notification class")
        if event.type == EV_DOC_REMOVED:
            if event.para[0] < self.pos:
                self.pos -= 1
                self._set_page_offset()
        elif event.type == EV_DOC_INSERTED:
            if event.para[0] < self.pos:
                self.pos += 1
                self._set_page_offset()
        else:
            raise ValueError("illegal event type: {0}".format(event.type))

    def _set_page_offset(self):
        """Private method to renew the page offset for DocumentInBinder."""
        self.page_offset = sum(self.binder.document_pages()[:self.pos])

    def absolute_page(self, pos, append=False):
        """Concrete method over absolute_page()."""
        pos = self._pos(pos, append=append)
        return self.page_offset + pos

    def dirname(self):
        """Concrete method over dirname()."""
        return self.binder.dir
