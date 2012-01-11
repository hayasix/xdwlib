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
import shutil
import atexit

from xdwapi import *
from common import *
from struct import Point


__all__ = (
        "XDWFile", "PageForm",
        "xdwopen", "create_sfx", "extract_sfx", "optimize", "copy",
        "VALID_DOCUMENT_HANDLES", "close_all",
        )


# The last resort to close documents in interactive session.
try:
    VALID_DOCUMENT_HANDLES
except NameError:
    VALID_DOCUMENT_HANDLES = []


@atexit.register
def atexithandler():
    """Close all files and perform finalization before finishing process."""
    for handle in VALID_DOCUMENT_HANDLES:
        try:
            XDW_CloseDocumentHandle(handle)
        except:
            continue
        VALID_DOCUMENT_HANDLES.remove(handle)
    XDW_Finalize()


def xdwopen(path, readonly=False, authenticate=True):
    """General opener.  Returns Document or Binder object."""
    from document import Document
    from binder import Binder
    path = cp(path)
    XDW_TYPES = {".XDW": Document, ".XBD": Binder}
    ext = os.path.splitext(path)[1].upper()
    if ext not in XDW_TYPES:
        raise BadFormatError("extension must be .xdw or .xbd")
    return XDW_TYPES[ext](path, readonly=readonly, authenticate=authenticate)


def create_sfx(input_path, output_path=None):
    """Create self-extract executable file.

    Returns pathname of generated sfx executable file.
    """
    input_path, output_path = cp(input_path), cp(output_path)
    output_path = os.path.splitext(output_path or input_path)[0] + ".exe"
    XDW_CreateSfxDocument(input_path, output_path)
    return output_path


def extract_sfx(input_path, output_path=None):
    """Extract DocuWorks document/binder from self-extract executable file.

    Returns pathname of generated document/binder file.
    """
    input_path, output_path = cp(input_path), cp(output_path)
    root = os.path.splitext(output_path or input_path)[0]
    output_path = root + ".xdw"  # for now
    XDW_ExtractFromSfxDocument(input_path, output_path)
    # Created file can be either document or binder.  We have to examine
    # which type of file was generated and rename if needed.
    xdwfile = xdwopen(output_path, readonly=True)
    doctype = xdwfile.type
    xdwfile.close()
    if doctype == XDW_DT_BINDER:
        orig, output_path = output_path, root + ".xbd"
        os.rename(orig, output_path)
    return output_path


def optimize(input_path, output_path=None):
    """Optimize document/binder file.

    Returns pathname of optimized document/binder file.
    """
    input_path, output_path = cp(input_path), cp(output_path)
    output_path = derivative_path(output_path or input_path)
    XDW_OptimizeDocument(input_path, output_path)
    return output_path


def copy(input_path, output_path=None):
    """Copy DocuWorks document/binder to another one.

    Returns pathname of copied file.
    """
    input_path, output_path = cp(input_path), cp(output_path)
    output_path = derivative_path(output_path or input_path)
    shutil.copyfile(input_path, output_path)
    return output_path


