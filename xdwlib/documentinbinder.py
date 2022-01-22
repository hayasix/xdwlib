#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix expandtab :

"""documentinbinder.py -- DocumentInBinder

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
from .basedocument import BaseDocument


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
        self.name  # Set self.text_type

    @property
    def handle(self):
        return self.binder.handle

    @property
    def name(self):
        name_, type_ = XDW_GetDocumentNameInBinderW(
                        self.binder.handle, self.pos + 1, codepage=CP)
        self.text_type = XDW_TEXT_TYPE[type_]
        return name_

    def name_compat(self, encoding, errors="ignore"):
        return XDW_GetDocumentNameInBinder(
                self.binder.handle, self.pos + 1).decode(encoding, errors=errors)

    @name.setter
    def name(self, value):
        if self.binder.unicode:
            coding = XDW_TEXT_UNICODE
        elif XDWVER < 8:
            coding = XDW_TEXT_UNICODE_IFNECESSARY
        else:  # DW 8+ seems to prefer Unicode even if IFNECESSARY is specified.
            coding = XDW_TEXT_MULTIBYTE
        XDW_SetDocumentNameInBinderW(
                self.binder.handle, self.pos + 1, value, coding, CP)

    def update_pages(self):
        """Concrete method over update_pages()."""
        docinfo = XDW_GetDocumentInformationInBinder(
                self.binder.handle, pos + 1)
        self.pages = docinfo.nPages

    def __repr__(self):
        return "{cls}({name} ({bdoc}[{pos}]){status})".format(
                cls=self.__class__.__name__,
                name=self.name,
                bdoc=self.binder.name,
                pos=self.pos,
                status="" if self.binder.handle else "; CLOSED")

    def __str__(self):
        return ("{cls}({name} ({bdoc}[{pos}]): "
                "{pages} pages, {atts} attachments{status})").format(
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
            raise ValueError(f"illegal event type: {event.type}")

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

    def save(self, path=None):
        """Save attached file.

        path    (str) save to {path};
                      with no dir, save to {binder dir}/{path}
                (None) save to {binder dir}/{attachment filename}

        Returns the saved pathname which may differ from path.
        """
        return self.binder.export(self.pos, path=path)
