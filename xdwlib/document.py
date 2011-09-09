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

from common import *
from xdwfile import XDWFile
from basedocument import BaseDocument
from documentinbinder import DocumentInBinder
from page import Page


__all__ = ("Document",)


class Document(BaseDocument, XDWFile):

    """DocuWorks document (XDW)"""

    def __init__(self, path, readonly=False, authenticate=True):
        BaseDocument.__init__(self)
        XDWFile.__init__(self, path,
                readonly=readonly, authenticate=authenticate)
        assert self.type == XDW_DT_DOCUMENT

    def __repr__(self):
        return u"Document(%s)" % self.name

    def __str__(self):
        return u"Document(%s: %d pages, %d attachments)" % (
                self.name, self.pages, self.original_data)

    def require_finalization(self):
        self.finalize = True

    def absolute_page(self, pos):
        return pos

    def dirname(self):
        return self.dirname