class XDWFile(object):

    """Docuworks file, XDW or XBD."""

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
        path = cp(path)
        self.handle = XDW_OpenDocumentHandle(path, open_mode)
        self.register()
        self.dir, self.name = os.path.split(path)
        self.name = os.path.splitext(self.name)[0]
        # Set document properties.
        document_info = XDW_GetDocumentInformation(self.handle)
        self.pages = document_info.nPages
        self.version = document_info.nVersion - 3  # DocuWorks version
        self.original_data = document_info.nOriginalData
        self.type = XDW_DOCUMENT_TYPE[document_info.nDocType]
        self.editable = bool(document_info.nPermission & XDW_PERM_DOC_EDIT)
        self.annotatable = bool(document_info.nPermission & XDW_PERM_ANNO_EDIT)
        self.printable = bool(document_info.nPermission & XDW_PERM_PRINT)
        self.copyable = bool(document_info.nPermission & XDW_PERM_COPY)
        self.show_annotations = bool(document_info.nShowAnnotations)
        # Followings are effective only for binders.
        self.documents = document_info.nDocuments
        self.binder_color = XDW_BINDER_COLOR[document_info.nBinderColor]
        self.binder_size = XDW_BINDER_SIZE[document_info.nBinderSize]
        # Document attributes.
        self.attributes = XDW_GetDocumentAttributeNumber(self.handle)

    def update_pages(self):
        """Update number of pages; used after insert multiple pages in."""
        document_info = XDW_GetDocumentInformation(self.handle)
        self.pages = document_info.nPages

    def save(self):
        """Save document regardless of whether it is modified or not."""
        XDW_SaveDocument(self.handle)

    def close(self):
        """Close document."""
        XDW_CloseDocumentHandle(self.handle)
        self.free()

    def __getattr__(self, name):
        name = unicode(name)
        attribute_name = inner_attribute_name(name)
        try:
            return XDW_GetDocumentAttributeByNameW(
                    self.handle, attribute_name, codepage=CP)[1]
        except InvalidArgError as e:
            pass
        return self.__dict__[name]

    def __setattr__(self, name, value):
        if name == "show_annotations":
            XDW_ShowOrHideAnnotations(self.handle, bool(value))
            return
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

    def pageform(self, form):
        return PageForm(self, form)


class PageForm(object):

    def __init__(self, xdwfile, form):
        self.xdwfile = xdwfile
        self.form = XDW_PAGEFORM.normalize(inner_attribute_name(form))

    def __setattr__(self, name, value):
        attrname = inner_attribute_name(name)
        if name == "xdwfile":
            self.__dict__[name] = value
            return
        elif name == "form":
            self.__dict__[name] = XDW_PAGEFORM.normalize(value)
            return
        special = isinstance(XDW_ANNOTATION_ATTRIBUTE[attrname][1], XDWConst)
        if special or isinstance(value, (int, float)):
            value = int(scale(attrname, value, store=True))
            value = byref(c_int(value))
            attribute_type = XDW_ATYPE_INT  # TODO: Scaling may be required.
        elif isinstance(value, basestring):
            attribute_type = XDW_ATYPE_STRING
            """TODO: unicode handling.
            Currently Author has no idea to take unicode with ord < 256.
            Python's unicode may have inner representation with 0x00,
            eg.  0x41 0x00 0x42 0x00 0x43 0x00 for "ABC".  This results in
            unexpected string termination eg. "ABC" -> "A".  So, if the next
            if-block is not placed, you will get much more but inexact
            elements in result for abbreviated search string.
            """
            if isinstance(value, unicode):
                value = value.encode(CODEPAGE)  # TODO: how can we take all unicodes?
            if 255 < len(value):
                raise ValueError("text length must be <= 255")
        # TODO: XDW_ATYPE_OTHER should also be valid.
        else:
            raise TypeError("illegal value " + repr(value))
        XDW_SetPageFormAttribute(
                self.__dict__["xdwfile"].handle,
                self.__dict__["form"],
                attrname, attribute_type, value)

    def __getattr__(self, name):
        if name in ("xdwfile", "form"):
            return self.__dict__[name]
        attrname = inner_attribute_name(name)
        value = XDW_GetPageFormAttribute(
                self.__dict__["xdwfile"].handle,
                self.__dict__["form"], attrname)
        attribute_type = XDW_ANNOTATION_ATTRIBUTE[attrname][0]
        if attribute_type == 1:  # string
            return unicode(value, CODEPAGE)
        value = unpack(value)
        return scale(attrname, value, store=False)

    def update(self, sync=False):
        """Update page form.

        sync    (bool) also update pageforms for documents in binder
        """
        sync = XDW_PAGEFORM_REMOVE if sync else XDW_PAGEFORM_STAY
        XDW_UpdatePageForm(self.xdwfile.handle, sync)

    def delete(self, sync=False):
        """delete page form.

        sync    (bool) also delete pageforms for documents in binder
        """
        sync = XDW_PAGEFORM_REMOVE if sync else XDW_PAGEFORM_STAY
        XDW_RemovePageForm(self.xdwfile.handle, sync)
