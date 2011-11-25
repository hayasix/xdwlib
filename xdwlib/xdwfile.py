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


__all__ = ("XDWFile", "environ", "xdwopen", "VALID_DOCUMENT_HANDLES")


def environ(name=None):
    """DocuWorks environment information."""
    if name:
        value = XDW_GetInformation(XDW_ENVIRON.normalize(name))
        if name == XDW_ENVIRON[XDW_GI_DWDESK_FILENAME_DIGITS]:
            value = ord(value)
        return value
    values = dict()
    for k, v in XDW_ENVIRON.items():
        try:
            value = XDW_GetInformation(k)
            if k == XDW_GI_DWDESK_FILENAME_DIGITS:
                value = ord(value)
            values[v] = value
        except XDWError as e:
            if e.error_code == XDW_E_INFO_NOT_FOUND:
                continue
            else:
                raise
    return values


# The last resort to close documents in interactive session.
try:
    VALID_DOCUMENT_HANDLES
except NameError:
    VALID_DOCUMENT_HANDLES = []


def xdwopen(path, readonly=False, authenticate=True):
    """General opener"""
    from document import Document
    from binder import Binder
    XDW_TYPES = {".XDW": Document, ".XBD": Binder}
    ext = os.path.splitext(path)[1].upper()
    if ext not in XDW_TYPES:
        raise XDWError(XDW_E_INVALIDARG)
    return XDW_TYPES[ext](path, readonly=readonly, authenticate=authenticate)


def create_sfx(input_path, output_path=None):
    """Create self-extract executable file.

    Returns path;  if no path is given, this method creates a temporary
    file somewhere and returns its path.  You have to remove the temporary
    file after use.
    """
    output_path = os.path.splitext(output_path or input_path)[0] + ".exe"
    XDW_CreateSfxDocument(input_path, output_path)
    return output_path


def extract_sfx(input_path, output_path=None):
    """Extract DocuWorks document/binder from self-extract executable file.

    Returns path;  if no path is given, this method creates a temporary
    file somewhere and returns its path.  You have to remove the temporary
    file after use.
    """
    root = os.path.splitext(output_path or input_path)[0]
    output_path = root + ".xdw"  # for now
    XDW_CreateSfxDocument(input_path, output_path)
    # Created file can be either document or binder.  We have to examine
    # which type of file was generated and rename if needed.
    doc = xdwopen(output_path, readonly=True)
    doctype = doc.type
    doc.close()
    if doctype == XDW_DT_BINDER:
        orig, output_path = output_path, root + ".xbd"
        os.rename(orig, output_path)
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
        path = os.path.abspath(path)
        self.handle = XDW_OpenDocumentHandle(path, open_mode)
        self.register()
        self.dir, self.name = os.path.split(path)
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
            XDW_Finalize()
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
        """DocuWorks file type, document or binder."""
        return XDW_DOCUMENT_TYPE[self.type]

    def insert_image(self, pos, input_path,
            fitimage=XDW_CREATE_FITDEF,
            compress=XDW_COMPRESS_NORMAL,
            zoom=0,  # %; 0=100%
            size=Point(0, 0),  # Point(width, height); 0=A4
            align=("center", "center"),  # left/center/right, top/center/bottom
            maxpapersize=XDW_CREATE_DEFAULT_SIZE,
            ):
        """Insert pages created from image files."""
        opt = XDW_CREATE_OPTION_EX2()
        opt.nFitImage = XDW_CREATE_FITIMAGE.normalize(fitimage)
        opt.nCompress = XDW_COMPRESS.normalize(compress)
        #opt.nZoom = 0
        opt.nZoomDetail = int(zoom * 1000)  # .3f
        # NB. Width and height are valid only for XDW_CREATE_USERDEF(_FIT).
        opt.nWidth, opt.nHeight = int(size * 100)  # .2f;
        opt.nHorPos = XDW_CREATE_HPOS.normalize(align[0])
        opt.nVerPos = XDW_CREATE_VPOS.normalize(align[1])
        opt.nMaxPaperSize = XDW_CREATE_MAXPAPERSIZE.normalize(maxpapersize)
        XDW_CreateXdwFromImageFileAndInsertDocument(
                self.handle, pos + 1, input_path, opt))
