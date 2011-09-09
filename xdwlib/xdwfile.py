#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""xdwfile.py -- DocuWorks library for Python.

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import os
import datetime

from xdwapi import *
from common import *


__all__ = ("XDWFile",)


# The last resort to close documents in interactive session.
try:
    VALID_DOCUMENT_HANDLES
except NameError:
    VALID_DOCUMENT_HANDLES = []


class XDWFile(object):

    """Docuworks file (XDW or XBD)"""

    @staticmethod
    def all_attributes():  # for debugging
        return [outer_attribute_name(k) for k in XDW_DOCUMENT_ATTRIBUTE_W]

    def register(self):
        VALID_DOCUMENT_HANDLES.append(self.handle)

    def free(self):
        VALID_DOCUMENT_HANDLES.remove(self.handle)

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
        if isinstance(path, str):
            path = unicode(path, CODEPAGE)
        self.handle = XDW_OpenDocumentHandle(path, open_mode)
        self.register()
        self.dirname, self.name = os.path.split(path)
        self.name = os.path.splitext(self.name)[0]
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

    def save(self):
        """Save document regardless of whether it is modified or not."""
        XDW_SaveDocument(self.handle)

    def close(self):
        """Finalize document if neccesary, and close document."""
        if self.finalize:
            XDW_Finalize(self.handle)
        XDW_CloseDocumentHandle(self.handle)
        self.free()

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

    def typename(self):
        return XDW_DOCUMENT_TYPE[self.type]
