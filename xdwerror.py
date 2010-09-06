#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""xdwerror.py -- DocuWorks errors

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""


XDW_E_NOT_INSTALLED             = 0x80040001
XDW_E_INFO_NOT_FOUND            = 0x80040002
XDW_E_INSUFFICIENT_BUFFER       = 0x8007007A
XDW_E_FILE_NOT_FOUND            = 0x80070002
XDW_E_FILE_EXISTS               = 0x80070050
XDW_E_ACCESSDENIED              = 0x80070005
XDW_E_BAD_FORMAT                = 0x8007000B
XDW_E_OUTOFMEMORY               = 0x8007000E
XDW_E_WRITE_FAULT               = 0x8007001D
XDW_E_SHARING_VIOLATION         = 0x80070020
XDW_E_DISK_FULL                 = 0x80070027
XDW_E_INVALIDARG                = 0x80070057
XDW_E_INVALID_NAME              = 0x8007007B
XDW_E_INVALID_ACCESS            = 0x80040003
XDW_E_INVALID_OPERATION         = 0x80040004
XDW_E_NEWFORMAT                 = 0x800E0004
XDW_E_BAD_NETPATH               = 0x800E0005
XDW_E_APPLICATION_FAILED        = 0x80001156
XDW_E_SIGNATURE_MODULE          = 0x800E0010
XDW_E_PROTECT_MODULE            = 0x800E0012
XDW_E_UNEXPECTED                = 0x8000FFFF
XDW_E_CANCELED                  = 0x80040005
XDW_E_ANNOTATION_NOT_ACCEPTED   = 0x80040006

XDW_ERROR_MESSAGES = {
    XDW_E_NOT_INSTALLED:            "XDW_E_NOT_INSTALLED",
    XDW_E_INFO_NOT_FOUND:           "XDW_E_INFO_NOT_FOUND",
    XDW_E_INSUFFICIENT_BUFFER:      "XDW_E_INSUFFICIENT_BUFFER",
    XDW_E_FILE_NOT_FOUND:           "XDW_E_FILE_NOT_FOUND",
    XDW_E_FILE_EXISTS:              "XDW_E_FILE_EXISTS",
    XDW_E_ACCESSDENIED:             "XDW_E_ACCESSDENIED",
    XDW_E_BAD_FORMAT:               "XDW_E_BAD_FORMAT",
    XDW_E_OUTOFMEMORY:              "XDW_E_OUTOFMEMORY",
    XDW_E_WRITE_FAULT:              "XDW_E_WRITE_FAULT",
    XDW_E_SHARING_VIOLATION:        "XDW_E_SHARING_VIOLATION",
    XDW_E_DISK_FULL:                "XDW_E_DISK_FULL",
    XDW_E_INVALIDARG:               "XDW_E_INVALIDARG",
    XDW_E_INVALID_NAME:             "XDW_E_INVALID_NAME",
    XDW_E_INVALID_ACCESS:           "XDW_E_INVALID_ACCESS",
    XDW_E_INVALID_OPERATION:        "XDW_E_INVALID_OPERATION",
    XDW_E_NEWFORMAT:                "XDW_E_NEWFORMAT",
    XDW_E_BAD_NETPATH:              "XDW_E_BAD_NETPATH",
    XDW_E_APPLICATION_FAILED:       "XDW_E_APPLICATION_FAILED",
    XDW_E_SIGNATURE_MODULE:         "XDW_E_SIGNATURE_MODULE",
    XDW_E_PROTECT_MODULE:           "XDW_E_PROTECT_MODULE",
    XDW_E_UNEXPECTED:               "XDW_E_UNEXPECTED",
    XDW_E_CANCELED:                 "XDW_E_CANCELED",
    XDW_E_ANNOTATION_NOT_ACCEPTED:  "XDW_E_ANNOTATION_NOT_ACCEPTED",
    }


class XDWError(Exception):

    def __init__(self, error_code):
        self.error_code = error_code
        error_code = (error_code + 0x100000000) & 0xffffffff
        msg = XDW_ERROR_MESSAGES.get(error_code, "XDW_E_UNDEFINED")
        Exception.__init__(self, "%s (%08X)" % (msg, error_code))
