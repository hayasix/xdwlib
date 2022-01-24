#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix :

"""xdwapi.py -- raw DocuWorks API

Copyright (C) 2010 HAYASHI Hideki <hideki@hayasix.com>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""


from ctypes import *

from .bitmap import Bitmap


### SETUP ############################################################

DLL = windll.LoadLibrary("xdwapi.dll")
CP = cdll.kernel32.GetACP()

# Get XDW VERSION.
size = DLL.XDW_GetInformation(1, None, 0, None)
buf = create_string_buffer(size)
size = DLL.XDW_GetInformation(1, byref(buf), size, None)
XDW_VERSION = buf.value.decode("ascii")
XDWVER = int(XDW_VERSION.split(".")[0])

# Stop running immediately if the fatal version is running.
if XDW_VERSION == "8.0.3":
    raise SystemExit("""\
THIS VERSION OF DOCUWORKS HAS A FATAL ERROR THAT MAY CAUSE MASSIVE DATA LOSS.
CONSULT YOUR SYSTEM ADMINISTRATOR AS SOON AS POSSIBLE.
PROGRAM STOPS RUNNING TO AVOID ANY ACCIDENT.""")

# Check if embedded OCR engine is available.
if XDWVER < 9:
    OCRENABLED = True
else:  # if 9 <= XDWVER:
    OCRENABLED = (DLL.XDW_GetInformation(15, None, 0, None) == 0)


######################################################################
### ERROR DEFINITIONS ################################################


def _uint32(n):
    return (n + 0x100000000) & 0xffffffff


def _int32(n):
    return n - 0x100000000 if 0x80000000 <= n else n


XDW_E_NOT_INSTALLED                 = _int32(0x80040001)
XDW_E_INFO_NOT_FOUND                = _int32(0x80040002)
XDW_E_INSUFFICIENT_BUFFER           = _int32(0x8007007A)
XDW_E_FILE_NOT_FOUND                = _int32(0x80070002)
XDW_E_FILE_EXISTS                   = _int32(0x80070050)
XDW_E_ACCESSDENIED                  = _int32(0x80070005)
XDW_E_BAD_FORMAT                    = _int32(0x8007000B)
XDW_E_OUTOFMEMORY                   = _int32(0x8007000E)
XDW_E_WRITE_FAULT                   = _int32(0x8007001D)
XDW_E_SHARING_VIOLATION             = _int32(0x80070020)
XDW_E_DISK_FULL                     = _int32(0x80070027)
XDW_E_INVALIDARG                    = _int32(0x80070057)
XDW_E_INVALID_NAME                  = _int32(0x8007007B)
XDW_E_INVALID_ACCESS                = _int32(0x80040003)
XDW_E_INVALID_OPERATION             = _int32(0x80040004)
XDW_E_NEWFORMAT                     = _int32(0x800E0004)
XDW_E_BAD_NETPATH                   = _int32(0x800E0005)
XDW_E_APPLICATION_FAILED            = _int32(0x80001156)
XDW_E_SIGNATURE_MODULE              = _int32(0x800E0010)
XDW_E_PROTECT_MODULE                = _int32(0x800E0012)
XDW_E_UNEXPECTED                    = _int32(0x8000FFFF)
XDW_E_CANCELED                      = _int32(0x80040005)
XDW_E_ANNOTATION_NOT_ACCEPTED       = _int32(0x80040006)

XDW_ERROR_MESSAGES = {
        XDW_E_NOT_INSTALLED             : "XDW_E_NOT_INSTALLED",
        XDW_E_INFO_NOT_FOUND            : "XDW_E_INFO_NOT_FOUND",
        XDW_E_INSUFFICIENT_BUFFER       : "XDW_E_INSUFFICIENT_BUFFER",
        XDW_E_FILE_NOT_FOUND            : "XDW_E_FILE_NOT_FOUND",
        XDW_E_FILE_EXISTS               : "XDW_E_FILE_EXISTS",
        XDW_E_ACCESSDENIED              : "XDW_E_ACCESSDENIED",
        XDW_E_BAD_FORMAT                : "XDW_E_BAD_FORMAT",
        XDW_E_OUTOFMEMORY               : "XDW_E_OUTOFMEMORY",
        XDW_E_WRITE_FAULT               : "XDW_E_WRITE_FAULT",
        XDW_E_SHARING_VIOLATION         : "XDW_E_SHARING_VIOLATION",
        XDW_E_DISK_FULL                 : "XDW_E_DISK_FULL",
        XDW_E_INVALIDARG                : "XDW_E_INVALIDARG",
        XDW_E_INVALID_NAME              : "XDW_E_INVALID_NAME",
        XDW_E_INVALID_ACCESS            : "XDW_E_INVALID_ACCESS",
        XDW_E_INVALID_OPERATION         : "XDW_E_INVALID_OPERATION",
        XDW_E_NEWFORMAT                 : "XDW_E_NEWFORMAT",
        XDW_E_BAD_NETPATH               : "XDW_E_BAD_NETPATH",
        XDW_E_APPLICATION_FAILED        : "XDW_E_APPLICATION_FAILED",
        XDW_E_SIGNATURE_MODULE          : "XDW_E_SIGNATURE_MODULE",
        XDW_E_PROTECT_MODULE            : "XDW_E_PROTECT_MODULE",
        XDW_E_UNEXPECTED                : "XDW_E_UNEXPECTED",
        XDW_E_CANCELED                  : "XDW_E_CANCELED",
        XDW_E_ANNOTATION_NOT_ACCEPTED   : "XDW_E_ANNOTATION_NOT_ACCEPTED",
        }


class XDWError(Exception):

    def __init__(self, message=""):
        Exception.__init__(self, message)
        self.code = self.__class__.e
        major = XDW_ERROR_MESSAGES.get(self.code, "XDW_E_UNDEFINED")
        if message:
            self.message = "{0} ({1:08X}) {2}".format(major, _uint32(self.code),
                                                      message)
        else:
            self.message = "{0} ({1:08X})".format(major, _uint32(self.code))

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message


class NotInstalledError(XDWError): e = XDW_E_NOT_INSTALLED
class InfoNotFoundError(XDWError): e = XDW_E_INFO_NOT_FOUND
class InsufficientBufferError(XDWError): e = XDW_E_INSUFFICIENT_BUFFER
class FileNotFoundError(XDWError): e = XDW_E_FILE_NOT_FOUND
class FileExistsError(XDWError): e = XDW_E_FILE_EXISTS
class AccessDeniedError(XDWError): e = XDW_E_ACCESSDENIED
class BadFormatError(XDWError): e = XDW_E_BAD_FORMAT
class OutOfMemoryError(XDWError): e = XDW_E_OUTOFMEMORY
class WriteFaultError(XDWError): e = XDW_E_WRITE_FAULT
class SharingViolationError(XDWError): e = XDW_E_SHARING_VIOLATION
class DiskFullError(XDWError): e = XDW_E_DISK_FULL
class InvalidArgError(XDWError): e = XDW_E_INVALIDARG
class InvalidNameError(XDWError): e = XDW_E_INVALID_NAME
class InvalidAccessError(XDWError): e = XDW_E_INVALID_ACCESS
class InvalidOperationError(XDWError): e = XDW_E_INVALID_OPERATION
class NewFormatError(XDWError): e = XDW_E_NEWFORMAT
class BadNetPathError(XDWError): e = XDW_E_BAD_NETPATH
class ApplicationFailedError(XDWError): e = XDW_E_APPLICATION_FAILED
class SignatureModuleError(XDWError): e = XDW_E_SIGNATURE_MODULE
class ProtectModuleError(XDWError): e = XDW_E_PROTECT_MODULE
class UnexpectedError(XDWError): e = XDW_E_UNEXPECTED
class CancelledError(XDWError): e = XDW_E_CANCELED
class AnnotationNotAcceptedError(XDWError): e = XDW_E_ANNOTATION_NOT_ACCEPTED

class UndefinedError(XDWError): e = _int32(0x8000fffe)

XDW_ERROR_CLASSES = {
        XDW_E_NOT_INSTALLED             : NotInstalledError,
        XDW_E_INFO_NOT_FOUND            : InfoNotFoundError,
        XDW_E_INSUFFICIENT_BUFFER       : InsufficientBufferError,
        XDW_E_FILE_NOT_FOUND            : FileNotFoundError,
        XDW_E_FILE_EXISTS               : FileExistsError,
        XDW_E_ACCESSDENIED              : AccessDeniedError,
        XDW_E_BAD_FORMAT                : BadFormatError,
        XDW_E_OUTOFMEMORY               : OutOfMemoryError,
        XDW_E_WRITE_FAULT               : WriteFaultError,
        XDW_E_SHARING_VIOLATION         : SharingViolationError,
        XDW_E_DISK_FULL                 : DiskFullError,
        XDW_E_INVALIDARG                : InvalidArgError,
        XDW_E_INVALID_NAME              : InvalidNameError,
        XDW_E_INVALID_ACCESS            : InvalidAccessError,
        XDW_E_INVALID_OPERATION         : InvalidOperationError,
        XDW_E_NEWFORMAT                 : NewFormatError,
        XDW_E_BAD_NETPATH               : BadNetPathError,
        XDW_E_APPLICATION_FAILED        : ApplicationFailedError,
        XDW_E_SIGNATURE_MODULE          : SignatureModuleError,
        XDW_E_PROTECT_MODULE            : ProtectModuleError,
        XDW_E_UNEXPECTED                : UnexpectedError,
        XDW_E_CANCELED                  : CancelledError,
        XDW_E_ANNOTATION_NOT_ACCEPTED   : AnnotationNotAcceptedError,
        }

def XDWErrorFactory(errorcode, message=""):
    return XDW_ERROR_CLASSES.get(errorcode, UndefinedError)(message)


######################################################################
### CONSTANTS ########################################################

NULL = None



class XDWConst(dict):

    def __init__(self, constants, default=None):
        dict.__init__(self, constants)
        self.constants = constants
        self.reverse = dict((v, k) for (k, v) in constants.items())
        self.default = default

    def inner(self, value):
        return self.reverse.get(str(value).upper(), self.default)

    def normalize(self, key_or_value):
        if isinstance(key_or_value, (str, bytes)):
            return self.inner(key_or_value)
        return key_or_value


### Environment

XDW_GI_VERSION                      =  1
XDW_GI_INSTALLPATH                  =  2
XDW_GI_BINPATH                      =  3
XDW_GI_PLUGINPATH                   =  4
XDW_GI_FOLDERROOTPATH               =  5
XDW_GI_USERFOLDERPATH               =  6
XDW_GI_SYSTEMFOLDERPATH             =  7
XDW_GI_RECEIVEFOLDERPATH            =  8
XDW_GI_SENDFOLDERPATH               =  9
XDW_GI_DWINPUTPATH                  = 10
XDW_GI_DWDESKPATH                   = 11
XDW_GI_DWVIEWERPATH                 = 12
XDW_GI_DWVLTPATH                    = 13
XDW_GI_TASKSPACEPATH                = 14
XDW_GI_OCRENABLER_STATE             = 15
XDW_GI_DWDESK_FILENAME_DELIMITER    = 1001
XDW_GI_DWDESK_FILENAME_DIGITS       = 1002

XDW_ENVIRON = XDWConst({
        XDW_GI_VERSION                  : "VERSION",
        XDW_GI_INSTALLPATH              : "INSTALLPATH",
        XDW_GI_BINPATH                  : "BINPATH",
        XDW_GI_PLUGINPATH               : "PLUGINPATH",
        XDW_GI_FOLDERROOTPATH           : "FOLDERROOTPATH",
        XDW_GI_USERFOLDERPATH           : "USERFOLDERPATH",
        XDW_GI_SYSTEMFOLDERPATH         : "SYSTEMFOLDERPATH",
        XDW_GI_RECEIVEFOLDERPATH        : "RECEIVEFOLDERPATH",
        XDW_GI_SENDFOLDERPATH           : "SENDFOLDERPATH",
        XDW_GI_DWINPUTPATH              : "DWINPUTPATH",
        XDW_GI_DWDESKPATH               : "DWDESKPATH",
        XDW_GI_DWVIEWERPATH             : "DWVIEWERPATH",
        XDW_GI_DWVLTPATH                : "DWVLTPATH",
        XDW_GI_TASKSPACEPATH            : "TASKSPACEPATH",
        XDW_GI_OCRENABLER_STATE         : "OCRENABLER_STATE",
        XDW_GI_DWDESK_FILENAME_DELIMITER: "DWDESK_FILENAME_DELIMITER",
        XDW_GI_DWDESK_FILENAME_DIGITS   : "DWDESK_FILENAME_DIGITS",
        })

XDW_MAXPATH                         = 255
XDW_MAXINPUTIMAGEPATH               = 127

### Common

XDW_COMPRESS_NORMAL                 = 0
XDW_COMPRESS_LOSSLESS               = 1
XDW_COMPRESS_HIGHQUALITY            = 2
XDW_COMPRESS_HIGHCOMPRESS           = 3
XDW_COMPRESS_NOCOMPRESS             = 4
XDW_COMPRESS_JPEG                   = 5
XDW_COMPRESS_PACKBITS               = 6
XDW_COMPRESS_G4                     = 7
XDW_COMPRESS_MRC_NORMAL             = 8
XDW_COMPRESS_MRC_HIGHQUALITY        = 9
XDW_COMPRESS_MRC_HIGHCOMPRESS       = 10
XDW_COMPRESS_MRC                    = 11
XDW_COMPRESS_JPEG_TTN2              = 12

XDW_COMPRESS = XDWConst({
        XDW_COMPRESS_NORMAL                 : "NORMAL",
        XDW_COMPRESS_LOSSLESS               : "LOSSLESS",
        XDW_COMPRESS_HIGHQUALITY            : "HIGHQUALITY",
        XDW_COMPRESS_HIGHCOMPRESS           : "HIGHCOMPRESS",
        XDW_COMPRESS_NOCOMPRESS             : "NOCOMPRESS",
        XDW_COMPRESS_JPEG                   : "JPEG",
        XDW_COMPRESS_PACKBITS               : "PACKBITS",
        XDW_COMPRESS_G4                     : "G4",
        XDW_COMPRESS_MRC_NORMAL             : "MRC_NORMAL",
        XDW_COMPRESS_MRC_HIGHQUALITY        : "MRC_HIGHQUALITY",
        XDW_COMPRESS_MRC_HIGHCOMPRESS       : "MRC_HIGHCOMPRESS",
        XDW_COMPRESS_MRC                    : "MRC",
        XDW_COMPRESS_JPEG_TTN2              : "JPEG_TTN2",
        }, default=XDW_COMPRESS_NORMAL)

XDW_CONVERT_MRC_ORIGINAL            = 0
XDW_CONVERT_MRC_OS                  = 1

XDW_CONVERT_MRC = XDWConst({
        XDW_CONVERT_MRC_ORIGINAL    : "ORIGINAL",
        XDW_CONVERT_MRC_OS          : "OS",
        }, default=XDW_CONVERT_MRC_ORIGINAL)

XDW_IMAGE_DIB                       = 0
XDW_IMAGE_TIFF                      = 1
XDW_IMAGE_JPEG                      = 2
XDW_IMAGE_PDF                       = 3

XDW_IMAGE_FORMAT = XDWConst({
        XDW_IMAGE_DIB               : "BMP",
        XDW_IMAGE_TIFF              : "TIFF",
        XDW_IMAGE_JPEG              : "JPEG",
        XDW_IMAGE_PDF               : "PDF",
        }, default=XDW_IMAGE_DIB)

XDW_TEXT_UNKNOWN                    = 0
XDW_TEXT_MULTIBYTE                  = 1
XDW_TEXT_UNICODE                    = 2
XDW_TEXT_UNICODE_IFNECESSARY        = 3

XDW_TEXT_TYPE = XDWConst({
        XDW_TEXT_UNKNOWN            : "UNKNOWN",
        XDW_TEXT_MULTIBYTE          : "MULTIBYTE",
        XDW_TEXT_UNICODE            : "UNICODE",
        XDW_TEXT_UNICODE_IFNECESSARY: "UNICODE_IFNECESSARY",
        }, default=XDW_TEXT_UNKNOWN)

### Document/Binder related

XDW_DT_DOCUMENT                     = 0
XDW_DT_BINDER                       = 1
XDW_DT_CONTAINER                    = 2

XDW_DOCUMENT_TYPE = XDWConst({
        XDW_DT_DOCUMENT             : "DOCUMENT",
        XDW_DT_BINDER               : "BINDER",
        XDW_DT_CONTAINER            : "CONTAINER",
        }, default=XDW_DT_DOCUMENT)


# open/create

XDW_OPEN_READONLY                   = 0
XDW_OPEN_UPDATE                     = 1

XDW_AUTH_NONE                       = 0
XDW_AUTH_NODIALOGUE                 = 1
XDW_AUTH_CONDITIONAL_DIALOGUE       = 2

XDW_AUTH = XDWConst({
        XDW_AUTH_NONE                   : "NONE",
        XDW_AUTH_NODIALOGUE             : "NODIALOGUE",
        XDW_AUTH_CONDITIONAL_DIALOGUE   : "CONDITIONAL",
        }, default=XDW_AUTH_NONE)

XDW_PERM_DOC_EDIT                   = 0x02
XDW_PERM_ANNO_EDIT                  = 0x04
XDW_PERM_PRINT                      = 0x08
XDW_PERM_COPY                       = 0x10

XDW_PERM = XDWConst({
        XDW_PERM_DOC_EDIT           : "EDIT_DOCUMENT",
        XDW_PERM_ANNO_EDIT          : "EDIT_ANNOTATION",
        XDW_PERM_PRINT              : "PRINT",
        XDW_PERM_COPY               : "COPY",
        })

XDW_CREATE_FITDEF                   = 0
XDW_CREATE_FIT                      = 1
XDW_CREATE_USERDEF                  = 2
XDW_CREATE_USERDEF_FIT              = 3
XDW_CREATE_FITDEF_DIVIDEBMP         = 4

XDW_CREATE_FITIMAGE = XDWConst({
        XDW_CREATE_FITDEF           : "FITDEF",
        XDW_CREATE_FIT              : "FIT",
        XDW_CREATE_USERDEF          : "USERDEF",
        XDW_CREATE_USERDEF_FIT      : "USERDEF_FIT",
        XDW_CREATE_FITDEF_DIVIDEBMP : "FITDEF_DIVIDEBMP",
        })

XDW_CREATE_HCENTER                  = 0
XDW_CREATE_LEFT                     = 1
XDW_CREATE_RIGHT                    = 2

XDW_CREATE_HPOS = XDWConst({
        XDW_CREATE_HCENTER          : "CENTER",
        XDW_CREATE_LEFT             : "LEFT",
        XDW_CREATE_RIGHT            : "RIGHT",
        }, default=XDW_CREATE_HCENTER)

XDW_CREATE_VCENTER                  = 0
XDW_CREATE_TOP                      = 1
XDW_CREATE_BOTTOM                   = 2

XDW_CREATE_VPOS = XDWConst({
        XDW_CREATE_VCENTER          : "CENTER",
        XDW_CREATE_TOP              : "TOP",
        XDW_CREATE_BOTTOM           : "BOTTOM",
        }, default=XDW_CREATE_VCENTER)

XDW_CREATE_DEFAULT_SIZE             = 0
XDW_CREATE_A3_SIZE                  = 1
XDW_CREATE_2A0_SIZE                 = 2

XDW_CREATE_MAXPAPERSIZE = XDWConst({
        XDW_CREATE_DEFAULT_SIZE     : "DEFAULT",
        XDW_CREATE_A3_SIZE          : "A3",
        XDW_CREATE_2A0_SIZE         : "2A0",
        }, default=XDW_CREATE_DEFAULT_SIZE)

XDW_CRTP_BEGINNING                  = 1
XDW_CRTP_PRINTING                   = 2
XDW_CRTP_PAGE_CREATING              = 3
XDW_CRTP_ORIGINAL_APPENDING         = 4
XDW_CRTP_WRITING                    = 5
XDW_CRTP_ENDING                     = 6
XDW_CRTP_CANCELING                  = 7
XDW_CRTP_FINISHED                   = 8
XDW_CRTP_CANCELED                   = 9

XDW_CREATE_PHASE = XDWConst({
        XDW_CRTP_BEGINNING          : "INITIALIZING",
        XDW_CRTP_PRINTING           : "PRINTING",
        XDW_CRTP_PAGE_CREATING      : "GENERATING",
        XDW_CRTP_ORIGINAL_APPENDING : "ATTACHING",
        XDW_CRTP_WRITING            : "WRITING",
        XDW_CRTP_ENDING             : "FINISHING",
        XDW_CRTP_CANCELING          : "CANCELLING",
        XDW_CRTP_FINISHED           : "FINISHED",
        XDW_CRTP_CANCELED           : "CANCELLED",
        })

# size

XDW_SIZE_FREE                       = 0
XDW_SIZE_A3_PORTRAIT                = 1
XDW_SIZE_A3_LANDSCAPE               = 2
XDW_SIZE_A4_PORTRAIT                = 3
XDW_SIZE_A4_LANDSCAPE               = 4
XDW_SIZE_A5_PORTRAIT                = 5
XDW_SIZE_A5_LANDSCAPE               = 6
XDW_SIZE_B4_PORTRAIT                = 7
XDW_SIZE_B4_LANDSCAPE               = 8
XDW_SIZE_B5_PORTRAIT                = 9
XDW_SIZE_B5_LANDSCAPE               = 10

XDW_SIZE = XDWConst({
        XDW_SIZE_FREE               : "FREE",
        XDW_SIZE_A3_PORTRAIT        : "A3R",
        XDW_SIZE_A3_LANDSCAPE       : "A3",
        XDW_SIZE_A4_PORTRAIT        : "A4R",
        XDW_SIZE_A4_LANDSCAPE       : "A4",
        XDW_SIZE_A5_PORTRAIT        : "A5R",
        XDW_SIZE_A5_LANDSCAPE       : "A5",
        XDW_SIZE_B4_PORTRAIT        : "B4R",
        XDW_SIZE_B4_LANDSCAPE       : "B4",
        XDW_SIZE_B5_PORTRAIT        : "B5R",
        XDW_SIZE_B5_LANDSCAPE       : "B5",
        }, default=XDW_SIZE_A4_PORTRAIT)

XDW_SIZE_MM = {
        XDW_SIZE_FREE               : (0, 0),
        XDW_SIZE_A3_PORTRAIT        : (297, 420),
        XDW_SIZE_A3_LANDSCAPE       : (420, 297),
        XDW_SIZE_A4_PORTRAIT        : (210, 297),
        XDW_SIZE_A4_LANDSCAPE       : (297, 210),
        XDW_SIZE_A5_PORTRAIT        : (148, 210),
        XDW_SIZE_A5_LANDSCAPE       : (210, 148),
        XDW_SIZE_B4_PORTRAIT        : (257, 364),
        XDW_SIZE_B4_LANDSCAPE       : (364, 257),
        XDW_SIZE_B5_PORTRAIT        : (182, 257),
        XDW_SIZE_B5_LANDSCAPE       : (257, 182),
        }

# binder color

XDW_BINDER_COLOR_0                  = 0
XDW_BINDER_COLOR_1                  = 1
XDW_BINDER_COLOR_2                  = 2
XDW_BINDER_COLOR_3                  = 3
XDW_BINDER_COLOR_4                  = 4
XDW_BINDER_COLOR_5                  = 5
XDW_BINDER_COLOR_6                  = 6
XDW_BINDER_COLOR_7                  = 7
XDW_BINDER_COLOR_8                  = 8
XDW_BINDER_COLOR_9                  = 9
XDW_BINDER_COLOR_10                 = 10
XDW_BINDER_COLOR_11                 = 11
XDW_BINDER_COLOR_12                 = 12
XDW_BINDER_COLOR_13                 = 13
XDW_BINDER_COLOR_14                 = 14
XDW_BINDER_COLOR_15                 = 15

# succession

XDW_SUMMARY_INFO                    = 1
XDW_USER_DEF                        = 2
XDW_ANNOTATION                      = 4

# protection

XDW_PROTECT_NONE                    = 0
XDW_PROTECT_PSWD                    = 1
XDW_PROTECT_PSWD128                 = 3
XDW_PROTECT_PKI                     = 4
XDW_PROTECT_STAMP                   = 5
XDW_PROTECT_CONTEXT_SERVICE         = 6
XDW_PROTECT_PSWD256                 = 7
XDW_PROTECT_PKI256                  = 8

XDW_PROTECT = XDWConst({
        XDW_PROTECT_NONE            : "NONE",
        XDW_PROTECT_PSWD            : "PASSWORD",
        XDW_PROTECT_PSWD128         : "PASSWORD128",
        XDW_PROTECT_PKI             : "PKI",
        XDW_PROTECT_STAMP           : "STAMP",
        XDW_PROTECT_CONTEXT_SERVICE : "CONTEXT_SERVICE",
        XDW_PROTECT_PSWD256         : "PASSWORD256",
        XDW_PROTECT_PKI256          : "PKI256",
        }, default=XDW_PROTECT_NONE)

# signature

XDW_SIGNATURE_STAMP                                     = 100
XDW_SIGNATURE_PKI                                       = 102
XDW_SIGNATURE_PKI_SHA256                                = 105

XDW_SIGNATURE = XDWConst({
        XDW_SIGNATURE_STAMP                             : "STAMP",
        XDW_SIGNATURE_PKI                               : "PKI",
        })

XDW_SIGNATURE_STAMP_DOC_NONE                            = 0
XDW_SIGNATURE_STAMP_DOC_NOEDIT                          = 1
XDW_SIGNATURE_STAMP_DOC_EDIT                            = 2
XDW_SIGNATURE_STAMP_DOC_BAD                             = 3

XDW_SIGNATURE_STAMP_DOC = XDWConst({
        XDW_SIGNATURE_STAMP_DOC_NONE                    : "NONE",
        XDW_SIGNATURE_STAMP_DOC_NOEDIT                  : "NOEDIT",
        XDW_SIGNATURE_STAMP_DOC_EDIT                    : "EDIT",
        XDW_SIGNATURE_STAMP_DOC_BAD                     : "BAD",
        })

XDW_SIGNATURE_STAMP_STAMP_NONE                          = 0
XDW_SIGNATURE_STAMP_STAMP_TRUSTED                       = 1
XDW_SIGNATURE_STAMP_STAMP_NOTRUST                       = 2

XDW_SIGNATURE_STAMP_STAMP = XDWConst({
        XDW_SIGNATURE_STAMP_STAMP_NONE                  : "NONE",
        XDW_SIGNATURE_STAMP_STAMP_TRUSTED               : "TRUSTED",
        XDW_SIGNATURE_STAMP_STAMP_NOTRUST               : "NOTRUST",
        })

XDW_SIGNATURE_STAMP_ERROR_OK                            = 0
XDW_SIGNATURE_STAMP_ERROR_NO_OPENING_CASE               = 1
XDW_SIGNATURE_STAMP_ERROR_NO_SELFSTAMP                  = 2
XDW_SIGNATURE_STAMP_ERROR_OUT_OF_VALIDITY               = 3
XDW_SIGNATURE_STAMP_ERROR_INVALID_DATA                  = 4
XDW_SIGNATURE_STAMP_ERROR_OUT_OF_MEMORY                 = 100
XDW_SIGNATURE_STAMP_ERROR_UNKNOWN                       = 9999

XDW_SIGNATURE_STAMP_ERROR = XDWConst({
        XDW_SIGNATURE_STAMP_ERROR_OK                    : "OK",
        XDW_SIGNATURE_STAMP_ERROR_NO_OPENING_CASE       : "NO_OPENING_CASE",
        XDW_SIGNATURE_STAMP_ERROR_NO_SELFSTAMP          : "NO_SELFSTAMP",
        XDW_SIGNATURE_STAMP_ERROR_OUT_OF_VALIDITY       : "OUT_OF_VALIDITY",
        XDW_SIGNATURE_STAMP_ERROR_INVALID_DATA          : "INVALID_DATA",
        XDW_SIGNATURE_STAMP_ERROR_OUT_OF_MEMORY         : "OUT_OF_MEMORY",
        XDW_SIGNATURE_STAMP_ERROR_UNKNOWN               : "UNKNOWN",
        })

XDW_SIGNATURE_PKI_DOC_UNKNOWN                           = 0
XDW_SIGNATURE_PKI_DOC_GOOD                              = 1
XDW_SIGNATURE_PKI_DOC_MODIFIED                          = 2
XDW_SIGNATURE_PKI_DOC_BAD                               = 3
XDW_SIGNATURE_PKI_DOC_GOOD_TRUSTED                      = 4
XDW_SIGNATURE_PKI_DOC_MODIFIED_TRUSTED                  = 5

XDW_SIGNATURE_PKI_DOC = XDWConst({
        XDW_SIGNATURE_PKI_DOC_UNKNOWN                   : "UNKNOWN",
        XDW_SIGNATURE_PKI_DOC_GOOD                      : "GOOD",
        XDW_SIGNATURE_PKI_DOC_MODIFIED                  : "MODIFIED",
        XDW_SIGNATURE_PKI_DOC_BAD                       : "BAD",
        XDW_SIGNATURE_PKI_DOC_GOOD_TRUSTED              : "GOOD_TRUSTED",
        XDW_SIGNATURE_PKI_DOC_MODIFIED_TRUSTED          : "MODIFIED_TRUSTED",
        })

XDW_SIGNATURE_PKI_TYPE_LOW                              = 0
XDW_SIGNATURE_PKI_TYPE_MID_LOCAL                        = 1
XDW_SIGNATURE_PKI_TYPE_MID_NETWORK                      = 2
XDW_SIGNATURE_PKI_TYPE_HIGH_LOCAL                       = 3
XDW_SIGNATURE_PKI_TYPE_HIGH_NETWORK                     = 4

XDW_SIGNATURE_PKI_TYPE = XDWConst({
        XDW_SIGNATURE_PKI_TYPE_LOW                      : "LOW",
        XDW_SIGNATURE_PKI_TYPE_MID_LOCAL                : "MID_LOCAL",
        XDW_SIGNATURE_PKI_TYPE_MID_NETWORK              : "MID_NETWORK",
        XDW_SIGNATURE_PKI_TYPE_HIGH_LOCAL               : "HIGH_LOCAL",
        XDW_SIGNATURE_PKI_TYPE_HIGH_NETWORK             : "HIGH_NETWORK",
        })

XDW_SIGNATURE_PKI_CERT_UNKNOWN                          = 0
XDW_SIGNATURE_PKI_CERT_OK                               = 1
XDW_SIGNATURE_PKI_CERT_NO_ROOT_CERTIFICATE              = 2
XDW_SIGNATURE_PKI_CERT_NO_REVOCATION_CHECK              = 3
XDW_SIGNATURE_PKI_CERT_OUT_OF_VALIDITY                  = 4
XDW_SIGNATURE_PKI_CERT_OUT_OF_VALIDITY_AT_SIGNED_TIME   = 5
XDW_SIGNATURE_PKI_CERT_REVOKE_CERTIFICATE               = 6
XDW_SIGNATURE_PKI_CERT_REVOKE_INTERMEDIATE_CERTIFICATE  = 7
XDW_SIGNATURE_PKI_CERT_INVALID_SIGNATURE                = 8
XDW_SIGNATURE_PKI_CERT_INVALID_USAGE                    = 9
XDW_SIGNATURE_PKI_CERT_UNDEFINED_ERROR                  = 10

XDW_SIGNATURE_PKI_CERT = XDWConst({
        XDW_SIGNATURE_PKI_CERT_UNKNOWN                  : "UNKNOWN",
        XDW_SIGNATURE_PKI_CERT_OK                       : "OK",
        XDW_SIGNATURE_PKI_CERT_NO_ROOT_CERTIFICATE      : "NO_ROOT_CERTIFICATE",
        XDW_SIGNATURE_PKI_CERT_NO_REVOCATION_CHECK      : "NO_REVOCATION_CHECK",
        XDW_SIGNATURE_PKI_CERT_OUT_OF_VALIDITY          : "OUT_OF_VALIDITY",
        XDW_SIGNATURE_PKI_CERT_OUT_OF_VALIDITY_AT_SIGNED_TIME : "OUT_OF_VALIDITY_AT_SIGNED_TIME",
        XDW_SIGNATURE_PKI_CERT_REVOKE_CERTIFICATE       : "REVOKE_CERTIFICATE",
        XDW_SIGNATURE_PKI_CERT_REVOKE_INTERMEDIATE_CERTIFICATE : "REVOKE_INTERMEDIATE_CERTIFICATE",
        XDW_SIGNATURE_PKI_CERT_INVALID_SIGNATURE        : "INVALID_SIGNATURE",
        XDW_SIGNATURE_PKI_CERT_INVALID_USAGE            : "INVALID_USAGE",
        XDW_SIGNATURE_PKI_CERT_UNDEFINED_ERROR          : "UNDEFINED_ERROR",
        })

XDW_SIGNATURE_PKI_ERROR_UNKNOWN                         = 0
XDW_SIGNATURE_PKI_ERROR_OK                              = 1
XDW_SIGNATURE_PKI_ERROR_BAD_PLATFORM                    = 2
XDW_SIGNATURE_PKI_ERROR_WRITE_REG_ERROR                 = 3
XDW_SIGNATURE_PKI_ERROR_BAD_TRUST_LEVEL                 = 4
XDW_SIGNATURE_PKI_ERROR_BAD_REVOKE_CHECK_TYPE           = 5
XDW_SIGNATURE_PKI_ERROR_BAD_AUTO_IMPORT_CERT_FLAG       = 6
XDW_SIGNATURE_PKI_ERROR_BAD_SIGN_CONFIG                 = 7
XDW_SIGNATURE_PKI_ERROR_NO_IMAGE_FILE                   = 8
XDW_SIGNATURE_PKI_ERROR_BAD_SIGN_CERT                   = 9
XDW_SIGNATURE_PKI_ERROR_NO_SIGN_CERT                    = 10
XDW_SIGNATURE_PKI_ERROR_NOT_USE_PRIVATE_KEY             = 11
XDW_SIGNATURE_PKI_ERROR_INVALID                         = 12
XDW_SIGNATURE_PKI_ERROR_BAD_SIGN                        = 13
XDW_SIGNATURE_PKI_ERROR_REVOKE_CHECK_ERROR              = 14
XDW_SIGNATURE_PKI_ERROR_OUT_OF_VALIDITY                 = 15
XDW_SIGNATURE_PKI_ERROR_NO_CERT                         = 16
XDW_SIGNATURE_PKI_ERROR_FAILURE_IMPOPT_CERT             = 17
XDW_SIGNATURE_PKI_ERROR_NO_ROOT_CERT                    = 18
XDW_SIGNATURE_PKI_ERROR_BAD_CERT_SIZE                   = 19
XDW_SIGNATURE_PKI_ERROR_BAD_ARG                         = 20
XDW_SIGNATURE_PKI_ERROR_BAD_CERT_FORMAT                 = 21

XDW_SIGNATURE_PKI_ERROR = XDWConst({
        XDW_SIGNATURE_PKI_ERROR_UNKNOWN                 : "UNKNOWN",
        XDW_SIGNATURE_PKI_ERROR_OK                      : "OK",
        XDW_SIGNATURE_PKI_ERROR_BAD_PLATFORM            : "BAD_PLATFORM",
        XDW_SIGNATURE_PKI_ERROR_WRITE_REG_ERROR         : "WRITE_REG_ERROR",
        XDW_SIGNATURE_PKI_ERROR_BAD_TRUST_LEVEL         : "BAD_TRUST_LEVEL",
        XDW_SIGNATURE_PKI_ERROR_BAD_REVOKE_CHECK_TYPE   : "BAD_REVOKE_CHECK_TYPE",
        XDW_SIGNATURE_PKI_ERROR_BAD_AUTO_IMPORT_CERT_FLAG : "BAD_AUTO_IMPORT_CERT_FLAG",
        XDW_SIGNATURE_PKI_ERROR_BAD_SIGN_CONFIG         : "BAD_SIGN_CONFIG",
        XDW_SIGNATURE_PKI_ERROR_NO_IMAGE_FILE           : "NO_IMAGE_FILE",
        XDW_SIGNATURE_PKI_ERROR_BAD_SIGN_CERT           : "BAD_SIGN_CERT",
        XDW_SIGNATURE_PKI_ERROR_NO_SIGN_CERT            : "NO_SIGN_CERT",
        XDW_SIGNATURE_PKI_ERROR_NOT_USE_PRIVATE_KEY     : "NOT_USE_PRIVATE_KEY",
        XDW_SIGNATURE_PKI_ERROR_INVALID                 : "INVALID",
        XDW_SIGNATURE_PKI_ERROR_BAD_SIGN                : "BAD_SIGN",
        XDW_SIGNATURE_PKI_ERROR_REVOKE_CHECK_ERROR      : "REVOKE_CHECK_ERROR",
        XDW_SIGNATURE_PKI_ERROR_OUT_OF_VALIDITY         : "OUT_OF_VALIDITY",
        XDW_SIGNATURE_PKI_ERROR_NO_CERT                 : "NO_CERT",
        XDW_SIGNATURE_PKI_ERROR_FAILURE_IMPOPT_CERT     : "FAILURE_IMPOPT_CERT",
        XDW_SIGNATURE_PKI_ERROR_NO_ROOT_CERT            : "NO_ROOT_CERT",
        XDW_SIGNATURE_PKI_ERROR_BAD_CERT_SIZE           : "BAD_CERT_SIZE",
        XDW_SIGNATURE_PKI_ERROR_BAD_ARG                 : "BAD_ARG",
        XDW_SIGNATURE_PKI_ERROR_BAD_CERT_FORMAT         : "BAD_CERT_FORMAT",
        })

XDW_SECURITY_PKI_ERROR_UNKNOWN                          = 0
XDW_SECURITY_PKI_ERROR_OK                               = 1
XDW_SECURITY_PKI_ERROR_BAD_PLATFORM                     = 2
XDW_SECURITY_PKI_ERROR_WRITE_REG_ERROR                  = 3
XDW_SECURITY_PKI_ERROR_BAD_TRUST_LEVEL                  = 4
XDW_SECURITY_PKI_ERROR_BAD_REVOKE_CHECK_TYPE            = 5
XDW_SECURITY_PKI_ERROR_REVOKED                          = 6
XDW_SECURITY_PKI_ERROR_BAD_SIGN                         = 7
XDW_SECURITY_PKI_ERROR_REVOKE_CHECK_ERROR               = 8
XDW_SECURITY_PKI_ERROR_OUT_OF_VALIDITY                  = 9
XDW_SECURITY_PKI_ERROR_NO_CERT                          = 10
XDW_SECURITY_PKI_ERROR_FAILURE_IMPORT_CERT              = 11
XDW_SECURITY_PKI_ERROR_NO_ROOT_CERT                     = 12
XDW_SECURITY_PKI_ERROR_BAD_CERT_FORMAT                  = 13
XDW_SECURITY_PKI_ERROR_BAD_CERT_USAGE                   = 14
XDW_SECURITY_PKI_ERROR_CA_CERT_IS_REVOKED               = 15
XDW_SECURITY_PKI_ERROR_TOO_MANY_CERT                    = 16

XDW_SECURITY_PKI_ERROR = XDWConst({
        XDW_SECURITY_PKI_ERROR_UNKNOWN                  : "UNKNOWN",
        XDW_SECURITY_PKI_ERROR_OK                       : "OK",
        XDW_SECURITY_PKI_ERROR_BAD_PLATFORM             : "BAD_PLATFORM",
        XDW_SECURITY_PKI_ERROR_WRITE_REG_ERROR          : "WRITE_REG_ERROR",
        XDW_SECURITY_PKI_ERROR_BAD_TRUST_LEVEL          : "BAD_TRUST_LEVEL",
        XDW_SECURITY_PKI_ERROR_BAD_REVOKE_CHECK_TYPE    : "BAD_REVOKE_CHECK_TYPE",
        XDW_SECURITY_PKI_ERROR_REVOKED                  : "REVOKED",
        XDW_SECURITY_PKI_ERROR_BAD_SIGN                 : "BAD_SIGN",
        XDW_SECURITY_PKI_ERROR_REVOKE_CHECK_ERROR       : "REVOKE_CHECK_ERROR",
        XDW_SECURITY_PKI_ERROR_OUT_OF_VALIDITY          : "OUT_OF_VALIDITY",
        XDW_SECURITY_PKI_ERROR_NO_CERT                  : "NO_CERT",
        XDW_SECURITY_PKI_ERROR_FAILURE_IMPORT_CERT      : "FAILURE_IMPORT_CERT",
        XDW_SECURITY_PKI_ERROR_NO_ROOT_CERT             : "NO_ROOT_CERT",
        XDW_SECURITY_PKI_ERROR_BAD_CERT_FORMAT          : "BAD_CERT_FORMAT",
        XDW_SECURITY_PKI_ERROR_BAD_CERT_USAGE           : "BAD_CERT_USAGE",
        XDW_SECURITY_PKI_ERROR_CA_CERT_IS_REVOKED       : "CA_CERT_IS_REVOKED",
        XDW_SECURITY_PKI_ERROR_TOO_MANY_CERT            : "TOO_MANY_CERT",
        }, default=XDW_SECURITY_PKI_ERROR_UNKNOWN)

XDW_PROP_TITLE                      = b"%Title"
XDW_PROP_SUBJECT                    = b"%Subject"
XDW_PROP_AUTHOR                     = b"%Author"
XDW_PROP_KEYWORDS                   = b"%Keywords"
XDW_PROP_COMMENTS                   = b"%Comments"

XDW_DOCUMENT_ATTRIBUTE = XDWConst({
        XDW_PROP_TITLE              : "%Title",
        XDW_PROP_SUBJECT            : "%Subject",
        XDW_PROP_AUTHOR             : "%Author",
        XDW_PROP_KEYWORDS           : "%Keywords",
        XDW_PROP_COMMENTS           : "%Comments",
        }, default=None)

XDW_PROPW_TITLE                     = b"%Title"
XDW_PROPW_SUBJECT                   = b"%Subject"
XDW_PROPW_AUTHOR                    = b"%Author"
XDW_PROPW_KEYWORDS                  = b"%Keywords"
XDW_PROPW_COMMENTS                  = b"%Comments"

XDW_DOCUMENT_ATTRIBUTE_W = XDWConst({
        XDW_PROPW_TITLE             : "%Title",
        XDW_PROPW_SUBJECT           : "%Subject",
        XDW_PROPW_AUTHOR            : "%Author",
        XDW_PROPW_KEYWORDS          : "%Keywords",
        XDW_PROPW_COMMENTS          : "%Comments",
        }, default=None)

XDW_BINDER_SIZE = XDWConst({
        XDW_SIZE_FREE               : "FREE",
        XDW_SIZE_A3_PORTRAIT        : "A3R",
        XDW_SIZE_A3_LANDSCAPE       : "A3",
        XDW_SIZE_A4_PORTRAIT        : "A4R",
        XDW_SIZE_A4_LANDSCAPE       : "A4",
        XDW_SIZE_A5_PORTRAIT        : "A5R",
        XDW_SIZE_A5_LANDSCAPE       : "A5",
        XDW_SIZE_B4_PORTRAIT        : "B4R",
        XDW_SIZE_B4_LANDSCAPE       : "B4",
        XDW_SIZE_B5_PORTRAIT        : "B5R",
        XDW_SIZE_B5_LANDSCAPE       : "B5",
        }, default=XDW_SIZE_FREE)

XDW_BINDER_COLOR = XDWConst({
        # Here we describe colors in RRGGBB format, though DocuWorks
        # inner color representation is BBGGRR.
        XDW_BINDER_COLOR_0          : "NAVY",       # 0x003366
        XDW_BINDER_COLOR_1          : "GREEN",      # 0x006633
        XDW_BINDER_COLOR_2          : "BLUE",       # 0x3366FF
        XDW_BINDER_COLOR_3          : "YELLOW",     # 0xFFFF66
        XDW_BINDER_COLOR_4          : "ORANGE",     # 0xFF6633
        XDW_BINDER_COLOR_5          : "RED",        # 0xFF3366
        XDW_BINDER_COLOR_6          : "FUCHSIA",    # 0xFF00FF
        XDW_BINDER_COLOR_7          : "PINK",       # 0xFFCCFF
        XDW_BINDER_COLOR_8          : "PURPLE",     # 0xCC99FF
        XDW_BINDER_COLOR_9          : "BROWN",      # 0x663333
        XDW_BINDER_COLOR_10         : "OLIVE",      # 0x999933
        XDW_BINDER_COLOR_11         : "LIME",       # 0x00FF00
        XDW_BINDER_COLOR_12         : "AQUA",       # 0x00FFFF
        XDW_BINDER_COLOR_13         : "CREAM",      # 0xFFFFCC
        XDW_BINDER_COLOR_14         : "SILVER",     # 0xBBBBBB
        XDW_BINDER_COLOR_15         : "WHITE",      # 0xFFFFFF
        }, default=XDW_BINDER_COLOR_5)

### Page related

XDW_GPTI_TYPE_EMF                   = 0
XDW_GPTI_TYPE_OCRTEXT               = 1

XDW_IMAGE_MONO                      = 0
XDW_IMAGE_COLOR                     = 1
XDW_IMAGE_MONO_HIGHQUALITY          = 2

XDW_IMAGE_COLORSCHEME = XDWConst({
        XDW_IMAGE_MONO              : "MONO",
        XDW_IMAGE_COLOR             : "COLOR",
        XDW_IMAGE_MONO_HIGHQUALITY  : "MONO_HIGHQUALITY",
        }, default=XDW_IMAGE_COLOR)

# rotation

XDW_ROT_0                           = 0
XDW_ROT_90                          = 90
XDW_ROT_180                         = 180
XDW_ROT_270                         = 270

# OCR

XDW_REDUCENOISE_NONE                            = 0
XDW_REDUCENOISE_NORMAL                          = 1
XDW_REDUCENOISE_WEAK                            = 2
XDW_REDUCENOISE_STRONG                          = 3

XDW_OCR_NOISEREDUCTION = XDWConst({
        XDW_REDUCENOISE_NONE                    : "NONE",
        XDW_REDUCENOISE_NORMAL                  : "NORMAL",
        XDW_REDUCENOISE_WEAK                    : "WEAK",
        XDW_REDUCENOISE_STRONG                  : "STRONG",
        }, default=XDW_REDUCENOISE_NONE)

XDW_PRIORITY_NONE                               = 0
XDW_PRIORITY_SPEED                              = 1
XDW_PRIORITY_RECOGNITION                        = 2
XDW_PRIORITY_ACCURACY = XDW_PRIORITY_RECOGNITION

XDW_PRIORITY = XDWConst({
        XDW_PRIORITY_NONE                       : "NONE",
        XDW_PRIORITY_SPEED                      : "SPEED",
        XDW_PRIORITY_ACCURACY                   : "ACCURACY",
        }, default=XDW_PRIORITY_NONE)

XDW_OCR_ENGINE_V4                               = 1  # for compatibility
XDW_OCR_ENGINE_DEFAULT                          = 1
XDW_OCR_ENGINE_WRP                              = 2
XDW_OCR_ENGINE_FRE                              = 3
XDW_OCR_ENGINE_FRE_MULTI                        = 4

XDW_OCR_ENGINE = XDWConst({
        XDW_OCR_ENGINE_DEFAULT                  : "DEFAULT",
        XDW_OCR_ENGINE_WRP                      : "WINREADER PRO",
        XDW_OCR_ENGINE_FRE                      : "EXTENDED",
        XDW_OCR_ENGINE_FRE_MULTI                : "MULTI",
        }, default=XDW_OCR_ENGINE_DEFAULT)


XDW_OCR_LANGUAGE_AUTO                           = -1
XDW_OCR_LANGUAGE_JAPANESE                       = 0
XDW_OCR_LANGUAGE_ENGLISH                        = 1

XDW_OCR_LANGUAGE = XDWConst({
        XDW_OCR_LANGUAGE_AUTO                   : "AUTO",
        XDW_OCR_LANGUAGE_JAPANESE               : "JAPANESE",
        XDW_OCR_LANGUAGE_ENGLISH                : "ENGLISH",
        }, default=XDW_OCR_LANGUAGE_AUTO)

#XDW_OCR_MULTIPLELANGUAGES_AUTO                  = 0x01
XDW_OCR_MULTIPLELANGUAGES_ENGLISH               = 0x02
XDW_OCR_MULTIPLELANGUAGES_FRENCH                = 0x04
XDW_OCR_MULTIPLELANGUAGES_SIMPLIFIED_CHINESE    = 0x08
XDW_OCR_MULTIPLELANGUAGES_TRADITIONAL_CHINESE   = 0x10
XDW_OCR_MULTIPLELANGUAGES_THAI                  = 0x20
XDW_OCR_MULTIPLELANGUAGES_JAPANESE              = 0x40
XDW_OCR_MULTIPLELANGUAGES_KOREAN                = 0x80
XDW_OCR_MULTIPLELANGUAGES_VIETNAMESE            = 0x100
XDW_OCR_MULTIPLELANGUAGES_INDONESIAN            = 0x200
XDW_OCR_MULTIPLELANGUAGES_MALAY                 = 0x400
XDW_OCR_MULTIPLELANGUAGES_TAGALOG               = 0x800

XDW_OCR_MULTIPLELANGUAGES = XDWConst({
        XDW_OCR_MULTIPLELANGUAGES_ENGLISH       : "ENGLISH",
        XDW_OCR_MULTIPLELANGUAGES_FRENCH        : "FRENCH",
        XDW_OCR_MULTIPLELANGUAGES_SIMPLIFIED_CHINESE: "SIMPLIFIED_CHINESE",
        XDW_OCR_MULTIPLELANGUAGES_TRADITIONAL_CHINESE : "TRADITIONAL_CHINESE",
        XDW_OCR_MULTIPLELANGUAGES_THAI          : "THAI",
        XDW_OCR_MULTIPLELANGUAGES_JAPANESE      : "JAPANESE",
        XDW_OCR_MULTIPLELANGUAGES_KOREAN        : "KOREAN",
        XDW_OCR_MULTIPLELANGUAGES_VIETNAMESE    : "VIETNAMESE",
        XDW_OCR_MULTIPLELANGUAGES_INDONESIAN    : "INDONESIAN",
        XDW_OCR_MULTIPLELANGUAGES_MALAY         : "MALAY",
        XDW_OCR_MULTIPLELANGUAGES_TAGALOG       : "TAGALOG",
        }, default=XDW_OCR_MULTIPLELANGUAGES_ENGLISH)

XDW_OCR_FORM_AUTO                               = 0
XDW_OCR_FORM_TABLE                              = 1
XDW_OCR_FORM_WRITING                            = 2

XDW_OCR_FORM = XDWConst({
        XDW_OCR_FORM_AUTO                       : "AUTO",
        XDW_OCR_FORM_TABLE                      : "TABLE",
        XDW_OCR_FORM_WRITING                    : "WRITING",
        }, default=XDW_OCR_FORM_AUTO)

XDW_OCR_COLUMN_AUTO                             = 0
XDW_OCR_COLUMN_HORIZONTAL_SINGLE                = 1
XDW_OCR_COLUMN_HORIZONTAL_MULTI                 = 2
XDW_OCR_COLUMN_VERTICAL_SINGLE                  = 3
XDW_OCR_COLUMN_VERTICAL_MULTI                   = 4

XDW_OCR_COLUMN = XDWConst({
        XDW_OCR_COLUMN_AUTO                     : "AUTO",
        XDW_OCR_COLUMN_HORIZONTAL_SINGLE        : "HORIZONTAL_SINGLE",
        XDW_OCR_COLUMN_HORIZONTAL_MULTI         : "HORIZONTAL_MULTI",
        XDW_OCR_COLUMN_VERTICAL_SINGLE          : "VERTICAL_SINGLE",
        XDW_OCR_COLUMN_VERTICAL_MULTI           : "VERTICAL_MULTI",
        }, default=XDW_OCR_COLUMN_AUTO)

XDW_OCR_DOCTYPE_AUTO                            = 0
XDW_OCR_DOCTYPE_HORIZONTAL_SINGLE               = 1
XDW_OCR_DOCTYPE_PLAINTEXT                       = 2

XDW_OCR_ENGINE_LEVEL_SPEED                      = 1
XDW_OCR_ENGINE_LEVEL_STANDARD                   = 2
XDW_OCR_ENGINE_LEVEL_ACCURACY                   = 3

XDW_OCR_ENGINE_LEVEL = XDWConst({
        XDW_OCR_ENGINE_LEVEL_SPEED              : "SPEED",
        XDW_OCR_ENGINE_LEVEL_STANDARD           : "STANDARD",
        XDW_OCR_ENGINE_LEVEL_ACCURACY           : "ACCURACY",
        }, default=XDW_OCR_ENGINE_LEVEL_STANDARD)
XDW_OCR_STRATEGY = XDW_OCR_ENGINE_LEVEL

XDW_OCR_MIXEDRATE_JAPANESE                      = 1
XDW_OCR_MIXEDRATE_BALANCED                      = 2
XDW_OCR_MIXEDRATE_ENGLISH                       = 3

XDW_OCR_MAIN_LANGUAGE = XDWConst({
        XDW_OCR_MIXEDRATE_JAPANESE              : "JAPANESE",
        XDW_OCR_MIXEDRATE_BALANCED              : "BALANCED",
        XDW_OCR_MIXEDRATE_ENGLISH               : "ENGLISH",
        }, default=XDW_OCR_MIXEDRATE_BALANCED)

XDW_OCR_PREPROCESSING_SPEED                     = 0
XDW_OCR_PREPROCESSING_RECOGNITION               = 1
XDW_OCR_PREPROCESSING_ACCURACY = XDW_OCR_PREPROCESSING_RECOGNITION

XDW_OCR_PREPROCESSING = XDWConst({
        XDW_OCR_PREPROCESSING_SPEED    : "SPEED",
        XDW_OCR_PREPROCESSING_ACCURACY : "ACCURACY",
        }, default=XDW_OCR_PREPROCESSING_ACCURACY)

XDW_OCR_PREPROCESS_PRIORITY_MONO_SPEED          = 0
XDW_OCR_PREPROCESS_PRIORITY_MONO_ACCURACY       = 1
XDW_OCR_PREPROCESS_PRIORITY_COLOR               = 2

XDW_OCR_PREPROCESS_PRIORITY = XDWConst({
        XDW_OCR_PREPROCESS_PRIORITY_MONO_SPEED  : "MONO_SPEED",
        XDW_OCR_PREPROCESS_PRIORITY_MONO_ACCURACY: "MONO_ACCURACY",
        XDW_OCR_PREPROCESS_PRIORITY_COLOR       : "COLOR",
        }, default=XDW_OCR_PREPROCESS_PRIORITY_MONO_ACCURACY)

# page type

XDW_PGT_NULL                        = 0
XDW_PGT_FROMIMAGE                   = 1
XDW_PGT_FROMAPPL                    = 2

XDW_PAGE_TYPE = XDWConst({
        XDW_PGT_FROMIMAGE           : "IMAGE",
        XDW_PGT_FROMAPPL            : "APPLICATION",
        XDW_PGT_NULL                : "NULL",
        }, default=XDW_PGT_NULL)

### Annotation related

XDW_AID_FUSEN                       = 32794
XDW_AID_TEXT                        = 32785
XDW_AID_STAMP                       = 32819
XDW_AID_STRAIGHTLINE                = 32828
XDW_AID_RECTANGLE                   = 32829
XDW_AID_ARC                         = 32830
XDW_AID_POLYGON                     = 32834
XDW_AID_MARKER                      = 32795
XDW_AID_LINK                        = 49199
XDW_AID_PAGEFORM                    = 32814
XDW_AID_OLE                         = 32783
XDW_AID_BITMAP                      = 32831
XDW_AID_RECEIVEDSTAMP               = 32832
XDW_AID_CUSTOM                      = 32837
XDW_AID_TITLE                       = 32838
XDW_AID_GROUP                       = 32839

XDW_ANNOTATION_TYPE = XDWConst({
        XDW_AID_FUSEN               : "STICKEY",
        XDW_AID_TEXT                : "TEXT",
        XDW_AID_STAMP               : "STAMP",
        XDW_AID_STRAIGHTLINE        : "STRAIGHTLINE",
        XDW_AID_RECTANGLE           : "RECTANGLE",
        XDW_AID_ARC                 : "ARC",
        XDW_AID_POLYGON             : "POLYGON",
        XDW_AID_MARKER              : "MARKER",
        XDW_AID_LINK                : "LINK",
        XDW_AID_PAGEFORM            : "PAGEFORM",
        XDW_AID_OLE                 : "OLE",
        XDW_AID_BITMAP              : "BITMAP",
        XDW_AID_RECEIVEDSTAMP       : "RECEIVEDSTAMP",
        XDW_AID_CUSTOM              : "CUSTOM",
        XDW_AID_TITLE               : "TITLE",
        XDW_AID_GROUP               : "GROUP",
        }, default=XDW_AID_TEXT)

XDW_ATYPE_INT                       = 0
XDW_ATYPE_STRING                    = 1
XDW_ATYPE_DATE                      = 2
XDW_ATYPE_BOOL                      = 3
XDW_ATYPE_OCTS                      = 4
XDW_ATYPE_OTHER                     = 999

XDW_ATTRIBUTE_TYPE = XDWConst({
        XDW_ATYPE_INT               : "INT",
        XDW_ATYPE_STRING            : "STRING",
        XDW_ATYPE_DATE              : "DATE",
        XDW_ATYPE_BOOL              : "BOOL",
        XDW_ATYPE_OCTS              : "OCTS",
        XDW_ATYPE_OTHER             : "OTHER",
        })

XDW_LINE_NONE                       = 0
XDW_LINE_BEGINNING                  = 1
XDW_LINE_ENDING                     = 2
XDW_LINE_BOTH                       = 3

XDW_ARROWHEAD_TYPE = XDWConst({
        XDW_LINE_NONE               : "NONE",
        XDW_LINE_BEGINNING          : "BEGINNING",
        XDW_LINE_ENDING             : "ENDING",
        XDW_LINE_BOTH               : "BOTH",
        }, default=XDW_LINE_NONE)

XDW_LINE_WIDE_POLYLINE              = 0
XDW_LINE_POLYLINE                   = 1
XDW_LINE_POLYGON                    = 2

XDW_ARROWHEAD_STYLE = XDWConst({
        XDW_LINE_WIDE_POLYLINE      : "WIDE",
        XDW_LINE_POLYLINE           : "NORMAL",
        XDW_LINE_POLYGON            : "FILL",
        }, default="NORMAL")

XDW_BORDER_TYPE_SOLID               = 0
XDW_BORDER_TYPE_DOT                 = 1
XDW_BORDER_TYPE_DASH                = 2
XDW_BORDER_TYPE_DASHDOT             = 3
XDW_BORDER_TYPE_DOUBLE              = 4

XDW_BORDER_TYPE = XDWConst({
        XDW_BORDER_TYPE_SOLID       : "SOLID",
        XDW_BORDER_TYPE_DOT         : "DOT",
        XDW_BORDER_TYPE_DASH        : "DASH",
        XDW_BORDER_TYPE_DASHDOT     : "DASHDOT",
        XDW_BORDER_TYPE_DOUBLE      : "DOUBLE",
        }, default=XDW_BORDER_TYPE_SOLID)

XDW_STAMP_AUTO                      = 0
XDW_STAMP_MANUAL                    = 1

XDW_STAMP_DATE_STYLE = XDWConst({
        XDW_STAMP_AUTO              : "AUTO",
        XDW_STAMP_MANUAL            : "MANUAL",
        }, default=XDW_STAMP_AUTO)

XDW_STAMP_NO_BASISYEAR              = 0
XDW_STAMP_BASISYEAR                 = 1

XDW_STAMP_BASISYEAR_STYLE = XDWConst({
        XDW_STAMP_NO_BASISYEAR      : "CLEAR",
        XDW_STAMP_BASISYEAR         : "SET",
        }, default=XDW_STAMP_NO_BASISYEAR)

XDW_STAMP_DATE_YMD                  = 0
XDW_STAMP_DATE_DMY                  = 1

XDW_STAMP_DATE_ORDER = XDWConst({
        XDW_STAMP_DATE_YMD          : "YMD",
        XDW_STAMP_DATE_DMY          : "DMY",
        }, default=XDW_STAMP_DATE_YMD)

XDW_PAGEFORM_HEADER                 = 0
XDW_PAGEFORM_FOOTER                 = 1
XDW_PAGEFORM_TOPIMAGE               = 2
XDW_PAGEFORM_BOTTOMIMAGE            = 3
XDW_PAGEFORM_PAGENUMBER             = 4

XDW_PAGEFORM = XDWConst({
        XDW_PAGEFORM_HEADER         : "HEADER",
        XDW_PAGEFORM_FOOTER         : "FOOTER",
        XDW_PAGEFORM_TOPIMAGE       : "TOPIMAGE",
        XDW_PAGEFORM_BOTTOMIMAGE    : "BOTTOMIMAGE",
        XDW_PAGEFORM_PAGENUMBER     : "PAGENUMBER",
        }, default=XDW_PAGEFORM_PAGENUMBER)

XDW_PAGEFORM_STAY                   = 0
XDW_PAGEFORM_REMOVE                 = 1

XDW_PAGEFORM_STAYREMOVE = XDWConst({
        XDW_PAGEFORM_STAY           : "ISOLATED",
        XDW_PAGEFORM_REMOVE         : "CONSOLIDATED",
        }, default=XDW_PAGEFORM_STAY)

XDW_ALIGN_LEFT                      = 0
XDW_ALIGN_HCENTER                   = 1
XDW_ALIGN_RIGHT                     = 2
XDW_ALIGN_TOP                       = 0
XDW_ALIGN_BOTTOM                    = 1
XDW_ALIGN_VCENTER                   = 2

XDW_ALIGN_HPOS = XDWConst({
        XDW_ALIGN_LEFT              : "LEFT",
        XDW_ALIGN_HCENTER           : "CENTER",
        XDW_ALIGN_RIGHT             : "RIGHT",
        }, default=XDW_ALIGN_HCENTER)

XDW_ALIGN_VPOS = XDWConst({
        XDW_ALIGN_TOP               : "TOP",
        XDW_ALIGN_VCENTER           : "CENTER",
        XDW_ALIGN_BOTTOM            : "BOTTOM",
        }, default=XDW_ALIGN_VCENTER)

XDW_PAGERANGE_ALL                   = 0
XDW_PAGERANGE_SPECIFIED             = 1

XDW_PAGERANGE = XDWConst({
        XDW_PAGERANGE_ALL           : "ALL",
        XDW_PAGERANGE_SPECIFIED     : "SPECIFIED",
        }, default=XDW_PAGERANGE_ALL)

XDW_IGNORE_CASE                     = 0x02
XDW_IGNORE_WIDTH                    = 0x04
XDW_IGNORE_HIRAKATA                 = 0x08

XDW_STARCH                          = 1
XDW_STARCH_OFF                      = 0

XDW_STARCH_ACTION = XDWConst({
        XDW_STARCH                  : "ON",
        XDW_STARCH_OFF              : "OFF",
        }, default=XDW_STARCH)

XDW_ATN_Text                        = b"%Text"
XDW_ATN_FontName                    = b"%FontName"
XDW_ATN_FontStyle                   = b"%FontStyle"
XDW_ATN_FontSize                    = b"%FontSize"
XDW_ATN_ForeColor                   = b"%ForeColor"
XDW_ATN_FontPitchAndFamily          = b"%FontPitchAndFamily"
XDW_ATN_FontCharSet                 = b"%FontCharSet"
XDW_ATN_BackColor                   = b"%BackColor"
XDW_ATN_Caption                     = b"%Caption"
XDW_ATN_Url                         = b"%Url"
XDW_ATN_XdwPath                     = b"%XdwPath"
XDW_ATN_ShowIcon                    = b"%ShowIcon"
XDW_ATN_LinkType                    = b"%LinkType"
XDW_ATN_XdwPage                     = b"%XdwPage"
XDW_ATN_Tooltip                     = b"%Tooltip"
XDW_ATN_Tooltip_String              = b"%TooltipString"
XDW_ATN_TooltipString               = XDW_ATN_Tooltip_String            # alias
XDW_ATN_XdwPath_Relative            = b"%XdwPathRelative"
XDW_ATN_XdwPathRelative             = XDW_ATN_XdwPath_Relative          # alias
XDW_ATN_XdwLink                     = b"%XdwLink"
XDW_ATN_LinkAtn_Title               = b"%LinkAtnTitle"
XDW_ATN_LinkAtnTitle                = XDW_ATN_LinkAtn_Title             # alias
XDW_ATN_OtherFilePath               = b"%OtherFilePath"
XDW_ATN_OtherFilePath_Relative      = b"%OtherFilePathRelative"
XDW_ATN_OtherFilePathRelative       = XDW_ATN_OtherFilePath_Relative    # alias
XDW_ATN_MailAddress                 = b"%MailAddress"
XDW_ATN_BorderStyle                 = b"%BorderStyle"
XDW_ATN_BorderWidth                 = b"%BorderWidth"
XDW_ATN_BorderColor                 = b"%BorderColor"
XDW_ATN_BorderTransparent           = b"%BorderTransparent"
XDW_ATN_BorderType                  = b"%BorderType"
XDW_ATN_FillStyle                   = b"%FillStyle"
XDW_ATN_FillColor                   = b"%FillColor"
XDW_ATN_FillTransparent             = b"%FillTransparent"
XDW_ATN_ArrowheadType               = b"%ArrowheadType"
XDW_ATN_ArrowheadStyle              = b"%ArrowheadStyle"
XDW_ATN_WordWrap                    = b"%WordWrap"
XDW_ATN_TextDirection               = b"%TextDirection"
XDW_ATN_TextOrientation             = b"%TextOrientation"
XDW_ATN_LineSpace                   = b"%LineSpace"
XDW_ATN_AutoResize                  = b"%AutoResize"
XDW_ATN_Invisible                   = b"%Invisible"
XDW_ATN_PageFrom                    = b"%PageFrom"
XDW_ATN_XdwNameInXbd                = b"%XdwNameInXbd"
XDW_ATN_TopField                    = b"%TopField"
XDW_ATN_BottomField                 = b"%BottomField"
XDW_ATN_DateStyle                   = b"%DateStyle"
XDW_ATN_YearField                   = b"%YearField"
XDW_ATN_MonthField                  = b"%MonthField"
XDW_ATN_DayField                    = b"%DayField"
XDW_ATN_BasisYearStyle              = b"%BasisYearStyle"
XDW_ATN_BasisYear                   = b"%BasisYear"
XDW_ATN_DateField_FirstChar         = b"%DateFieldFirstChar"
XDW_ATN_DateFieldFirstChar          = XDW_ATN_DateField_FirstChar       # alias
XDW_ATN_Alignment                   = b"%Alignment"
XDW_ATN_LeftRightMargin             = b"%LeftRightMargin"
XDW_ATN_TopBottomMargin             = b"%TopBottomMargin"
XDW_ATN_VerPosition                 = b"%VerPosition"
XDW_ATN_StartingNumber              = b"%StartingNumber"
XDW_ATN_Digit                       = b"%Digit"
XDW_ATN_PageRange                   = b"%PageRange"
XDW_ATN_BeginningPage               = b"%BeginningPage"
XDW_ATN_EndingPage                  = b"%EndingPage"
XDW_ATN_Zoom                        = b"%Zoom"
XDW_ATN_ImageFile                   = b"%ImageFile"
XDW_ATN_Points                      = b"%Points"
XDW_ATN_DateFormat                  = b"%DateFormat"
XDW_ATN_DateOrder                   = b"%DateOrder"
XDW_ATN_TextSpacing                 = b"%Spacing"
XDW_ATN_TextTopMargin               = b"%TopMargin"
XDW_ATN_TextLeftMargin              = b"%LeftMargin"
XDW_ATN_TextBottomMargin            = b"%BottomMargin"
XDW_ATN_TextRightMargin             = b"%RightMargin"
XDW_ATN_TextAutoResizeHeight        = b"%AutoResizeHeight"
XDW_ATN_TopMargin                   = XDW_ATN_TextTopMargin             # alias
XDW_ATN_LeftMargin                  = XDW_ATN_TextLeftMargin            # alias
XDW_ATN_BottomMargin                = XDW_ATN_TextBottomMargin          # alias
XDW_ATN_RightMargin                 = XDW_ATN_TextRightMargin           # alias
XDW_ATN_AutoResizeHeight            = XDW_ATN_TextAutoResizeHeight
XDW_ATN_GUID                        = b"%CustomAnnGuid"
XDW_ATN_CustomData                  = b"%CustomAnnCustomData"
XDW_ATN_CustomAnnGuid               = XDW_ATN_GUID                      # alias
XDW_ATN_CustomAnnCustomData         = XDW_ATN_CustomData                # alias

XDW_COLOR_NONE                      = 0x010101
XDW_COLOR_BLACK                     = 0x000000
XDW_COLOR_MAROON                    = 0x000080
XDW_COLOR_GREEN                     = 0x008000
XDW_COLOR_OLIVE                     = 0x008080
XDW_COLOR_NAVY                      = 0x800000
XDW_COLOR_PURPLE                    = 0x800080
XDW_COLOR_TEAL                      = 0x808000
XDW_COLOR_GRAY                      = 0x808080
XDW_COLOR_SILVER                    = 0xC0C0C0
XDW_COLOR_RED                       = 0x0000FF
XDW_COLOR_LIME                      = 0x00FF00
XDW_COLOR_YELLOW                    = 0x00FFFF
XDW_COLOR_BLUE                      = 0xFF0000
XDW_COLOR_FUCHSIA                   = 0xFF00FF
XDW_COLOR_AQUA                      = 0xFFFF00
XDW_COLOR_WHITE                     = 0xFFFFFF
XDW_COLOR_FUSEN_RED                 = 0xFFC2FF
XDW_COLOR_FUSEN_BLUE                = 0xFFBF9D
XDW_COLOR_FUSEN_YELLOW              = 0x64FFFF
XDW_COLOR_FUSEN_LIME                = 0xC2FF9D
XDW_COLOR_FUSEN_PALE_RED            = 0xE1D7FF
XDW_COLOR_FUSEN_PALE_BLUE           = 0xFAE1C8
XDW_COLOR_FUSEN_PALE_YELLOW         = 0xC3FAFF
XDW_COLOR_FUSEN_PALE_LIME           = 0xD2FACD

XDW_COLOR = XDWConst({
        XDW_COLOR_NONE              : "NONE",
        XDW_COLOR_BLACK             : "BLACK",
        XDW_COLOR_MAROON            : "MAROON",
        XDW_COLOR_GREEN             : "GREEN",
        XDW_COLOR_OLIVE             : "OLIVE",
        XDW_COLOR_NAVY              : "NAVY",
        XDW_COLOR_PURPLE            : "PURPLE",
        XDW_COLOR_TEAL              : "TEAL",
        XDW_COLOR_GRAY              : "GRAY",
        XDW_COLOR_SILVER            : "SILVER",
        XDW_COLOR_RED               : "RED",
        XDW_COLOR_LIME              : "LIME",
        XDW_COLOR_YELLOW            : "YELLOW",
        XDW_COLOR_BLUE              : "BLUE",
        XDW_COLOR_FUCHSIA           : "FUCHSIA",
        XDW_COLOR_AQUA              : "AQUA",
        XDW_COLOR_WHITE             : "WHITE",
        }, default=XDW_COLOR_BLACK)

XDW_COLOR_FUSEN = XDWConst({
        XDW_COLOR_WHITE             : "WHITE",
        XDW_COLOR_FUSEN_RED         : "RED",
        XDW_COLOR_FUSEN_BLUE        : "BLUE",
        XDW_COLOR_FUSEN_YELLOW      : "YELLOW",
        XDW_COLOR_FUSEN_LIME        : "LIME",
        XDW_COLOR_FUSEN_PALE_RED    : "PALE_RED",
        XDW_COLOR_FUSEN_PALE_BLUE   : "PALE_BLUE",
        XDW_COLOR_FUSEN_PALE_YELLOW : "PALE_YELLOW",
        XDW_COLOR_FUSEN_PALE_LIME   : "PALE_LIME",
        }, default=XDW_COLOR_FUSEN_PALE_YELLOW)

XDW_FS_ITALIC_FLAG                  = 1
XDW_FS_BOLD_FLAG                    = 2
XDW_FS_UNDERLINE_FLAG               = 4
XDW_FS_STRIKEOUT_FLAG               = 8

XDW_FONT_STYLE = XDWConst({
        XDW_FS_ITALIC_FLAG          : "ITALIC",
        XDW_FS_BOLD_FLAG            : "BOLD",
        XDW_FS_UNDERLINE_FLAG       : "UNDERLINE",
        XDW_FS_STRIKEOUT_FLAG       : "STRIKEOUT",
        }, default=0)

XDW_LT_LINK_TO_ME                   = 0
XDW_LT_LINK_TO_XDW                  = 1
XDW_LT_LINK_TO_URL                  = 2
XDW_LT_LINK_TO_OTHERFILE            = 3
XDW_LT_LINK_TO_MAILADDR             = 4

XDW_LINK_TYPE = XDWConst({
        XDW_LT_LINK_TO_ME           : "ME",
        XDW_LT_LINK_TO_XDW          : "XDW",
        XDW_LT_LINK_TO_URL          : "URL",
        XDW_LT_LINK_TO_OTHERFILE    : "OTHERFILE",
        XDW_LT_LINK_TO_MAILADDR     : "MAILADDR",
        }, default=XDW_LT_LINK_TO_ME)

XDW_PF_XDW                          = 0
XDW_PF_XBD                          = 1
XDW_PF_XDW_IN_XBD                   = 2

XDW_PAGE_FORM = XDWConst({
        XDW_PF_XDW                  : "DOCUMENT",
        XDW_PF_XBD                  : "BINDER",
        XDW_PF_XDW_IN_XBD           : "DOCUMENTINBINDER",
        }, default=XDW_PF_XDW)

ANSI_CHARSET                        = 0
DEFAULT_CHARSET                     = 1
SYMBOL_CHARSET                      = 2
MAC_CHARSET                         = 77
SHIFTJIS_CHARSET                    = 128
HANGEUL_CHARSET                     = 129
CHINESEBIG5_CHARSET                 = 136
GREEK_CHARSET                       = 161
TURKISH_CHARSET                     = 162
BALTIC_CHARSET                      = 186
RUSSIAN_CHARSET                     = 204
EASTEUROPE_CHARSET                  = 238
OEM_CHARSET                         = 255

XDW_FONT_CHARSET = XDWConst({
        ANSI_CHARSET                : "ANSI",
        DEFAULT_CHARSET             : "DEFAULT",
        SYMBOL_CHARSET              : "SYMBOL",
        MAC_CHARSET                 : "MAC",
        SHIFTJIS_CHARSET            : "SHIFTJIS",
        HANGEUL_CHARSET             : "HANGEUL",
        CHINESEBIG5_CHARSET         : "CHINESEBIG5",
        GREEK_CHARSET               : "GREEK",
        TURKISH_CHARSET             : "TURKISH",
        BALTIC_CHARSET              : "BALTIC",
        RUSSIAN_CHARSET             : "RUSSIAN",
        EASTEUROPE_CHARSET          : "EASTEUROPE",
        OEM_CHARSET                 : "OEM",
        }, default=DEFAULT_CHARSET)

### Windows LOGFONT constants
DEFAULT_PITCH           = 0
FIXED_PITCH             = 1
VARIABLE_PITCH          = 2
MONO_FONT               = 8
FF_DONTCARE             = 0
FF_ROMAN                = 16
FF_SWISS                = 32
FF_MODERN               = 48
FF_SCRIPT               = 64
FF_DECORATIVE           = 80

XDW_PITCH_AND_FAMILY = XDWConst({
        0                       : "DEFAULT",
        #DEFAULT_PITCH           : "DEFAULT_PITCH",
        FIXED_PITCH             : "FIXED_PITCH",
        VARIABLE_PITCH          : "VARIABLE_PITCH",
        MONO_FONT               : "MONO_FONT",
        #FF_DONTCARE             : "DONTCARE",
        FF_ROMAN                : "ROMAN",
        FF_SWISS                : "SWISS",
        FF_MODERN               : "MODERN",
        FF_SCRIPT               : "SCRIPT",
        FF_DECORATIVE           : "DECORATIVE",
        }, default=FF_DONTCARE)

# Assert to ensure XDW_ANNOTATION_ATTRIBUTE.
assert XDW_ATYPE_INT == 0
assert XDW_ATYPE_STRING == 1

XDW_ANNOTATION_ATTRIBUTE = {
        # attribute_id: (type, unit, available_ann_types)
        #   where type is either 0(int), 1(string) or 2(points)
        XDW_ATN_Alignment           : (0, XDW_ALIGN_HPOS, ()),
        XDW_ATN_ArrowheadStyle      : (0, XDW_ARROWHEAD_STYLE, (
                                        XDW_AID_STRAIGHTLINE,
                                        )),
        XDW_ATN_ArrowheadType       : (0, XDW_ARROWHEAD_TYPE, (
                                        XDW_AID_STRAIGHTLINE,
                                        )),
        XDW_ATN_AutoResize          : (0, None, (
                                        XDW_AID_LINK,
                                        XDW_AID_FUSEN,
                                        )),
        XDW_ATN_BackColor           : (0, XDW_COLOR, (XDW_AID_TEXT,)),
        XDW_ATN_BasisYear           : (0, None, (XDW_AID_STAMP,)),
        XDW_ATN_BasisYearStyle      : (0, XDW_STAMP_BASISYEAR_STYLE, (
                                        XDW_AID_STAMP,
                                        )),
        XDW_ATN_BeginningPage       : (0, None, ()),
        XDW_ATN_BorderColor         : (0, XDW_COLOR, (
                                        XDW_AID_STRAIGHTLINE,
                                        XDW_AID_RECTANGLE,
                                        XDW_AID_ARC,
                                        XDW_AID_STAMP,
                                        XDW_AID_MARKER,
                                        XDW_AID_POLYGON,
                                        )),
        XDW_ATN_BorderStyle         : (0, None, (XDW_AID_RECTANGLE,
                                                 XDW_AID_ARC,
                                                 XDW_AID_POLYGON,)),
        XDW_ATN_BorderTransparent   : (0, None, (XDW_AID_STRAIGHTLINE,
                                                 XDW_AID_MARKER,)),
        XDW_ATN_BorderType          : (0, XDW_BORDER_TYPE, (
                                        XDW_AID_STRAIGHTLINE,
                                        )),
        XDW_ATN_BorderWidth         : (0, "pt", (
                                        XDW_AID_STRAIGHTLINE,
                                        XDW_AID_RECTANGLE,
                                        XDW_AID_ARC,
                                        XDW_AID_MARKER,
                                        XDW_AID_POLYGON,
                                        )),
        XDW_ATN_BottomField         : (1, None, (XDW_AID_STAMP,)),
        XDW_ATN_Caption             : (1, None, (XDW_AID_LINK,)),
        XDW_ATN_CustomData          : (0, None, ()),
        XDW_ATN_DateField_FirstChar : (1, None, (XDW_AID_STAMP,)),
        # DateFormat in ("yy.mm.dd", "yy.m.d", "dd.mmm.yy", "dd.mmm.yyyy")
        XDW_ATN_DateFormat          : (1, None, (XDW_AID_STAMP,)),
        XDW_ATN_DateOrder           : (0, XDW_STAMP_DATE_ORDER, (
                                        XDW_AID_STAMP,
                                        )),
        XDW_ATN_DateStyle           : (0, XDW_STAMP_DATE_STYLE, (
                                        XDW_AID_STAMP,
                                        )),
        XDW_ATN_DayField            : (1, None, (XDW_AID_STAMP,)),
        XDW_ATN_Digit               : (0, None, ()),
        XDW_ATN_EndingPage          : (0, None, ()),
        XDW_ATN_FillColor           : (0, XDW_COLOR, (XDW_AID_FUSEN,
                                                 XDW_AID_RECTANGLE,
                                                 XDW_AID_ARC,
                                                 XDW_AID_POLYGON,)),
        XDW_ATN_FillStyle           : (0, None, (XDW_AID_RECTANGLE,
                                                 XDW_AID_ARC,
                                                 XDW_AID_POLYGON,)),
        XDW_ATN_FillTransparent     : (0, None, (XDW_AID_RECTANGLE,
                                                 XDW_AID_ARC,
                                                 XDW_AID_POLYGON,)),
        XDW_ATN_FontCharSet         : (0, XDW_FONT_CHARSET, (
                                        XDW_AID_TEXT, XDW_AID_LINK,
                                        )),
        XDW_ATN_FontName            : (1, None, (XDW_AID_TEXT, XDW_AID_LINK,)),
        # Take special care in your code for FontPitchAndFamily.
        XDW_ATN_FontPitchAndFamily  : (0, XDW_PITCH_AND_FAMILY, (
                                        XDW_AID_TEXT, XDW_AID_LINK,
                                        )),
        XDW_ATN_FontSize            : (0, "1/10pt", (XDW_AID_TEXT,
                                                     XDW_AID_LINK,)),
        # Take special care in your code for FontStyle.
        XDW_ATN_FontStyle           : (0, XDW_FONT_STYLE, (
                                        XDW_AID_TEXT, XDW_AID_LINK,
                                        )),
        XDW_ATN_ForeColor           : (0, XDW_COLOR, (
                                        XDW_AID_TEXT, XDW_AID_LINK,
                                        )),
        XDW_ATN_GUID                : (0, None, ()),
        XDW_ATN_ImageFile           : (1, None, ()),
        XDW_ATN_Invisible           : (0, None, (XDW_AID_LINK,)),
        XDW_ATN_LeftRightMargin     : (0, "mm", ()),
        # 1 <= LineSpace <= 10
        XDW_ATN_LineSpace           : (0, "1/100line", (XDW_AID_TEXT,)),
        XDW_ATN_LinkAtn_Title       : (1, None, (XDW_AID_LINK,)),
        XDW_ATN_LinkType            : (0, XDW_LINK_TYPE, (XDW_AID_LINK,)),
        XDW_ATN_MailAddress         : (1, None, (XDW_AID_LINK,)),
        XDW_ATN_MonthField          : (1, None, (XDW_AID_STAMP,)),
        XDW_ATN_OtherFilePath       : (1, None, (XDW_AID_LINK,)),
        XDW_ATN_OtherFilePath_Relative  : (0, None, (XDW_AID_LINK,)),
        XDW_ATN_PageFrom            : (0, None, (XDW_AID_LINK,)),
        XDW_ATN_PageRange           : (0, XDW_PAGERANGE, ()),
        # TODO: TREAT Points SPECIALLY
        XDW_ATN_Points              : (2, "1/100mm", (XDW_AID_STRAIGHTLINE,
                                                 XDW_AID_MARKER,
                                                 XDW_AID_POLYGON,)),
        XDW_ATN_ShowIcon            : (0, None, (XDW_AID_LINK,)),
        XDW_ATN_StartingNumber      : (0, None, ()),
        XDW_ATN_Text                : (1, None, (XDW_AID_TEXT,)),
        XDW_ATN_TextAutoResizeHeight    : (0, None, (XDW_AID_TEXT,)),
        # 0 <= TextBottomMargin <= 2000
        XDW_ATN_TextBottomMargin    : (0, "1/100mm", (XDW_AID_TEXT,)),
        XDW_ATN_TextDirection       : (0, None, (XDW_AID_TEXT,)),
        # 0 <= TextLeftMargin <= 2000
        XDW_ATN_TextLeftMargin      : (0, "1/100mm", (XDW_AID_TEXT,)),
        XDW_ATN_TextOrientation     : (0, None, (XDW_AID_TEXT,)),
        # 0 <= TextRightMargin <= 2000
        XDW_ATN_TextRightMargin     : (0, "1/100mm", (XDW_AID_TEXT,)),
        XDW_ATN_TextSpacing         : (0, "1/10char", (XDW_AID_TEXT,)),
        # 0 <= TextTopMargin <= 2000
        XDW_ATN_TextTopMargin       : (0, "1/100mm", (XDW_AID_TEXT,)),
        XDW_ATN_Tooltip             : (0, None, (XDW_AID_LINK,)),
        XDW_ATN_Tooltip_String      : (1, None, (XDW_AID_LINK,)),
        XDW_ATN_TopBottomMargin     : (0, "mm", ()),
        XDW_ATN_TopField            : (1, None, (XDW_AID_STAMP,)),
        XDW_ATN_Url                 : (1, None, (XDW_AID_LINK,)),
        XDW_ATN_VerPosition         : (0, XDW_ALIGN_VPOS, ()),
        XDW_ATN_WordWrap            : (0, None, (XDW_AID_TEXT,)),
        XDW_ATN_XdwLink             : (0, None, (XDW_AID_LINK,)),
        XDW_ATN_XdwNameInXbd        : (1, None, (XDW_AID_LINK,)),
        XDW_ATN_XdwPage             : (0, None, (XDW_AID_LINK,)),
        XDW_ATN_XdwPath             : (1, None, (XDW_AID_LINK,)),
        XDW_ATN_XdwPath_Relative    : (0, None, (XDW_AID_LINK,)),
        XDW_ATN_YearField           : (1, None, (XDW_AID_STAMP,)),
        XDW_ATN_Zoom                : (0, "%", ()),
        }


######################################################################
### STRUCTURES #######################################################

### C types and structures used in xdwapi.dll

XDW_HGLOBAL = c_void_p
XDW_WCHAR = c_wchar
XDW_DOCUMENT_HANDLE = POINTER(c_int)
XDW_CREATE_HANDLE = POINTER(c_int)
XDW_ANNOTATION_HANDLE = POINTER(c_int)
XDW_FOUND_HANDLE = POINTER(c_int)


class SizedStructure(Structure):
    """ctypes.Structure with setting self.nSize automatically."""
    def __init__(self):
        Structure.__init__(self)
        self.nSize = sizeof(self)


class ResizedStructure(SizedStructure):
    def __init__(self):
        SizedStructure.__init__(self)
        self.common.nSize = sizeof(self)


class XDW_RECT(Structure):
    _fields_ = [
        ("left", c_long),
        ("top", c_long),
        ("right", c_long),
        ("bottom", c_long),
        ]


class XDW_GPTI_OCRTEXT_UNIT(Structure):
    _fields_ = [
        ("lpszText", c_char_p),
        ("rect", XDW_RECT),
        ]


class XDW_GPTI_OCRTEXT(Structure):
    _fields_ = [
        ("nUnitNum", c_int),
        ("pUnits", POINTER(XDW_GPTI_OCRTEXT_UNIT)),
        ]


class XDW_GPTI_INFO(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nInfoType", c_int),
        ("nPageWidth", c_int),
        ("nPageHeight", c_int),
        ("nRotateDegree", c_int),
        ("nDataSize", c_int),
        ("pData", XDW_HGLOBAL),
        ]


class XDW_DOCUMENT_INFO(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nPages", c_int),
        ("nVersion", c_int),
        ("nOriginalData", c_int),
        ("nDocType", c_int),
        ("nPermission", c_int),
        ("nShowAnnotations", c_int),
        ("nDocuments", c_int),
        ("nBinderColor", c_int),
        ("nBinderSize", c_int),
        ]


class XDW_PAGE_INFO(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nWidth", c_int),
        ("nHeight", c_int),
        ("nPageType", c_int),
        ("nHorRes", c_int),
        ("nVerRes", c_int),
        ("nCompressType", c_int),
        ("nAnnotations", c_int),
        ]


class XDW_PAGE_INFO_EX(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nWidth", c_int),
        ("nHeight", c_int),
        ("nPageType", c_int),
        ("nHorRes", c_int),
        ("nVerRes", c_int),
        ("nCompressType", c_int),
        ("nAnnotations", c_int),
        ("nDegree", c_int),
        ("nOrgWidth", c_int),
        ("nOrgHeight", c_int),
        ("nOrgHorRes", c_int),
        ("nOrgVerRes", c_int),
        ("nImageWidth", c_int),
        ("nImageHeight", c_int),
        ]


class XDW_IMAGE_OPTION(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nDpi", c_int),
        ("nColor", c_int),
        ]


class XDW_OPEN_MODE(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nOption", c_int),
        ]


class XDW_OPEN_MODE_EX(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nOption", c_int),
        ("nAuthMode", c_int),
        ]


class XDW_CREATE_OPTION(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nFitImage", c_int),
        ("nCompress", c_int),
        ("nZoom", c_int),
        ("nWidth", c_int),
        ("nHeight", c_int),
        ("nHorPos", c_int),
        ("nVerPos", c_int),
        ]


class XDW_CREATE_OPTION_EX(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nFitImage", c_int),
        ("nCompress", c_int),
        ("nZoom", c_int),
        ("nWidth", c_int),
        ("nHeight", c_int),
        ("nHorPos", c_int),
        ("nVerPos", c_int),
        ("nZoomDetail", c_int),
        ]


class XDW_CREATE_OPTION_EX2(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nFitImage", c_int),
        ("nCompress", c_int),
        ("nZoom", c_int),
        ("nWidth", c_int),
        ("nHeight", c_int),
        ("nHorPos", c_int),
        ("nVerPos", c_int),
        ("nZoomDetail", c_int),
        ("nMaxPaperSize", c_int),
        ]


XDW_SIZEOF_ORGDATANAME = 256


class XDW_ORGDATA_INFO(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nDataSize", c_int),
        ("nDate", c_long),
        ("szName", c_char * XDW_SIZEOF_ORGDATANAME),
        ]


class XDW_ORGDATA_INFOW(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nDataSize", c_int),
        ("nDate", c_long),
        ("szName", XDW_WCHAR * XDW_SIZEOF_ORGDATANAME),
        ]


XDW_SIZEOF_LINKROOTFOLDER = 256


class XDW_LINKROOTFOLDER_INFO(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("szPath", c_char * XDW_SIZEOF_LINKROOTFOLDER),
        ("szLinkRootFolderName", c_char * XDW_SIZEOF_LINKROOTFOLDER),
        ]


class XDW_CREATE_STATUS(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("phase", c_int),
        ("nTotalPage", c_int),
        ("nPage", c_int),
        ]


class XDW_ANNOTATION_INFO(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("handle", XDW_ANNOTATION_HANDLE),
        ("nHorPos", c_int),
        ("nVerPos", c_int),
        ("nWidth", c_int),
        ("nHeight", c_int),
        ("nAnnotationType", c_int),
        ("nChildAnnotations", c_int),
        ]


class XDW_AA_INITIAL_DATA(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nAnnotationType", c_int),
        ("nReserved1", c_int),
        ("nReserved2", c_int),
        ]


class XDW_AA_FUSEN_INITIAL_DATA(ResizedStructure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nWidth", c_int),
        ("nHeight", c_int),
        ]


class XDW_AA_STRAIGHTLINE_INITIAL_DATA(ResizedStructure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nHorVec", c_int),
        ("nVerVec", c_int),
        ]


class XDW_AA_RECT_INITIAL_DATA(ResizedStructure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nWidth", c_int),
        ("nHeight", c_int),
        ]


class XDW_AA_ARC_INITIAL_DATA(ResizedStructure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nWidth", c_int),
        ("nHeight", c_int),
        ]


class XDW_AA_BITMAP_INITIAL_DATA(ResizedStructure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("szImagePath", c_char * 256),
        ]


class XDW_AA_BITMAP_INITIAL_DATAW(ResizedStructure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("szImagePath", c_wchar * 256),
        ]


class XDW_AA_STAMP_INITIAL_DATA(ResizedStructure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nWidth", c_int),
        ]


class XDW_AA_RECEIVEDSTAMP_INITIAL_DATA(ResizedStructure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nWidth", c_int),
        ]


XDW_SIZEOF_GUID = 36


class XDW_AA_CUSTOM_INITIAL_DATA(ResizedStructure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nWidth", c_int),
        ("nHeight", c_int),
        ("lpszGuid", c_char_p),
        ("nCustomDataSize", c_int),
        ("pCustomData", c_char_p),
        ]


class XDW_IMAGE_OPTION_EX(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nDpi", c_int),
        ("nColor", c_int),
        ("nImageType", c_int),
        ("pDetailOption", c_void_p),
        ]


class XDW_IMAGE_OPTION_TIFF(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nCompress", c_int),
        ("nEndOfMultiPages", c_int),
        ]


class XDW_IMAGE_OPTION_JPEG(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nCompress", c_int),
        ]


class XDW_IMAGE_OPTION_PDF(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nCompress", c_int),
        ("nConvertMethod", c_int),
        ("nEndOfMultiPages", c_int),
        ]


class XDW_BINDER_INITIAL_DATA(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nBinderColor", c_int),
        ("nBinderSize", c_int),
        ]


class XDW_OCR_OPTION_V4(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nNoiseReduction", c_int),
        ("nLanguage", c_int),
        ("nInsertSpaceCharacter", c_int),
        ("nJapaneseKnowledgeProcessing", c_int),
        ("nForm", c_int),
        ("nColumn", c_int),
        ("nDisplayProcess", c_int),
        ("nAutoDeskew", c_int),
        ]


class XDW_OCR_OPTION_V5(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nNoiseReduction", c_int),
        ("nLanguage", c_int),
        ("nInsertSpaceCharacter", c_int),
        ("nJapaneseKnowledgeProcessing", c_int),
        ("nForm", c_int),
        ("nColumn", c_int),
        ("nDisplayProcess", c_int),
        ("nAutoDeskew", c_int),
        ("nAreaNum", c_uint),
        ("pAreaRects", POINTER(POINTER(XDW_RECT))),
        ]


class XDW_OCR_OPTION_V5_EX(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nNoiseReduction", c_int),
        ("nLanguage", c_int),
        ("nInsertSpaceCharacter", c_int),
        ("nJapaneseKnowledgeProcessing", c_int),
        ("nForm", c_int),
        ("nColumn", c_int),
        ("nDisplayProcess", c_int),
        ("nAutoDeskew", c_int),
        ("nAreaNum", c_uint),
        ("pAreaRects", POINTER(POINTER(XDW_RECT))),
        ("nPriority", c_int),
        ]


class XDW_OCR_OPTION_V7(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nNoiseReduction", c_int),
        ("nLanguage", c_int),
        ("nInsertSpaceCharacter", c_int),
        ("nJapaneseKnowledgeProcessing", c_int),
        ("nForm", c_int),
        ("nColumn", c_int),
        ("nDisplayProcess", c_int),
        ("nAutoDeskew", c_int),
        ("nAreaNum", c_uint),
        ("pAreaRects", POINTER(POINTER(XDW_RECT))),
        ("nPriority", c_int),
        ("nEngineLevel", c_int),
        ("nLanguageMixedRate", c_int),
        ("nHalfSizeChar", c_int),
        ]


class XDW_OCR_OPTION_V9(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nNoiseReduction", c_int),
        ("nLanguage", c_int),
        ("nInsertSpaceCharacter", c_int),
        ("nForm", c_int),
        ("nColumn", c_int),
        ("nDisplayProcess", c_int),
        ("nAutoDeskew", c_int),
        ("nAreaNum", c_uint),
        ("pAreaRects", POINTER(POINTER(XDW_RECT))),
        ("nPriority", c_int),
        ("nEngineLevel", c_int),
        ("nHalfSizeChar", c_int)
        ]


class XDW_OCR_OPTION_WRP(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nNoiseReduction", c_int),
        ("nLanguage", c_int),
        ("nInsertSpaceCharacter", c_int),
        ("nForm", c_int),
        ("nColumn", c_int),
        ("nAutoDeskew", c_int),
        ("nPriority", c_int),
        ]


class XDW_OCR_OPTION_FRE(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nNoiseReduction", c_int),
        ("nLanguage", c_int),
        ("nDocumentType", c_int),
        ("nDisplayProcess", c_int),
        ("nAutoDeskew", c_int),
        ("nAreaNum", c_uint),
        ("pAreaRects", POINTER(POINTER(XDW_RECT))),
        ("nPriority", c_int),
        ]


class XDW_OCR_OPTION_FRE_V7(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nNoiseReduction", c_int),
        ("nLanguage", c_int),
        ("nDocumentType", c_int),
        ("nDisplayProcess", c_int),
        ("nAutoDeskew", c_int),
        ("nAreaNum", c_uint),
        ("pAreaRects", POINTER(POINTER(XDW_RECT))),
        ("nPriority", c_int),
        ("nEngineLevel", c_int),
        ]


class XDW_PAGE_COLOR_INFO(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nColor", c_int),
        ("nImageDepth", c_int),
        ]


XDW_SIZEOF_PSWD = 256


class XDW_SECURITY_OPTION_PSWD(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nPermission", c_int),
        ("szOpenPswd", c_char * XDW_SIZEOF_PSWD),
        ("szFullAccessPswd", c_char * XDW_SIZEOF_PSWD),
        ("lpszComment", c_char_p),
        ]


class XDW_DER_CERTIFICATE(Structure):
    _fields_ = [
        ("pCert", c_void_p),
        ("nCertSize", c_int),
        ]


class XDW_SECURITY_OPTION_PKI(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nPermission", c_int),
        ("lpxdcCerts", POINTER(XDW_DER_CERTIFICATE)),
        ("nCertsNum", c_int),
        ("nFullAccessCertsNum", c_int),
        ("nErrorStatus", c_int),
        ("nFirstErrorCert", c_int),
        ]


class XDW_PROTECT_OPTION(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nAuthMode", c_int),
        ]


class XDW_RELEASE_PROTECTION_OPTION(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nAuthMode", c_int),
        ]


class XDW_PROTECTION_INFO(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nProtectType", c_int),
        ("nPermission", c_int),
        ]


class XDW_SIGNATURE_OPTION_V5(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nPage", c_int),
        ("nHorPos", c_int),
        ("nVerPos", c_int),
        ("nSignatureType", c_int),
        ]


class XDW_SIGNATURE_INFO_V5(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nSignatureType", c_int),
        ("nPage", c_int),
        ("nHorPos", c_int),
        ("nVerPos", c_int),
        ("nWidth", c_int),
        ("nHeight", c_int),
        ("nSignedTime", c_long),
        ]


class XDW_SIGNATURE_MODULE_STATUS(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nSignatureType", c_int),
        ("nErrorStatus", c_int),
        ]


class XDW_SIGNATURE_MODULE_OPTION_PKI(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("pSignerCert", c_void_p),
        ("nSignerCertSize", c_int),
        ]


XDW_SIZEOF_STAMPNAME = 256
XDW_SIZEOF_STAMPOWNERNAME = 64
XDW_SIZEOF_STAMPREMARKS = 1024


class XDW_SIGNATURE_STAMP_INFO_V5(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("lpszStampName", c_char * XDW_SIZEOF_STAMPNAME),
        ("lpszOwnerName", c_char * XDW_SIZEOF_STAMPOWNERNAME),
        ("nValidDate", c_long),
        ("lpszRemarks", c_char * XDW_SIZEOF_STAMPREMARKS),
        ("nDocVerificationStatus", c_int),
        ("nStampVerificationStatus", c_int),
        ]


XDW_SIZEOF_PKIMODULENAME    = 16
XDW_SIZEOF_PKISUBJECTDN     = 512
XDW_SIZEOF_PKISUBJECT       = 256
XDW_SIZEOF_PKIISSUERDN      = 512
XDW_SIZEOF_PKIISSUER        = 256
XDW_SIZEOF_PKINOTBEFORE     = 32
XDW_SIZEOF_PKINOTAFTER      = 32
XDW_SIZEOF_PKISERIAL        = 64
XDW_SIZEOF_PKIREMARKS       = 64
XDW_SIZEOF_PKISIGNEDTIME    = 32


class XDW_SIGNATURE_PKI_INFO_V5(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("lpszModule", c_char * XDW_SIZEOF_PKIMODULENAME),
        ("lpszSubjectDN", c_char * XDW_SIZEOF_PKISUBJECTDN),
        ("lpszSubject", c_char * XDW_SIZEOF_PKISUBJECT),
        ("lpszIssuerDN", c_char * XDW_SIZEOF_PKIISSUERDN),
        ("lpszIssuer", c_char * XDW_SIZEOF_PKIISSUER),
        ("lpszNotBefore", c_char * XDW_SIZEOF_PKINOTBEFORE),
        ("lpszNotAfter", c_char * XDW_SIZEOF_PKINOTAFTER),
        ("lpszSerial", c_char * XDW_SIZEOF_PKISERIAL),
        ("pSignerCert", c_void_p),
        ("nSignerCertSize", c_int),
        ("lpszRemarks", c_char * XDW_SIZEOF_PKIREMARKS),
        ("lpszSigningTime", c_char * XDW_SIZEOF_PKISIGNEDTIME),
        ("nDocVerificationStatus", c_int),
        ("nCertVerificationType", c_int),
        ("nCertVerificationStatus", c_int),
        ]


class XDW_OCR_TEXTINFO(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nWidth", c_int),
        ("nHeight", c_int),
        ("charset", c_long),
        ("lpszText", c_char_p),
        ("nLineRect", c_int),
        ("pLineRect", POINTER(XDW_RECT)),
        ]


class XDW_OCRIMAGE_OPTION(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nDpi", c_int),
        ("nNoiseReduction", c_int),
        ("nPriority", c_int),
        ]


class XDW_FIND_TEXT_OPTION(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("nIgnoreMode", c_int),
        ("nReserved", c_int),
        ("nReserved2", c_int),
        ]


XDW_FOUND_RECT_STATUS_HIT = 0
XDW_FOUND_RECT_STATUS_PAGE = 1


class XDW_POINT(Structure):
    _fields_ = [
        ("x", c_long),
        ("y", c_long),
        ]


class XDW_AA_MARKER_INITIAL_DATA(ResizedStructure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nCounts", c_int),
        ("pPoints", POINTER(XDW_POINT)),
        ]


class XDW_AA_POLYGON_INITIAL_DATA(ResizedStructure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nCounts", c_int),
        ("pPoints", POINTER(XDW_POINT)),
        ]


XDW_AID_INITIAL_DATA = {
        XDW_AID_FUSEN           : XDW_AA_FUSEN_INITIAL_DATA,
        XDW_AID_TEXT            : None,
        XDW_AID_STAMP           : XDW_AA_STAMP_INITIAL_DATA,
        XDW_AID_STRAIGHTLINE    : XDW_AA_STRAIGHTLINE_INITIAL_DATA,
        XDW_AID_RECTANGLE       : XDW_AA_RECT_INITIAL_DATA,
        XDW_AID_ARC             : XDW_AA_ARC_INITIAL_DATA,
        XDW_AID_POLYGON         : XDW_AA_POLYGON_INITIAL_DATA,
        XDW_AID_MARKER          : XDW_AA_MARKER_INITIAL_DATA,
        XDW_AID_LINK            : None,
        XDW_AID_PAGEFORM        : None,
        XDW_AID_OLE             : None,
        XDW_AID_BITMAP          : (XDW_AA_BITMAP_INITIAL_DATA if XDWVER < 8
                                   else XDW_AA_BITMAP_INITIAL_DATAW),
        XDW_AID_RECEIVEDSTAMP   : XDW_AA_RECEIVEDSTAMP_INITIAL_DATA,
        XDW_AID_CUSTOM          : XDW_AA_CUSTOM_INITIAL_DATA,
        XDW_AID_TITLE           : None,
        XDW_AID_GROUP           : None,
        }


######################################################################

### API ##############################################################

### decorators and utility functions

from functools import wraps

NULL = None  # or POINTER(c_int)()


def ptr(obj):
    return byref(obj) if obj else NULL


def RAISE(api):
    @wraps(api)
    def apifunc(*args):
        result = api(*args)
        if result & 0x80000000:
            raise XDWErrorFactory(result)
        return result
    return apifunc


@RAISE
def TRY(api, *args):
    return api(*args)


def APPEND(*ext, **kw):
    """Decorator to call XDWAPI with trailing arguments *ext.

    N.B. Decorated function must be of the same name as XDWAPI's one.
    """
    def deco(api):
        @wraps(api)
        def func(*args, **kw):
            args = list(args)
            if "codepage" in kw:
                args.append(kw["codepage"])
            args.extend(ext)
            return TRY(getattr(DLL, api.__name__), *args)
        return func
    return deco


def QUERY(struct, *ext):
    """Decorator to call XDWAPI querying XDW_* struct data.

    N.B. Decorated function must be of the same name as XDWAPI's one.
    """
    def deco(api):
        @wraps(api)
        def func(*args):
            result = struct()
            args = list(args)
            args.append(byref(result))
            args.extend(ext)
            TRY(getattr(DLL, api.__name__), *args)
            return result
        return func
    return deco


def STRING(api):
    """Decorator to get a string value via XDWAPI.

    N.B. Decorated function must be of the same name as XDWAPI's one.
    """
    @wraps(api)
    def func(*args):
        args = list(args)
        args.extend([NULL, 0, NULL])
        size = TRY(getattr(DLL, api.__name__), *args)
        buf = create_string_buffer(size)
        args[-3:] = [byref(buf), size, NULL]
        TRY(getattr(DLL, api.__name__), *args)
        return buf.value
    return func


def UNICODE(api):
    """Decorator to get a unicode (wchar) string value via XDWAPI.

    N.B. Decorated function must be of the same name as XDWAPI's one.
    """
    @wraps(api)
    def func(*args):
        args = list(args)
        args.extend([NULL, 0, NULL])
        size = TRY(getattr(DLL, api.__name__), *args)
        buf = create_unicode_buffer(size)
        args[-3:] = [byref(buf), size, NULL]
        TRY(getattr(DLL, api.__name__), *args)
        return buf.value
    return func


def ATTR(byorder=False, widename=False, multitype=False, widevalue=False):
    """Decorator to get document attribute via XDWAPI.

    N.B. Decorated function must be of the same name as XDWAPI's one.
    """
    def deco(api):
        @wraps(api)
        def func(*args, **kw):
            args = list(args)
            codepage = kw.get("codepage", CP)
            def create_buffer(wide):
                return create_unicode_buffer if wide else create_string_buffer
            # Pass 1 - get the size of value.
            if byorder:
                attrname = create_buffer(widename)(256)
                args.append(byref(attrname))
            if multitype:
                attrtype = c_int()
                args.append(byref(attrtype))
            else:
                attrtype = c_int(XDW_ANNOTATION_ATTRIBUTE[args[1]][0])
            if widevalue:
                texttype = c_int()
                args.extend([NULL, 0, byref(texttype), codepage])
            else:
                args.extend([NULL, 0])
            args.append(NULL)
            size = TRY(getattr(DLL, api.__name__), *args)
            # Pass 2 - read the actual value.
            if attrtype.value in (XDW_ATYPE_INT, XDW_ATYPE_DATE,
                                  XDW_ATYPE_BOOL, XDW_ATYPE_OCTS):
                attrvalue = c_int()
            elif attrtype.value == XDW_ATYPE_STRING:
                attrvalue = create_buffer(
                        multitype and widename or widevalue)(size)
            else:  # if attrtype.value == XDW_ATYPE_OTHER:
                attrvalue = (XDW_POINT * int(size / sizeof(XDW_POINT)))()
            if widevalue:
                args[-5:-3] = [byref(attrvalue), size]
            else:
                args[-3:-1] = [byref(attrvalue), size]
            TRY(getattr(DLL, api.__name__), *args)
            # Build the result.
            result = []
            if byorder:
                result.append(attrname.value)
            result.extend([attrtype.value, attrvalue.value])
            if widevalue:
                result.append(texttype.value)
            return tuple(result)
            # (name*, type, value, text_type*), *=optional
        return func
    return deco


def XDWVERSION(ver):
    """Decorator to indicate if the following function is valid or not."""
    def deco(api):
        if ver <= XDWVER:
            @wraps(api)
            def func(*args):
                return api(*args)
            return func
        else:
            @wraps(api)
            def func(*args):
                raise NotImplementedError
            return func
    return deco


### DocuWorks API's provided by xdwapi.dll

@STRING
def XDW_GetInformation(index): pass

@XDWVERSION(8)
@UNICODE
def XDW_GetInformationW(index): pass

@APPEND(NULL)
def XDW_AddSystemFolder(index): pass

@RAISE
def XDW_MergeXdwFiles(input_paths, output_path):
    n = len(input_paths)
    _input_paths = (c_char_p * n)(*input_paths)
    return DLL.XDW_MergeXdwFiles(ptr(_input_paths), n, output_path, NULL)

@XDWVERSION(8)
@RAISE
def XDW_MergeXdwFilesW(input_paths, output_path):
    n = len(input_paths)
    _input_paths = (c_wchar_p * n)(*input_paths)
    return DLL.XDW_MergeXdwFilesW(ptr(_input_paths), n, output_path, NULL)

def XDW_OpenDocumentHandle(path, open_mode):
    doc_handle = XDW_DOCUMENT_HANDLE()
    TRY(DLL.XDW_OpenDocumentHandle, path, byref(doc_handle), byref(open_mode))
    return doc_handle

@XDWVERSION(8)
def XDW_OpenDocumentHandleW(path, open_mode):
    doc_handle = XDW_DOCUMENT_HANDLE()
    TRY(DLL.XDW_OpenDocumentHandleW, path, byref(doc_handle), byref(open_mode))
    return doc_handle

@XDWVERSION(9)
def XDW_OpenDocumentHandleEx(path, open_mode):
    doc_handle = XDW_DOCUMENT_HANDLE()
    TRY(DLL.XDW_OpenDocumentHandleEx, path, byref(doc_handle), byref(open_mode))
    return doc_handle

@XDWVERSION(9)
def XDW_OpenDocumentHandleExW(path, open_mode):
    doc_handle = XDW_DOCUMENT_HANDLE()
    TRY(DLL.XDW_OpenDocumentHandleExW, path, byref(doc_handle), byref(open_mode))
    return doc_handle

@APPEND(NULL)
def XDW_CloseDocumentHandle(doc_handle): pass

@QUERY(XDW_DOCUMENT_INFO)
def XDW_GetDocumentInformation(doc_handle): pass

def XDW_GetPageInformation(doc_handle, page, extend=False):
    page_info = XDW_PAGE_INFO_EX() if extend else XDW_PAGE_INFO()
    TRY(DLL.XDW_GetPageInformation, doc_handle, page, byref(page_info))
    return page_info

@APPEND(NULL)
def XDW_GetPageImage(doc_handle, page, output_path): pass

@XDWVERSION(8)
@APPEND(NULL)
def XDW_GetPageImageW(doc_handle, page, output_path): pass

@APPEND(NULL)
def XDW_GetPageText(doc_handle, page, output_path): pass

@RAISE
def XDW_ConvertPageToImageFile(doc_handle, page, output_path, img_option):
    return DLL.XDW_ConvertPageToImageFile(doc_handle, page, output_path, byref(img_option))

@XDWVERSION(8)
@RAISE
def XDW_ConvertPageToImageFileW(doc_handle, page, output_path, img_option):
    return DLL.XDW_ConvertPageToImageFileW(doc_handle, page, output_path, byref(img_option))

@APPEND(NULL)
def XDW_GetPage(doc_handle, page, output_path): pass

@XDWVERSION(8)
@APPEND(NULL)
def XDW_GetPageW(doc_handle, page, output_path): pass

@APPEND(NULL)
def XDW_DeletePage(doc_handle, page): pass

@APPEND(NULL)
def XDW_RotatePage(doc_handle, page, degree): pass

@APPEND(NULL)
def XDW_SaveDocument(doc_handle): pass

@RAISE
def XDW_CreateXdwFromImageFile(input_path, output_path, cre_option):
    return DLL.XDW_CreateXdwFromImageFile(input_path, output_path, byref(cre_option))

@XDWVERSION(8)
@RAISE
def XDW_CreateXdwFromImageFileW(input_path, output_path, cre_option):
    return DLL.XDW_CreateXdwFromImageFileW(input_path, output_path, byref(cre_option))

@QUERY(XDW_ORGDATA_INFO, NULL)
def XDW_GetOriginalDataInformation(doc_handle, org_dat): pass

@APPEND(NULL)
def XDW_GetOriginalData(doc_handle, org_dat, output_path): pass

@XDWVERSION(8)
@APPEND(NULL)
def XDW_GetOriginalDataW(doc_handle, org_dat, output_path): pass

@APPEND(NULL)
def XDW_InsertOriginalData(doc_handle, org_dat, input_path): pass

@APPEND(NULL)
def XDW_DeleteOriginalData(doc_handle, org_dat): pass

@QUERY(XDW_CREATE_HANDLE, NULL)
def XDW_BeginCreationFromAppFile(input_path, output_path, with_org): pass

@XDWVERSION(8)
@QUERY(XDW_CREATE_HANDLE, NULL)
def XDW_BeginCreationFromAppFileW(input_path, output_path, with_org): pass

@APPEND(NULL)
def XDW_EndCreationFromAppFile(cre_handle): pass

@QUERY(XDW_CREATE_STATUS)
def XDW_GetStatusCreationFromAppFile(cre_handle): pass

@APPEND(NULL)
def XDW_CancelCreationFromAppFile(cre_handle): pass

@STRING
def XDW_GetUserAttribute(doc_handle, attr_name): pass

@RAISE
def XDW_SetUserAttribute(doc_handle, attr_name, attr_val):
    return DLL.XDW_SetUserAttribute(doc_handle, attr_name, attr_val, len(attr_val or b""), NULL)

@QUERY(XDW_ANNOTATION_INFO, NULL)
def XDW_GetAnnotationInformation(doc_handle, page, parent_ann_handle, index): pass

@ATTR
def XDW_GetAnnotationAttribute(ann_handle, attr_name): pass

def XDW_AddAnnotation(doc_handle, ann_type, page, hpos, vpos, init_dat):
    new_ann_handle = XDW_ANNOTATION_HANDLE()
    TRY(DLL.XDW_AddAnnotation, doc_handle, ann_type, page, hpos, vpos, ptr(init_dat), byref(new_ann_handle), NULL)
    return new_ann_handle

@APPEND(NULL)
def XDW_RemoveAnnotation(doc_handle, ann_handle): pass

@APPEND(0, NULL)
def XDW_SetAnnotationAttribute(doc_handle, ann_handle, attr_name, attr_type, attr_val): pass

@APPEND(NULL)
def XDW_SetAnnotationSize(doc_handle, ann_handle, width, height): pass

@APPEND(NULL)
def XDW_SetAnnotationPosition(doc_handle, ann_handle, hpos, vpos): pass

if XDWVER < 9:

    @APPEND(NULL)
    def XDW_CreateSfxDocument(input_path, output_path): pass

    @XDWVERSION(8)
    @APPEND(NULL)
    def XDW_CreateSfxDocumentW(input_path, output_path): pass

else:

    def XDW_CreateSfxDocument(*args, **kw):
        raise NotImplementedError

    XDW_CreateSfxDocumentW = XDW_CreateSfxDocument


@APPEND(NULL)
def XDW_ExtractFromSfxDocument(input_path, output_path): pass

@XDWVERSION(8)
@APPEND(NULL)
def XDW_ExtractFromSfxDocumentW(input_path, output_path): pass

def XDW_ConvertPageToImageHandle(doc_handle, page, img_option):
    handle = XDW_HGLOBAL()
    TRY(DLL.XDW_ConvertPageToImageHandle, doc_handle, page, byref(handle), byref(img_option))
    windll.kernel32.GlobalLock.argtypes = [c_void_p]
    windll.kernel32.GlobalLock.restype = c_void_p
    bitmap = Bitmap(windll.kernel32.GlobalLock(handle))
    windll.kernel32.GlobalFree(handle)
    return bitmap

def XDW_GetThumbnailImageHandle(doc_handle, page):
    """XDW_GetThumbnailImageHandle(doc_handle, page) --> Bitmap"""
    handle = XDW_HGLOBAL()
    TRY(DLL.XDW_GetThumbnailImageHandle, doc_handle, page, byref(handle), NULL)
    windll.kernel32.GlobalLock.argtypes = [c_void_p]
    windll.kernel32.GlobalLock.restype = c_void_p
    bitmap = Bitmap(windll.kernel32.GlobalLock(handle))
    bitmap.header.biXPelsPerMeter = 492  # pixels/m = 12.5 dpi
    bitmap.header.biYPelsPerMeter = 492  # pixels/m = 12.5 dpi
    windll.kernel32.GlobalFree(handle)
    return bitmap

@STRING
def XDW_GetPageTextToMemory(doc_handle, page): pass

@APPEND(NULL)
def XDW_GetFullText(doc_handle, output_path): pass

@STRING
def XDW_GetPageUserAttribute(doc_handle, page, attr_name): pass

@RAISE
def XDW_SetPageUserAttribute(doc_handle, page, attr_name, attr_val):
    return DLL.XDW_SetPageUserAttribute(doc_handle, page, attr_name, attr_val, len(attr_val or b""), NULL)

@APPEND(NULL)
def XDW_ReducePageNoise(doc_handle, page, level): pass

@APPEND(NULL)
def XDW_ShowOrHideAnnotations(doc_handle, show_annotations): pass

@APPEND(NULL)
def XDW_GetCompressedPageImage(doc_handle, page, output_path): pass

@XDWVERSION(8)
@APPEND(NULL)
def XDW_GetCompressedPageImageW(doc_handle, page, output_path): pass

@APPEND(NULL)
def XDW_InsertDocument(doc_handle, page, input_path): pass

@XDWVERSION(8)
@APPEND(NULL)
def XDW_InsertDocumentW(doc_handle, page, input_path): pass

@RAISE
def XDW_ApplyOcr(doc_handle, page, ocr_engine, option):
    return DLL.XDW_ApplyOcr(doc_handle, page, ocr_engine, ptr(option), NULL)

@APPEND(NULL)
def XDW_RotatePageAuto(doc_handle, page): pass

@RAISE
def XDW_CreateBinder(output_path, binder_init_dat):
    return DLL.XDW_CreateBinder(output_path, ptr(binder_init_dat), NULL)

@XDWVERSION(8)
@RAISE
def XDW_CreateBinderW(output_path, binder_init_dat):
    return DLL.XDW_CreateBinderW(output_path, ptr(binder_init_dat), NULL)

@APPEND(NULL)
def XDW_InsertDocumentToBinder(doc_handle, pos, input_path): pass

@APPEND(NULL)
def XDW_GetDocumentFromBinder(doc_handle, pos, output_path): pass

@XDWVERSION(8)
@APPEND(NULL)
def XDW_GetDocumentFromBinderW(doc_handle, pos, output_path): pass

@APPEND(NULL)
def XDW_DeleteDocumentInBinder(doc_handle, pos): pass

@STRING
def XDW_GetDocumentNameInBinder(doc_handle, pos): pass

@APPEND(NULL)
def XDW_SetDocumentNameInBinder(doc_handle, pos, doc_name): pass

@QUERY(XDW_DOCUMENT_INFO, NULL)
def XDW_GetDocumentInformationInBinder(doc_handle, pos): pass

@APPEND(NULL)
def XDW_Finalize(): pass

@QUERY(XDW_PAGE_COLOR_INFO, NULL)
def XDW_GetPageColorInformation(doc_handle, page): pass

@APPEND(NULL)
def XDW_OptimizeDocument(input_path, output_path): pass

@XDWVERSION(8)
@APPEND(NULL)
def XDW_OptimizeDocumentW(input_path, output_path): pass

@RAISE
def XDW_ProtectDocument(input_path, output_path, protect_type, module_option, protect_option):
    return DLL.XDW_ProtectDocument(input_path, output_path, protect_type, byref(module_option), byref(protect_option))

@XDWVERSION(8)
@RAISE
def XDW_ProtectDocumentW(input_path, output_path, protect_type, module_option, protect_option):
    return DLL.XDW_ProtectDocumentW(input_path, output_path, protect_type, byref(module_option), byref(protect_option))

@RAISE
def XDW_CreateXdwFromImageFileAndInsertDocument(doc_handle, page, input_path, create_option):
    return DLL.XDW_CreateXdwFromImageFileAndInsertDocument(doc_handle, page, input_path, byref(create_option), NULL)

@XDWVERSION(8)
@RAISE
def XDW_CreateXdwFromImageFileAndInsertDocumentW(doc_handle, page, input_path, create_option):
    return DLL.XDW_CreateXdwFromImageFileAndInsertDocumentW(doc_handle, page, input_path, byref(create_option), NULL)

@APPEND(NULL)
def XDW_GetDocumentAttributeNumber(doc_handle): pass

@ATTR(multitype=True)
def XDW_GetDocumentAttributeByName(doc_handle, attr_name): pass

@ATTR(byorder=True, multitype=True)
def XDW_GetDocumentAttributeByOrder(doc_handle, order): pass

@APPEND(NULL)
def XDW_SetDocumentAttribute(doc_handle, attr_name, attr_type, attr_val): pass

@APPEND(NULL)
def XDW_SucceedAttribute(doc_handle, file_path, document, succession): pass

@XDWVERSION(8)
@APPEND(NULL)
def XDW_SucceedAttributeW(doc_handle, file_path, document, succession): pass

@STRING
def XDW_GetPageFormAttribute(doc_handle, page_form, attr_name): pass

@APPEND(0, NULL)
def XDW_SetPageFormAttribute(doc_handle, page_form, attr_name, attr_type, attr_val): pass

@APPEND(NULL)
def XDW_UpdatePageForm(doc_handle, other_page_form): pass

@APPEND(NULL)
def XDW_RemovePageForm(doc_handle, other_page_form): pass

@QUERY(XDW_LINKROOTFOLDER_INFO, NULL)
def XDW_GetLinkRootFolderInformation(order): pass

class XDW_LINKROOTFOLDER_INFOW(SizedStructure):
    _fields_ = [
        ("nSize", c_int),
        ("szPath", c_wchar * XDW_SIZEOF_LINKROOTFOLDER),
        ("szLinkRootFolderName", c_wchar * XDW_SIZEOF_LINKROOTFOLDER),
        ]

@XDWVERSION(8)
@QUERY(XDW_LINKROOTFOLDER_INFOW, NULL)
def XDW_GetLinkRootFolderInformationW(order): pass

@APPEND(NULL)
def XDW_GetLinkRootFolderNumber(): pass

@XDWVERSION(8)
@APPEND(NULL)
def XDW_GetLinkRootFolderNumberW(): pass

# Undocumented API in DocuWorksTM Development Tool Kit 7.1
# int XDWAPI XDW_GetPageTextInformation(XDW_DOCUMENT_HANDLE handle, int nPage, void* pInfo, void* reserved);

def XDW_GetPageTextInformation(doc_handle, page):
    gpti_info = XDW_GPTI_INFO()  # right?
    TRY(DLL.XDW_GetPageTextInformation, doc_handle, page, byref(gpti_info), NULL)
    return gpti_info

@APPEND(NULL)
def XDW_GetDocumentSignatureNumber(doc_handle): pass

def XDW_AddAnnotationOnParentAnnotation(doc_handle, ann_handle, ann_type, hpos, vpos, init_dat):
    new_ann_handle = XDW_ANNOTATION_HANDLE()
    TRY(DLL.XDW_AddAnnotationOnParentAnnotation, doc_handle, ann_handle, ann_type, hpos, vpos, ptr(init_dat), byref(new_ann_handle), NULL)
    return new_ann_handle

@RAISE
def XDW_SignDocument(input_path, output_path, option, module_option):
    module_status = XDW_SIGNATURE_MODULE_STATUS()
    try:
        TRY(DLL.XDW_SignDocument, input_path, output_path, ptr(option), ptr(module_option), NULL, ptr(module_status))
    except SignatureModuleError as e:
        if module_status.nSignatureType == XDW_SIGNATURE_STAMP:
            msg = XDW_SIGNATURE_STAMP_ERROR[module_status.nErrorStatus]
        else:
            msg = XDW_SIGNATURE_PKI_ERROR[module_status.nErrorStatus]
        raise SignatureModuleError(msg)
    return 0

@XDWVERSION(8)
@RAISE
def XDW_SignDocumentW(input_path, output_path, option, module_option):
    module_status = XDW_SIGNATURE_MODULE_STATUS()
    try:
        TRY(DLL.XDW_SignDocumentW, input_path, output_path, ptr(option), ptr(module_option), NULL, ptr(module_status))
    except SignatureModuleError as e:
        if module_status.nSignatureType == XDW_SIGNATURE_STAMP:
            msg = XDW_SIGNATURE_STAMP_ERROR[module_status.nErrorStatus]
        else:
            msg = XDW_SIGNATURE_PKI_ERROR[module_status.nErrorStatus]
        raise SignatureModuleError(msg)
    return 0

def XDW_GetSignatureInformation(doc_handle, pos):
    """XDW_GetSignatureInformation(doc_handle, pos) --> (signature_info, module_info)

    For PKI based signatures, returning module_info contains additional attribute
    `signer_cert', which provides actual certificate as a DER (RFC3280) formatted str.
    Note that accessing module_info.pSignerCert is expected to raise error like GPE.
    """
    signature_info = XDW_SIGNATURE_INFO_V5()
    TRY(DLL.XDW_GetSignatureInformation, doc_handle, pos, byref(signature_info), NULL, NULL, NULL)
    if signature_info.nSignatureType == XDW_SIGNATURE_STAMP:
        module_info = XDW_SIGNATURE_STAMP_INFO_V5()
        module_status = XDW_SIGNATURE_MODULE_STATUS()
        try:
            TRY(DLL.XDW_GetSignatureInformation, doc_handle, pos, ptr(signature_info), ptr(module_info), NULL, ptr(module_status))
        except SignatureModuleError as e:
            raise SignatureModuleError("signature type {0}, error status {1}".format(
                    module_status.nSignatureType, module_status.nErrorStatus))
        # N.B. signature_info.nSignedTime is UTC Unix time.
        return (signature_info, module_info)
    else:  # signature_info.nSignatureType == XDW_SIGNATURE_PKI
        module_info = XDW_SIGNATURE_PKI_INFO_V5()
        module_status = XDW_SIGNATURE_MODULE_STATUS()
        try:  # Try to get certificate size.
            #module_info.pSignerCert = NULL
            TRY(DLL.XDW_GetSignatureInformation, doc_handle, pos, ptr(signature_info), ptr(module_info), NULL, ptr(module_status))
        except SignatureModuleError as e:
            raise SignatureModuleError("signature type {0}, error status {1}".format( module_status.nSignatureType, module_status.nErrorStatus))
        signer_cert = c_char * module_info.nSignerCertSize
        module_info.pSignerCert = byref(signer_cert)
        try:  # Actually get certificate and other attributes.
            TRY(DLL.XDW_GetSignatureInformation, doc_handle, pos, ptr(signature_info), ptr(module_info), NULL, ptr(module_status))
        except SignatureModuleError as e:
            raise SignatureModuleError("signature type {0}, error status {1}".format(module_status.nSignatureType, module_status.nErrorStatus))
        # N.B. signature_info.nSignedTime is UTC Unix time.
        module_info.signer_cert = signer_cert
        return (signature_info, module_info)

@RAISE
def XDW_UpdateSignatureStatus(doc_handle, pos, module_option, module_status):
    """The 3rd argument, module_option, should currently be specified as NULL."""
    module_status = XDW_SIGNATURE_MODULE_STATUS()
    try:
        TRY(DLL.XDW_UpdateSignatureStatus, doc_handle, pos, NULL, NULL, ptr(module_status))
    except SignatureModuleError as e:
        raise SignatureModuleError("signature type {0}, error status {1}".format(module_status.nSignatureType, module_status.nErrorStatus))
    # Note that signature information (XDW_GetSignatureInformation()) may be altered.
    return module_status

@RAISE
def XDW_GetOcrImage(doc_handle, page, output_path, img_option):
    return DLL.XDW_GetOcrImage(doc_handle, page, output_path, byref(img_option), NULL)

@XDWVERSION(8)
@RAISE
def XDW_GetOcrImageW(doc_handle, page, output_path, img_option):
    return DLL.XDW_GetOcrImageW(doc_handle, page, output_path, byref(img_option), NULL)

def XDW_SetOcrData(doc_handle, page, ocr_textinfo):
    TRY(DLL.XDW_SetOcrData, doc_handle, page, byref(ocr_textinfo) if ocr_textinfo else NULL, NULL)

@APPEND(NULL)
def XDW_GetDocumentAttributeNumberInBinder(doc_handle, pos): pass

@ATTR(multitype=True)
def XDW_GetDocumentAttributeByNameInBinder(doc_handle, pos, attr_name): pass

@ATTR(byorder=True, multitype=True)
def XDW_GetDocumentAttributeByOrderInBinder(doc_handle, pos, order): pass

#int XDWAPI XDW_GetTMInfo(doc_handle, void* pTMInfo, int nTMInfoSize, void* reserved);
#int XDWAPI XDW_SetTMInfo(doc_handle, const void* pTMInfo, int nTMInfoSize, void* reserved);

@APPEND(NULL)
def XDW_CreateXdwFromImagePdfFile(input_path, output_path): pass

def XDW_FindTextInPage(doc_handle, page, text, find_text_option):
    found_handle = XDW_FOUND_HANDLE()
    TRY(DLL.XDW_FindTextInPage, doc_handle, page, text, ptr(find_text_option), byref(found_handle), NULL)
    return found_handle

def XDW_FindNext(found_handle):
    TRY(DLL.XDW_FindNext, byref(found_handle), NULL)
    return found_handle

@RAISE
def XDW_GetNumberOfRectsInFoundObject(found_handle):
    return DLL.XDW_GetNumberOfRectsInFoundObject(found_handle, NULL)

def XDW_GetRectInFoundObject(found_handle, pos):
    rect = XDW_RECT()
    status = c_int()
    TRY(DLL.XDW_GetRectInFoundObject, found_handle, pos, byref(rect), byref(status), NULL)
    return (rect, status.value)

@RAISE
def XDW_CloseFoundHandle(found_handle):
    return DLL.XDW_CloseFoundHandle(found_handle)

@STRING
def XDW_GetAnnotationUserAttribute(ann_handle, attr_name): pass

@RAISE
def XDW_SetAnnotationUserAttribute(doc_handle, ann_handle, attr_name, attr_val):
    return DLL.XDW_SetAnnotationUserAttribute(doc_handle, ann_handle, attr_name, attr_val, len(attr_val or b""), NULL)

@APPEND(NULL)
def XDW_StarchAnnotation(doc_handle, ann_handle, starch): pass

@RAISE
def XDW_ReleaseProtectionOfDocument(input_path, output_path, release_protection_option):
    return DLL.XDW_ReleaseProtectionOfDocument(input_path, output_path, byref(release_protection_option))

@XDWVERSION(8)
@RAISE
def XDW_ReleaseProtectionOfDocumentW(input_path, output_path, release_protection_option):
    return DLL.XDW_ReleaseProtectionOfDocumentW(input_path, output_path, byref(release_protection_option))

@QUERY(XDW_PROTECTION_INFO, NULL)
def XDW_GetProtectionInformation(input_path): pass

@XDWVERSION(8)
@QUERY(XDW_PROTECTION_INFO, NULL)
def XDW_GetProtectionInformationW(input_path): pass

@ATTR(widename=True, multitype=True)
def XDW_GetAnnotationCustomAttributeByName(ann_handle, attr_name): pass

@ATTR(byorder=True, widename=True, multitype=True)
def XDW_GetAnnotationCustomAttributeByOrder(ann_handle, order): pass

@APPEND(NULL)
def XDW_GetAnnotationCustomAttributeNumber(ann_handle): pass

@RAISE
def XDW_SetAnnotationCustomAttribute(doc_handle, ann_handle, attr_name, attr_type, attr_val):
    return DLL.XDW_SetAnnotationCustomAttribute(doc_handle, ann_handle, attr_name, attr_type, attr_val, NULL)

@UNICODE
def XDW_GetPageTextToMemoryW(doc_handle, page): pass

@APPEND(NULL)
def XDW_GetFullTextW(doc_handle, output_path): pass

@ATTR(widevalue=True)
def XDW_GetAnnotationAttributeW(ann_handle, attr_name, codepage=CP): pass

@APPEND(0, NULL)
def XDW_SetAnnotationAttributeW(doc_handle, ann_handle, attr_name, attr_type, attr_val, text_type, codepage=CP): pass

@ATTR(widename=True, multitype=True, widevalue=True)
def XDW_GetDocumentAttributeByNameW(doc_handle, attr_name, codepage=CP): pass

@ATTR(byorder=True, widename=True, multitype=True, widevalue=True)
def XDW_GetDocumentAttributeByOrderW(doc_handle, order, codepage=CP): pass

@ATTR(widename=True, multitype=True, widevalue=True)
def XDW_GetDocumentAttributeByNameInBinderW(doc_handle, pos, attr_name, codepage=CP): pass

@ATTR(byorder=True, multitype=True, widevalue=True)
def XDW_GetDocumentAttributeByOrderInBinderW(doc_handle, pos, order, codepage=CP): pass

@APPEND(NULL)
def XDW_SetDocumentAttributeW(doc_handle, attr_name, attr_type, attr_val, text_type, codepage=CP): pass

def XDW_GetDocumentNameInBinderW(doc_handle, pos, codepage=CP):
    text_type = c_int()
    size = TRY(DLL.XDW_GetDocumentNameInBinderW, doc_handle, pos, NULL, 0, byref(text_type), codepage, NULL)
    doc_name = create_unicode_buffer(size)
    TRY(DLL.XDW_GetDocumentNameInBinderW, doc_handle, pos, byref(doc_name), size, byref(text_type), codepage, NULL)
    return (doc_name.value, text_type.value)

@APPEND(NULL)
def XDW_SetDocumentNameInBinderW(doc_handle, pos, doc_name, text_type, codepage=CP): pass

def XDW_GetOriginalDataInformationW(doc_handle, org_data, codepage=CP):
    text_type = c_int()
    orgdata_infow = XDW_ORGDATA_INFOW()
    TRY(DLL.XDW_GetOriginalDataInformationW, doc_handle, org_data, byref(orgdata_infow), byref(text_type), codepage, NULL)
    return (orgdata_infow, text_type.value)  # N.B. orgdata_infow.nDate is UTC Unix time.

@XDWVERSION(8)
@QUERY(XDW_ANNOTATION_HANDLE, NULL)
def XDW_AddAnnotationFromAnnFile(doc_handle, ann_file_path, index, page, ann_handle, hpos, vpos): pass

@XDWVERSION(8)
@QUERY(XDW_ANNOTATION_HANDLE, NULL)
def XDW_AddAnnotationFromAnnFileW(doc_handle, ann_file_path, index, page, ann_handle, hpos, vpos): pass

@XDWVERSION(8)
def XDW_GroupAnnotations(doc_handle, page, ann_handle, indexes):
    new_ann_handle = XDW_ANNOTATION_HANDLE()
    count = len(indexes)
    indexlist = (c_int * count)(*indexes)
    TRY(DLL.XDW_GroupAnnotations, doc_handle, page, ann_handle, byref(indexlist), count, byref(new_ann_handle), NULL)
    return new_ann_handle

@XDWVERSION(8)
@APPEND(NULL)
def XDW_UnGroupAnnotation(doc_handle, ann_handle): pass
