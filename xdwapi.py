#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""xdwapi.py -- DocuWorks API

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE. 
"""

from ctypes import *

DLL = windll.LoadLibrary("xdwapi.dll")


# decorators and utility functions

NULL = None  # or POINTER(c_int)()

def ptr(obj):
    return byref(obj) if obj else NULL

def RAISE(api):
    def apifunc(*args):
        result = api(*args)
        if result & 0x80000000:
            raise XDWError(result)
        return result
    return apifunc

@RAISE
def TRY(api, *args):
    return api(*args)

def APPEND(*ext):
    """Decorator to call XDWAPI with trailing arguments *ext.

    NB. Decorated function must be of the same name as XDWAPI's one.
    """
    def deco(api):
        def func(*args):
            args = list(args)
            args.extend(ext)
            return TRY(getattr(DLL, api.__name__), *args)
        return func
    return deco

def STRING(api):
    """Decorator to get a string value via XDWAPI.

    NB. Decorated function must be of the same name as XDWAPI's one.
    """
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

    NB. Decorated function must be of the same name as XDWAPI's one.
    """
    def func(*args):
        args = list(args)
        args.extend([NULL, 0, NULL])
        size = TRY(getattr(DLL, api.__name__), *args)
        buf = create_unicode_buffer(size)
        args[-3:] = [byref(buf), size, NULL]
        TRY(getattr(DLL, api.__name__), *args)
        return buf.value
    return func


# DocuWorks error

class XDWError(Exception):

    messages = {
        0x80040001: "XDW_E_NOT_INSTALLED",
        0x80040002: "XDW_E_INFO_NOT_FOUND",
        0x8007007A: "XDW_E_INSUFFICIENT_BUFFER",
        0x80070002: "XDW_E_FILE_NOT_FOUND",
        0x80070050: "XDW_E_FILE_EXISTS",
        0x80070005: "XDW_E_ACCESSDENIED",
        0x8007000B: "XDW_E_BAD_FORMAT",
        0x8007000E: "XDW_E_OUTOFMEMORY",
        0x8007001D: "XDW_E_WRITE_FAULT",
        0x80070020: "XDW_E_SHARING_VIOLATION",
        0x80070027: "XDW_E_DISK_FULL",
        0x80070057: "XDW_E_INVALIDARG",
        0x8007007B: "XDW_E_INVALID_NAME",
        0x80040003: "XDW_E_INVALID_ACCESS",
        0x80040004: "XDW_E_INVALID_OPERATION",
        0x800E0004: "XDW_E_NEWFORMAT",
        0x800E0005: "XDW_E_BAD_NETPATH",
        0x80001156: "XDW_E_APPLICATION_FAILED",
        0x800E0010: "XDW_E_SIGNATURE_MODULE",
        0x800E0012: "XDW_E_PROTECT_MODULE",
        0x8000FFFF: "XDW_E_UNEXPECTED",
        0x80040005: "XDW_E_CANCELED",
        0x80040006: "XDW_E_ANNOTATION_NOT_ACCEPTED",
        }

    def __init__(self, error_code):
        error_code = (error_code + 0x100000000) & 0xffffffff
        msg = XDWError.messages.get(error_code, "XDW_E_UNDEFINED")
        Exception.__init__(self, "%s (%08X)" % (msg, error_code))


# DocuWorks constants

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
XDW_GI_DWDESK_FILENAME_DELIMITER    = 1001
XDW_GI_DWDESK_FILENAME_DIGITS       = 1002

XDW_PGT_NULL                        = 0
XDW_PGT_FROMIMAGE                   = 1
XDW_PGT_FROMAPPL                    = 2

XDW_MAXPATH                         = 255
XDW_MAXINPUTIMAGEPATH               = 127

XDW_OPEN_READONLY                   = 0
XDW_OPEN_UPDATE                     = 1

XDW_AUTH_NONE                       = 0
XDW_AUTH_NODIALOGUE                 = 1
XDW_AUTH_CONDITIONAL_DIALOGUE       = 2

XDW_PERM_DOC_EDIT                   = 0x02
XDW_PERM_ANNO_EDIT                  = 0x04
XDW_PERM_PRINT                      = 0x08
XDW_PERM_COPY                       = 0x10

XDW_DT_DOCUMENT                     = 0
XDW_DT_BINDER                       = 1

XDW_ROT_0                           = 0
XDW_ROT_90                          = 90
XDW_ROT_180                         = 180
XDW_ROT_270                         = 270

XDW_CREATE_FITDEF                   = 0
XDW_CREATE_FIT                      = 1
XDW_CREATE_USERDEF                  = 2
XDW_CREATE_USERDEF_FIT              = 3
XDW_CREATE_FITDEF_DIVIDEBMP         = 4

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

XDW_CONVERT_MRC_ORIGINAL            = 0
XDW_CONVERT_MRC_OS                  = 1

XDW_IMAGE_DIB                       = 0
XDW_IMAGE_TIFF                      = 1
XDW_IMAGE_JPEG                      = 2
XDW_IMAGE_PDF                       = 3

XDW_CREATE_HCENTER                  = 0
XDW_CREATE_LEFT                     = 1
XDW_CREATE_RIGHT                    = 2

XDW_CREATE_VCENTER                  = 0
XDW_CREATE_TOP                      = 1
XDW_CREATE_BOTTOM                   = 2

XDW_CREATE_DEFAULT_SIZE             = 0
XDW_CREATE_A3_SIZE                  = 1
XDW_CREATE_2A0_SIZE                 = 2

XDW_LINE_NONE                       = 0
XDW_LINE_BEGINNING                  = 1
XDW_LINE_ENDING                     = 2
XDW_LINE_BOTH                       = 3
XDW_LINE_WIDE_POLYLINE              = 0
XDW_LINE_POLYLINE                   = 1
XDW_LINE_POLYGON                    = 2

XDW_BORDER_TYPE_SOLID               = 0
XDW_BORDER_TYPE_DOT                 = 1
XDW_BORDER_TYPE_DASH                = 2
XDW_BORDER_TYPE_DASHDOT             = 3
XDW_BORDER_TYPE_DOUBLE              = 4

XDW_STAMP_AUTO                      = 0
XDW_STAMP_MANUAL                    = 1
XDW_STAMP_NO_BASISYEAR              = 0
XDW_STAMP_BASISYEAR                 = 1
XDW_STAMP_DATE_YMD                  = 0
XDW_STAMP_DATE_DMY                  = 1

XDW_PAGEFORM_HEADER                 = 0
XDW_PAGEFORM_FOOTER                 = 1
XDW_PAGEFORM_TOPIMAGE               = 2
XDW_PAGEFORM_BOTTOMIMAGE            = 3
XDW_PAGEFORM_PAGENUMBER             = 4

XDW_PAGEFORM_STAY                   = 0
XDW_PAGEFORM_REMOVE                 = 1

XDW_ALIGN_LEFT                      = 0
XDW_ALIGN_HCENTER                   = 1
XDW_ALIGN_RIGHT                     = 2
XDW_ALIGN_TOP                       = 0
XDW_ALIGN_BOTTOM                    = 1
XDW_ALIGN_VCENTER                   = 2

XDW_PAGERANGE_ALL                   = 0
XDW_PAGERANGE_SPECIFIED             = 1

XDW_CRTP_BEGINNING                  = 1
XDW_CRTP_PRINTING                   = 2
XDW_CRTP_PAGE_CREATING              = 3
XDW_CRTP_ORIGINAL_APPENDING         = 4
XDW_CRTP_WRITING                    = 5
XDW_CRTP_ENDING                     = 6
XDW_CRTP_CANCELING                  = 7
XDW_CRTP_FINISHED                   = 8
XDW_CRTP_CANCELED                   = 9

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

XDW_ATYPE_INT                       = 0
XDW_ATYPE_STRING                    = 1
XDW_ATYPE_DATE                      = 2
XDW_ATYPE_BOOL                      = 3
XDW_ATYPE_OCTS                      = 4
XDW_ATYPE_OTHER                     = 999

XDW_SUMMARY_INFO        = 1
XDW_USER_DEF            = 2
XDW_ANNOTATION          = 4

XDW_SIZE_FREE           = 0
XDW_SIZE_A3_PORTRAIT    = 1
XDW_SIZE_A3_LANDSCAPE   = 2
XDW_SIZE_A4_PORTRAIT    = 3
XDW_SIZE_A4_LANDSCAPE   = 4
XDW_SIZE_A5_PORTRAIT    = 5
XDW_SIZE_A5_LANDSCAPE   = 6
XDW_SIZE_B4_PORTRAIT    = 7
XDW_SIZE_B4_LANDSCAPE   = 8
XDW_SIZE_B5_PORTRAIT    = 9
XDW_SIZE_B5_LANDSCAPE   = 10

XDW_BINDER_COLOR_0      = 0
XDW_BINDER_COLOR_1      = 1
XDW_BINDER_COLOR_2      = 2
XDW_BINDER_COLOR_3      = 3
XDW_BINDER_COLOR_4      = 4
XDW_BINDER_COLOR_5      = 5
XDW_BINDER_COLOR_6      = 6
XDW_BINDER_COLOR_7      = 7
XDW_BINDER_COLOR_8      = 8
XDW_BINDER_COLOR_9      = 9
XDW_BINDER_COLOR_10     = 10
XDW_BINDER_COLOR_11     = 11
XDW_BINDER_COLOR_12     = 12
XDW_BINDER_COLOR_13     = 13
XDW_BINDER_COLOR_14     = 14
XDW_BINDER_COLOR_15     = 15

XDW_REDUCENOISE_NONE    = 0
XDW_REDUCENOISE_NORMAL  = 1
XDW_REDUCENOISE_WEAK    = 2
XDW_REDUCENOISE_STRONG  = 3

XDW_PRIORITY_NONE           = 0
XDW_PRIORITY_SPEED          = 1
XDW_PRIORITY_RECOGNITION    = 2

XDW_OCR_ENGINE_V4                               = 1  # old name - should be here for = compatibility
XDW_OCR_ENGINE_DEFAULT                          = 1
XDW_OCR_ENGINE_WRP                              = 2
XDW_OCR_ENGINE_FRE                              = 3

XDW_OCR_LANGUAGE_AUTO                           = -1
XDW_OCR_LANGUAGE_JAPANESE                       = 0
XDW_OCR_LANGUAGE_ENGLISH                        = 1

XDW_OCR_MULTIPLELANGUAGES_ENGLISH               = 0x02
XDW_OCR_MULTIPLELANGUAGES_FRENCH                = 0x04
XDW_OCR_MULTIPLELANGUAGES_SIMPLIFIED_CHINESE    = 0x08
XDW_OCR_MULTIPLELANGUAGES_TRADITIONAL_CHINESE   = 0x10
XDW_OCR_MULTIPLELANGUAGES_THAI                  = 0x20

XDW_OCR_FORM_AUTO                               = 0
XDW_OCR_FORM_TABLE                              = 1
XDW_OCR_FORM_WRITING                            = 2

XDW_OCR_COLUMN_AUTO                             = 0
XDW_OCR_COLUMN_HORIZONTAL_SINGLE                = 1
XDW_OCR_COLUMN_HORIZONTAL_MULTI                 = 2
XDW_OCR_COLUMN_VERTICAL_SINGLE                  = 3
XDW_OCR_COLUMN_VERTICAL_MULTI                   = 4

XDW_OCR_DOCTYPE_AUTO                            = 0
XDW_OCR_DOCTYPE_HORIZONTAL_SINGLE               = 1
XDW_OCR_DOCTYPE_PLAINTEXT                       = 2

XDW_OCR_ENGINE_LEVEL_SPEED                      = 1
XDW_OCR_ENGINE_LEVEL_STANDARD                   = 2
XDW_OCR_ENGINE_LEVEL_ACCURACY                   = 3

XDW_OCR_MIXEDRATE_JAPANESE                      = 1
XDW_OCR_MIXEDRATE_BALANCED                      = 2
XDW_OCR_MIXEDRATE_ENGLISH                       = 3

XDW_PROTECT_PSWD            = 1
XDW_PROTECT_PSWD128         = 3
XDW_PROTECT_PKI             = 4
XDW_PROTECT_STAMP           = 5
XDW_PROTECT_CONTEXT_SERVICE = 6

XDW_GPTI_TYPE_EMF           = 0
XDW_GPTI_TYPE_OCRTEXT       = 1

XDW_IMAGE_MONO              = 0
XDW_IMAGE_COLOR             = 1
XDW_IMAGE_MONO_HIGHQUALITY  = 2

XDW_SIGNATURE_STAMP                                     = 100
XDW_SIGNATURE_PKI                                       = 102

XDW_SIGNATURE_STAMP_DOC_NONE                            = 0
XDW_SIGNATURE_STAMP_DOC_NOEDIT                          = 1
XDW_SIGNATURE_STAMP_DOC_EDIT                            = 2
XDW_SIGNATURE_STAMP_DOC_BAD                             = 3

XDW_SIGNATURE_STAMP_STAMP_NONE                          = 0
XDW_SIGNATURE_STAMP_STAMP_TRUSTED                       = 1
XDW_SIGNATURE_STAMP_STAMP_NOTRUST                       = 2

XDW_SIGNATURE_STAMP_ERROR_OK                            = 0
XDW_SIGNATURE_STAMP_ERROR_NO_OPENING_CASE               = 1
XDW_SIGNATURE_STAMP_ERROR_NO_SELFSTAMP                  = 2
XDW_SIGNATURE_STAMP_ERROR_OUT_OF_VALIDITY               = 3
XDW_SIGNATURE_STAMP_ERROR_INVALID_DATA                  = 4
XDW_SIGNATURE_STAMP_ERROR_OUT_OF_MEMORY                 = 100
XDW_SIGNATURE_STAMP_ERROR_UNKNOWN                       = 9999

XDW_SIGNATURE_PKI_DOC_UNKNOWN                           = 0
XDW_SIGNATURE_PKI_DOC_GOOD                              = 1
XDW_SIGNATURE_PKI_DOC_MODIFIED                          = 2
XDW_SIGNATURE_PKI_DOC_BAD                               = 3
XDW_SIGNATURE_PKI_DOC_GOOD_TRUSTED                      = 4
XDW_SIGNATURE_PKI_DOC_MODIFIED_TRUSTED                  = 5

XDW_SIGNATURE_PKI_TYPE_LOW                              = 0
XDW_SIGNATURE_PKI_TYPE_MID_LOCAL                        = 1
XDW_SIGNATURE_PKI_TYPE_MID_NETWORK                      = 2
XDW_SIGNATURE_PKI_TYPE_HIGH_LOCAL                       = 3
XDW_SIGNATURE_PKI_TYPE_HIGH_NETWORK                     = 4

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

XDW_SECURITY_PKI_ERROR_UNKNOWN                  = 0
XDW_SECURITY_PKI_ERROR_OK                       = 1
XDW_SECURITY_PKI_ERROR_BAD_PLATFORM             = 2
XDW_SECURITY_PKI_ERROR_WRITE_REG_ERROR          = 3
XDW_SECURITY_PKI_ERROR_BAD_TRUST_LEVEL          = 4
XDW_SECURITY_PKI_ERROR_BAD_REVOKE_CHECK_TYPE    = 5
XDW_SECURITY_PKI_ERROR_REVOKED                  = 6
XDW_SECURITY_PKI_ERROR_BAD_SIGN                 = 7
XDW_SECURITY_PKI_ERROR_REVOKE_CHECK_ERROR       = 8
XDW_SECURITY_PKI_ERROR_OUT_OF_VALIDITY          = 9
XDW_SECURITY_PKI_ERROR_NO_CERT                  = 10
XDW_SECURITY_PKI_ERROR_FAILURE_IMPORT_CERT      = 11
XDW_SECURITY_PKI_ERROR_NO_ROOT_CERT             = 12
XDW_SECURITY_PKI_ERROR_BAD_CERT_FORMAT          = 13
XDW_SECURITY_PKI_ERROR_BAD_CERT_USAGE           = 14
XDW_SECURITY_PKI_ERROR_CA_CERT_IS_REVOKED       = 15
XDW_SECURITY_PKI_ERROR_TOO_MANY_CERT            = 16

# Constants from xdwapian.h

XDW_IGNORE_CASE                 = 0x02
XDW_IGNORE_WIDTH                = 0x04
XDW_IGNORE_HIRAKATA             = 0x08

XDW_STARCH                      = 1
XDW_STARCH_OFF                  = 0

XDW_TEXT_UNKNOWN                = 0
XDW_TEXT_MULTIBYTE              = 1
XDW_TEXT_UNICODE                = 2
XDW_TEXT_UNICODE_IFNECESSARY    = 3

XDW_ATN_Text                    = "%Text"
XDW_ATN_FontName                = "%FontName"
XDW_ATN_FontStyle               = "%FontStyle"
XDW_ATN_FontSize                = "%FontSize"
XDW_ATN_ForeColor               = "%ForeColor"
XDW_ATN_FontPitchAndFamily      = "%FontPitchAndFamily"
XDW_ATN_FontCharSet             = "%FontCharSet"
XDW_ATN_BackColor               = "%BackColor"
XDW_ATN_Caption                 = "%Caption"
XDW_ATN_Url                     = "%Url"
XDW_ATN_XdwPath                 = "%XdwPath"
XDW_ATN_ShowIcon                = "%ShowIcon"
XDW_ATN_LinkType                = "%LinkType"
XDW_ATN_XdwPage                 = "%XdwPage"
XDW_ATN_Tooltip                 = "%Tooltip"
XDW_ATN_Tooltip_String          = "%TooltipString"
XDW_ATN_XdwPath_Relative        = "%XdwPathRelative"
XDW_ATN_XdwLink                 = "%XdwLink"
XDW_ATN_LinkAtn_Title           = "%LinkAtnTitle"
XDW_ATN_OtherFilePath           = "%OtherFilePath"
XDW_ATN_OtherFilePath_Relative  = "%OtherFilePathRelative"
XDW_ATN_MailAddress             = "%MailAddress"
XDW_ATN_BorderStyle             = "%BorderStyle"
XDW_ATN_BorderWidth             = "%BorderWidth"
XDW_ATN_BorderColor             = "%BorderColor"
XDW_ATN_BorderTransparent       = "%BorderTransparent"
XDW_ATN_BorderType              = "%BorderType"
XDW_ATN_FillStyle               = "%FillStyle"
XDW_ATN_FillColor               = "%FillColor"
XDW_ATN_FillTransparent         = "%FillTransparent"
XDW_ATN_ArrowheadType           = "%ArrowheadType"
XDW_ATN_ArrowheadStyle          = "%ArrowheadStyle"
XDW_ATN_WordWrap                = "%WordWrap"
XDW_ATN_TextDirection           = "%TextDirection"
XDW_ATN_TextOrientation         = "%TextOrientation"
XDW_ATN_LineSpace               = "%LineSpace"
XDW_ATN_AutoResize              = "%AutoResize"
XDW_ATN_Invisible               = "%Invisible"
XDW_ATN_PageFrom                = "%PageFrom"
XDW_ATN_XdwNameInXbd            = "%XdwNameInXbd"
XDW_ATN_TopField                = "%TopField"
XDW_ATN_BottomField             = "%BottomField"
XDW_ATN_DateStyle               = "%DateStyle"
XDW_ATN_YearField               = "%YearField"
XDW_ATN_MonthField              = "%MonthField"
XDW_ATN_DayField                = "%DayField"
XDW_ATN_BasisYearStyle          = "%BasisYearStyle"
XDW_ATN_BasisYear               = "%BasisYear"
XDW_ATN_DateField_FirstChar     = "%DateFieldFirstChar"
XDW_ATN_Alignment               = "%Alignment"
XDW_ATN_LeftRightMargin         = "%LeftRightMargin"
XDW_ATN_TopBottomMargin         = "%TopBottomMargin"
XDW_ATN_VerPosition             = "%VerPosition"
XDW_ATN_StartingNumber          = "%StartingNumber"
XDW_ATN_Digit                   = "%Digit"
XDW_ATN_PageRange               = "%PageRange"
XDW_ATN_BeginningPage           = "%BeginningPage"
XDW_ATN_EndingPage              = "%EndingPage"
XDW_ATN_Zoom                    = "%Zoom"
XDW_ATN_ImageFile               = "%ImageFile"
XDW_ATN_Points                  = "%Points"
XDW_ATN_DateFormat              = "%DateFormat"
XDW_ATN_DateOrder               = "%DateOrder"
XDW_ATN_TextSpacing             = "%Spacing"
XDW_ATN_TextTopMargin           = "%TopMargin"
XDW_ATN_TextLeftMargin          = "%LeftMargin"
XDW_ATN_TextBottomMargin        = "%BottomMargin"
XDW_ATN_TextRightMargin         = "%RightMargin"
XDW_ATN_TextAutoResizeHeight    = "%AutoResizeHeight"
XDW_ATN_GUID                    = "%CustomAnnGuid"
XDW_ATN_CustomData              = "%CustomAnnCustomData"

XDW_PROP_TITLE                  = "%Title"
XDW_PROP_SUBJECT                = "%Subject"
XDW_PROP_AUTHOR                 = "%Author"
XDW_PROP_KEYWORDS               = "%Keywords"
XDW_PROP_COMMENTS               = "%Comments"

XDW_PROPW_TITLE                 = "%Title"
XDW_PROPW_SUBJECT               = "%Subject"
XDW_PROPW_AUTHOR                = "%Author"
XDW_PROPW_KEYWORDS              = "%Keywords"
XDW_PROPW_COMMENTS              = "%Comments"

XDW_COLOR_NONE                  = 0x010101
XDW_COLOR_BLACK                 = 0x000000
XDW_COLOR_MAROON                = 0x000080
XDW_COLOR_GREEN                 = 0x008000
XDW_COLOR_OLIVE                 = 0x008080
XDW_COLOR_NAVY                  = 0x800000
XDW_COLOR_PURPLE                = 0x800080
XDW_COLOR_TEAL                  = 0x808000
XDW_COLOR_GRAY                  = 0x808080
XDW_COLOR_SILVER                = 0xC0C0C0
XDW_COLOR_RED                   = 0x0000FF
XDW_COLOR_LIME                  = 0x00FF00
XDW_COLOR_YELLOW                = 0x00FFFF
XDW_COLOR_BLUE                  = 0xFF0000
XDW_COLOR_FUCHIA                = 0xFF00FF
XDW_COLOR_AQUA                  = 0xFFFF00
XDW_COLOR_WHITE                 = 0xFFFFFF
XDW_COLOR_FUSEN_RED             = 0xFFC2FF
XDW_COLOR_FUSEN_BLUE            = 0xFFBF9D
XDW_COLOR_FUSEN_YELLOW          = 0x64FFFF
XDW_COLOR_FUSEN_LIME            = 0xC2FF9D
XDW_COLOR_FUSEN_PALE_RED        = 0xE1D7FF
XDW_COLOR_FUSEN_PALE_BLUE       = 0xFAE1C8
XDW_COLOR_FUSEN_PALE_YELLOW     = 0xC3FAFF
XDW_COLOR_FUSEN_PALE_LIME       = 0xD2FACD

XDW_FS_ITALIC_FLAG              = 1
XDW_FS_BOLD_FLAG                = 2
XDW_FS_UNDERLINE_FLAG           = 4
XDW_FS_STRIKEOUT_FLAG           = 8

XDW_LT_LINK_TO_ME               = 0
XDW_LT_LINK_TO_XDW              = 1
XDW_LT_LINK_TO_URL              = 2
XDW_LT_LINK_TO_OTHERFILE        = 3
XDW_LT_LINK_TO_MAILADDR         = 4

XDW_PF_XDW                      = 0
XDW_PF_XBD                      = 1
XDW_PF_XDW_IN_XBD               = 2


# C types and structures used in xdwapi.dll

XDW_HGLOBAL = c_void_p
XDW_WCHAR = c_wchar

class SizedStructure(Structure):
    """ctypes.Structure with setting self.nSize automatically."""
    def __init__(self):
        Structure.__init__(self)
        self.nSize = sizeof(self)

class XDW_DOCUMENT_HANDLE(Structure):
    _fields_ = [("dummy", c_int),]

class XDW_CREATE_HANDLE(Structure):
    _fields_ = [("dummy", c_int),]

class XDW_ANNOTATION_HANDLE(Structure):
    _fields_ = [("dummy", c_int),]

class XDW_FOUND_HANDLE(Structure):
    _fields_ = [("dummy", c_int),]

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

class XDW_AA_FUSEN_INITIAL_DATA(Structure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nWidth", c_int),
        ("nHeight", c_int),
        ]

class XDW_AA_STRAIGHTLINE_INITIAL_DATA(Structure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nHorVec", c_int),
        ("nVerVec", c_int),
        ]

class XDW_AA_RECT_INITIAL_DATA(Structure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nWidth", c_int),
        ("nHeight", c_int),
        ]

class XDW_AA_ARC_INITIAL_DATA(Structure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nWidth", c_int),
        ("nHeight", c_int),
        ]

class XDW_AA_BITMAP_INITIAL_DATA(Structure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("szImagePath", c_char * 256),
        ]

class XDW_AA_STAMP_INITIAL_DATA(Structure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nWidth", c_int),
        ]

class XDW_AA_RECEIVEDSTAMP_INITIAL_DATA(Structure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nWidth", c_int),
        ]

XDW_SIZEOF_GUID = 36
class XDW_AA_CUSTOM_INITIAL_DATA(Structure):
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
        ("x", c_int),
        ("y", c_int),
        ]

class XDW_AA_MARKER_INITIAL_DATA(Structure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nCounts", c_int),
        ("pPoints", POINTER(XDW_POINT)),
        ]

class XDW_AA_POLYGON_INITIAL_DATA(Structure):
    _fields_ = [
        ("common", XDW_AA_INITIAL_DATA),
        ("nCounts", c_int),
        ("pPoints", POINTER(XDW_POINT)),
        ]


# DocuWorks API's provided by xdwapi.dll

@STRING
def XDW_GetInformation(index):
    pass

@APPEND(NULL)
def XDW_AddSystemFolder(index):
    pass

@RAISE
def XDW_MergeXdwFiles(inputPaths, files, outputPath):
    input_paths = c_char_p() * len(inputPaths)
    for i in range(len(inputPaths)):
        input_paths[i] = byref(inputPaths[i])
    return DLL.XDW_MergeXdwFiles(input_paths, files, outputPath, NULL)

def XDW_OpenDocumentHandle(filePath, openMode):
    """XDW_OpenDocumentHandle(filePath, openMode) --> documentHandle"""
    documentHandle = XDW_DOCUMENT_HANDLE()
    if isinstance(filePath, unicode):
        filePath = filePath.encode("mbcs")
    TRY(DLL.XDW_OpenDocumentHandle, filePath, byref(documentHandle), byref(openMode))
    return documentHandle

@APPEND(NULL)
def XDW_CloseDocumentHandle(documentHandle):
    pass

def XDW_GetDocumentInformation(documentHandle):
    """XDW_GetDocumentInformation(handle) --> document_info"""
    documentInfo = XDW_DOCUMENT_INFO()
    TRY(DLL.XDW_GetDocumentInformation, documentHandle, byref(documentInfo))
    return documentInfo

def XDW_GetPageInformation(documentHandle, page, extend=False):
    """XDW_GetPageInformation(handle, page) --> page_info"""
    pageInfo = XDW_PAGE_INFO_EX() if extend else XDW_PAGE_INFO()
    TRY(DLL.XDW_GetPageInformation, documentHandle, page, byref(pageInfo))
    return pageInfo

@APPEND(NULL)
def XDW_GetPageImage(documentHandle, page, outputPath):
    pass

@APPEND(NULL)
def XDW_GetPageText(documentHandle, page, outputPath):
    pass

@RAISE
def XDW_ConvertPageToImageFile(documentHandle, page, outputPath, imageOption):
    return DLL.XDW_ConvertPageToImageFile(documentHandle, page, outputPath, byref(imageOption))

@APPEND(NULL)
def XDW_GetPage(documentHandle, page, outputPath):
    pass

@APPEND(NULL)
def XDW_DeletePage(documentHandle, page):
    pass

@APPEND(NULL)
def XDW_RotatePage(documentHandle, page, degree):
    pass

@APPEND(NULL)
def XDW_SaveDocument(documentHandle):
    pass

@RAISE
def XDW_CreateXdwFromImageFile(inputPath, outputPath, createOption):
    return DLL.XDW_CreateXdwFromImageFile(inputPath, outputPath, byref(createOption))

def XDW_GetOriginalDataInformation(documentHandle, originalData):
    """XDW_GetOriginalDataInformation(documentHandle, originalData) --> orgDataInfo"""
    orgDataInfo = XDW_ORGDATA_INFO()
    TRY(DLL.XDW_GetOriginalDataInformation, documentHandle, originalData, byref(orgDataInfo), NULL)
    return orgDataInfo

@APPEND(NULL)
def XDW_GetOriginalData(documentHandle, originalData, outputPath):
    pass

@APPEND(NULL)
def XDW_InsertOriginalData(documentHandle, originalData, inputPath):
    pass

@APPEND(NULL)
def XDW_DeleteOriginalData(documentHandle, originalData):
    pass

def XDW_BeginCreationFromAppFile(inputPath, outputPath, withOriginal):
    """XDW_BeginCreationFromAppFile(inputPath, outputPath, withOriginal) --> createHandle"""
    createHandle = XDW_CREATE_HANDLE()
    TRY(DLL.XDW_BeginCreationFromAppFile, inputPath, outputPath, withOriginal, byref(createHandle), NULL)
    return createHandle

@APPEND(NULL)
def XDW_EndCreationFromAppFile(createHandle):
    pass

def XDW_GetStatusCreationFromAppFile(createHandle):
    """XDW_GetStatusCreationFromAppFile(createHandle) --> createStatus"""
    createStatus = XDW_CREATE_STATUS()
    TRY(DLL.XDW_GetStatusCreationFromAppFile, createHandle, byref(createStatus))
    return createStatus

@APPEND(NULL)
def XDW_CancelCreationFromAppFile(createHandle):
    pass

@STRING
def XDW_GetUserAttribute(documentHandle, attributeName):
    pass

@RAISE
def XDW_SetUserAttribute(documentHandle, attributeName, attributeValue):
    size = attributeValue and len(attributeValue) or 0
    return DLL.XDW_SetUserAttribute(documentHandle, attributeName, attributeValue, size, NULL)

def XDW_GetAnnotationInformation(documentHandle, page, parent_annotationHandle, index):
    """XDW_GetAnnotationInformation(documentHandle, page, parent_annotationHandle, index) --> annotationInfo"""
    annotationInfo = XDW_ANNOTATION_INFO()
    TRY(DLL.XDW_GetAnnotationInformation, documentHandle, page, parent_annotationHandle, index, byref(annotationInfo), NULL)
    return annotationInfo

@STRING
def XDW_GetAnnotationAttribute(annotationHandle, attributeName):
    pass

def XDW_AddAnnotation(documentHandle, annotationType, page, horPos, verPos, initialData):
    """XDW_AddAnnotation(documentHandle, annotationType, page, horPos, verPos, initialData) --> new_annotationHandle"""
    new_annotationHandle = XDW_ANNOTATION_HANDLE()
    TRY(DLL.XDW_AddAnnotation, documentHandle, annotationType, page, horPos, verPos, ptr(initialData), byref(new_annotationHandle), NULL)
    return new_annotationHandle

@APPEND(NULL)
def XDW_RemoveAnnotation(documentHandle, annotationHandle):
    pass

@APPEND(0, NULL)
def XDW_SetAnnotationAttribute(documentHandle, annotationHandle, attributeName, attributeType, attributeValue):
    pass

@APPEND(NULL)
def XDW_SetAnnotationSize(documentHandle, annotationHandle, width, height):
    pass

@APPEND(NULL)
def XDW_SetAnnotationPosition(documentHandle, annotationHandle, horPos, verPos):
    pass

@APPEND(NULL)
def XDW_CreateSfxDocument(inputPath, outputPath):
    pass

@APPEND(NULL)
def XDW_ExtractFromSfxDocument(inputPath, outputPath):
    pass

def XDW_ConvertPageToImageHandle(documentHandle, page, imageOption):
    """XDW_ConvertPageToImageHandle(documentHandle, page, imageOption) --> dib"""
    dib = XDW_HGLOBAL()
    TRY(DLL.XDW_ConvertPageToImageHandle, documentHandle, page, byref(dib), byref(imageOption))
    return dib

def XDW_GetThumbnailImageHandle(documentHandle, page):
    """XDW_GetThumbnailImageHandle(documentHandle, page) --> dib"""
    dib = XDW_HGLOBAL()
    TRY(DLL.XDW_GetThumbnailImageHandle, documentHandle, page, byref(dib), NULL)
    return dib

@STRING
def XDW_GetPageTextToMemory(documentHandle, page):
    pass


@APPEND(NULL)
def XDW_GetFullText(documentHandle, outputPath):
    pass

@STRING
def XDW_GetPageUserAttribute(documentHandle, page, attributeName):
    pass

@RAISE
def XDW_SetPageUserAttribute(documentHandle, page, attributeName, attributeValue):
    size = attributeValue and len(attributeValue) or 0
    return DLL.XDW_SetPageUserAttribute(documentHandle, page, attributeName, attributeValue, size, NULL)

@APPEND(NULL)
def XDW_ReducePageNoise(documentHandle, page, level):
    pass

@APPEND(NULL)
def XDW_ShowOrHideAnnotations(documentHandle, showAnnotations):
    pass

@APPEND(NULL)
def XDW_GetCompressedPageImage(documentHandle, page, outputPath):
    pass

@APPEND(NULL)
def XDW_InsertDocument(documentHandle, page, inputPath):
    pass

@RAISE
def XDW_ApplyOcr(documentHandle, page, ocrEngine, option):
    return DLL.XDW_ApplyOcr(documentHandle, page, ocrEngine, ptr(option), NULL)

@APPEND(NULL)
def XDW_RotatePageAuto(documentHandle, page):
    pass

@RAISE
def XDW_CreateBinder(outputPath, binderInitialData):
    return DLL.XDW_CreateBinder(outputPath, ptr(binderInitialData), NULL)

@APPEND(NULL)
def XDW_InsertDocumentToBinder(documentHandle, position, inputPath):
    pass

@APPEND(NULL)
def XDW_GetDocumentFromBinder(documentHandle, position, outputPath):
    pass

@APPEND(NULL)
def XDW_DeleteDocumentInBinder(documentHandle, position):
    pass

@STRING
def XDW_GetDocumentNameInBinder(documentHandle, position):
    pass

@APPEND(NULL)
def XDW_SetDocumentNameInBinder(documentHandle, position, docName):
    pass

def XDW_GetDocumentInformationInBinder(documentHandle, position):
    """XDW_GetDocumentInformationInBinder(documentHandle, position) --> documentInfo"""
    documentInfo = XDW_DOCUMENT_INFO()
    TRY(DLL.XDW_GetDocumentInformationInBinder, documentHandle, position, byref(documentInfo), NULL)
    return documentInfo

@APPEND(NULL)
def XDW_Finalize():
    pass

@RAISE
def XDW_GetPageColorInformation(documentHandle, page):
    """XDW_GetPageColorInformation(documentHandle, page) --> pageColorInfo"""
    pageColorInfo = XDW_PAGE_COLOR_INFO()
    TRY(DLL.XDW_GetPageColorInformation, documentHandle, page, byref(pageColorInfo), NULL)
    return pageColorInfo

@APPEND(NULL)
def XDW_OptimizeDocument(inputPath, outputPath):
    pass

@RAISE
def XDW_ProtectDocument(inputPath, outputPath, protectType, moduleOption, protectOption):
    return DLL.XDW_ProtectDocument(inputPath, outputPath, protectType, byref(moduleOption), byref(protectOption))

@RAISE
def XDW_CreateXdwFromImageFileAndInsertDocument(documentHandle, page, inputPath, createOption):
    return DLL.XDW_CreateXdwFromImageFileAndInsertDocument(documentHandle, page, inputPath, byref(createOption), NULL)

@APPEND(NULL)
def XDW_GetDocumentAttributeNumber(documentHandle):
    pass

def XDW_GetDocumentAttributeByName(documentHandle, attributeName):
    """XDW_GetDocumentAttributeByName(documentHandle, attributeName) --> (attributeType, attributeValue)"""
    attributeType = c_int()
    size = TRY(DLL.XDW_GetDocumentAttributeByName, documentHandle, attributeName, NULL, NULL, 0, NULL)
    attributeValue = create_string_buffer(size)
    TRY(DLL.XDW_GetDocumentAttributeByName, documentHandle, attributeName, byref(attributeType), byref(attributeValue), size, NULL)
    return (attributeType.value, attributeValue.value)

def XDW_GetDocumentAttributeByOrder(documentHandle, order):
    """XDW_GetDocumentAttributeByOrder(documentHandle, order) --> (attributeName, attributeType, attributeValue)"""
    attributeName = create_string_buffer(256)  # size MUST >= 256
    attributeType = c_int()
    size = TRY(DLL.XDW_GetDocumentAttributeByOrder, documentHandle, order, NULL, NULL, NULL, 0, NULL)
    attributeValue = create_string_buffer(size)
    TRY(DLL.XDW_GetDocumentAttributeByOrder, documentHandle, order, byref(attributeName), byref(attributeType), byref(attributeValue), size, NULL)
    return (attributeName.value, attributeType.value, attributeValue.value)

@APPEND(NULL)
def XDW_SetDocumentAttribute(documentHandle, attributeName, attributeType, attributeValue):
    pass

@APPEND(NULL)
def XDW_SucceedAttribute(documentHandle, filePath, document, succession):
    pass

@STRING
def XDW_GetPageFormAttribute(documentHandle, pageForm, attributeName):
    pass

@APPEND(0, NULL)
def XDW_SetPageFormAttribute(documentHandle, pageForm, attributeName, attributeType, attributeValue):
    pass

@APPEND(NULL)
def XDW_UpdatePageForm(documentHandle, otherPageForm):
    pass

@APPEND(NULL)
def XDW_RemovePageForm(documentHandle, otherPageForm):
    pass

def XDW_GetLinkRootFolderInformation(order):
    """XDW_GetLinkRootFolderInformation(order) --> linkrootfolderInfo"""
    linkrootfolderInfo = XDW_LINKROOTFOLDER_INFO()
    TRY(DLL.XDW_GetLinkRootFolderInformation, order, byref(linkrootfolderInfo), NULL)
    return linkrootfolderInfo

@APPEND()
def XDW_GetLinkRootFolderNumber():
    pass

# Undocumented API in DocuWorksTM Development Tool Kit 7.1
# int XDWAPI XDW_GetPageTextInformation(XDW_DOCUMENT_HANDLE handle, int nPage, void* pInfo, void* reserved);
def XDW_GetPageTextInformation(documentHandle, page):
    """XDW_GetPageTextInformation(documentHandle, page) --> gptiInfo"""
    gptiInfo = XDW_GPTI_INFO()  # right?
    TRY(DLL.XDW_GetPageTextInformation, documentHandle, page, byref(gptiInfo), NULL)
    return gptiInfo

@APPEND(NULL)
def XDW_GetDocumentSignatureNumber(documentHandle):
    pass

def XDW_AddAnnotationOnParentAnnotation(documentHandle, annotationHandle, annotationType, horPos, verPos, aaInitialData):
    """XDW_AddAnnotationOnParentAnnotation(documentHandle, annotationHandle, annotationType, horPos, verPos, aaInitialData) --> new_annotationHandle"""
    new_annotationHandle = XDW_ANNOTATION_HANDLE()
    TRY(DLL.XDW_AddAnnotationOnParentAnnotation, documentHandle, annotationHandle, annotationType, horPos, verPos, ptr(aaInitialData), byref(new_annotationHandle), NULL)
    return new_annotationHandle

@RAISE
def XDW_SignDocument(inputPath, outputPath, option, moduleOption, moduleStatus):
    return DLL.XDW_SignDocument(inputPath, outputPath, byref(option), byref(moduleOption), NULL, byref(moduleStatus))

def XDW_GetSignatureInformation(documentHandle, signature, moduleInfo, moduleStatus):
    """XDW_GetSignatureInformation(documentHandle, signature, moduleInfo, moduleStatus) --> signatureInfoV5"""
    signatureInfoV5 = XDW_SIGNATURE_INFO_V5()
    TRY(DLL.XDW_GetSignatureInformation, documentHandle, signature, byref(signatureInfoV5), ptr(moduleInfo), NULL, ptr(moduleStatus))
    return signatureInfoV5

@RAISE
def XDW_UpdateSignatureStatus(documentHandle, signature, moduleOption, moduleStatus):
    return XDW_UpdateSignatureStatus(documentHandle, signature, ptr(moduleOption), NULL, ptr(moduleStatus))

@RAISE
def XDW_GetOcrImage(documentHandle, page, outputPath, imageOption):
    return DLL.XDW_GetOcrImage(documentHandle, page, outputPath, byref(imageOption), NULL)

def XDW_SetOcrData(documentHandle, page):
    """XDW_SetOcrData(documentHandle, page) --> ocrTextInfo"""
    ocrTextInfo = XDW_OCR_TEXTINFO()
    TRY(DLL.XDW_SetOcrData, documentHandle, page, byref(ocrTextInfo), NULL)
    return ocrTextInfo

@APPEND(NULL)
def XDW_GetDocumentAttributeNumberInBinder(documentHandle, position):
    pass

def XDW_GetDocumentAttributeByNameInBinder(documentHandle, position, attributeName):
    attributeType = c_int()
    size = TRY(DLL.XDW_GetDocumentAttributeByNameInBinder, documentHandle, position, attributeName, NULL, NULL, 0, NULL)
    attributeValue = create_string_buffer(size)
    TRY(DLL.XDW_GetDocumentAttributeByNameInBinder, documentHandle, attributeName, byref(attributeType), byref(attributeValue), size, NULL)
    return (attributeType.value, attributeValue.value)

def XDW_GetDocumentAttributeByOrderInBinder(documentHandle, position, order):
    """XDW_GetDocumentAttributeByOrderInBinder(documentHandle, position, order) --> (attributeName, attributeType, attributeValue)"""
    attributeName = create_string_buffer(256)  # size MUST >= 256
    attributeType = c_int()
    size = TRY(DLL.XDW_GetDocumentAttributeByOrderInBinder, documentHandle, position, order, NULL, NULL, NULL, 0, NULL)
    attributeValue = create_string_buffer(size)
    TRY(DLL.XDW_GetDocumentAttributeByOrderInBinder, documentHandle, position, order, byref(attributeName), byref(attributeType), byref(attributeValue), size, NULL)
    return (attributeName.value, attributeType.value, attributeValue.value)

"""
int XDWAPI XDW_GetTMInfo(documentHandle, void* pTMInfo, int nTMInfoSize, void* reserved);
int XDWAPI XDW_SetTMInfo(documentHandle, const void* pTMInfo, int nTMInfoSize, void* reserved);
"""

@APPEND(NULL)
def XDW_CreateXdwFromImagePdfFile(inputPath, outputPath):
    pass

def XDW_FindTextInPage(documentHandle, page, text, findTextOption):
    """XDW_FindTextInPage(documentHandle, page, text, findTextOption) --> foundHandle"""
    foundHandle = XDW_FOUND_HANDLE()
    TRY(DLL.XDW_FindTextInPage, documentHandle, page, text, ptr(findTextOption), byref(foundHandle), NULL)
    return foundHandle

def XDW_FindNext(foundHandle):
    """XDW_FindNext(foundHandle) --> foundHandle"""
    TRY(DLL.XDW_FindNext, byref(foundHandle), NULL)
    return foundHandle

@RAISE
def XDW_GetNumberOfRectsInFoundObject(foundHandle):
    return DLL.XDW_GetNumberOfRectsInFoundObject(foundHandle, NULL)

def XDW_GetRectInFoundObject(foundHandle, rect):
    """XDW_GetRectInFoundObject(foundHandle, rect) --> (xdwRect, status)"""
    xdwRect = XDW_RECT()
    status = c_int()
    TRY(DLL.XDW_GetRectInFoundObject, foundHandle, rect, byref(xdwRect), byref(status), NULL)
    return (xdwRect, status.value)

@RAISE
def XDW_CloseFoundHandle(foundHandle):
    return DLL.XDW_CloseFoundHandle(foundHandle)

@STRING
def XDW_GetAnnotationUserAttribute(annotationHandle, attributeName):
    pass

@RAISE
def XDW_SetAnnotationUserAttribute(documentHandle, annotationHandle, attributeName, attributeValue):
    dataSize = len(attributeValue) if attributeValue else 0
    return DLL.XDW_SetAnnotationUserAttribute(documentHandle, annotationHandle, attributeName, attributeValue, dataSize, NULL)

@APPEND(NULL)
def XDW_StarchAnnotation(documentHandle, annotationHandle, starch):
    pass

@RAISE
def XDW_ReleaseProtectionOfDocument(inputPath, outputPath, releaseProtectionOption):
    return DLL.XDW_ReleaseProtectionOfDocument(inputPath, outputPath, byref(releaseProtectionOption))

def XDW_GetProtectionInformation(inputPath):
    """XDW_GetProtectionInformation(inputPath) --> protectionInfo"""
    protectionInfo = XDW_PROTECTION_INFO()
    TRY(DLL.XDW_GetProtectionInformation, inputPath, byref(protectionInfo), NULL)
    return protectionInfo

def XDW_GetAnnotationCustomAttributeByName(annotationHandle, uAttributeName):
    """XDW_GetAnnotationCustomAttributeByName(annotationHandle, uAttributeName) --> (attributeType, attributeValue)"""
    attributeType = c_int()
    size = TRY(DLL.XDW_GetAnnotationCustomAttributeByName, annotationHandle, uAttributeName, NULL, NULL, 0, NULL)
    attributeValue = create_string_buffer(size)
    TRY(DLL.XDW_GetAnnotationCustomAttributeByName, annotationHandle, uAttributeName, byref(attributeType), byref(attributeValue), size, NULL)
    return (attributeType.value, attributeValue.value)

def XDW_GetAnnotationCustomAttributeByOrder(annotationHandle, order):
    """XDW_GetAnnotationCustomAttributeByOrder(annotationHandle, order) --> (uAttributeName, attributeType, attributeValue)"""
    uAttributeName = create_unicode_buffer(256)  # size MUST >= 512 bytes
    attributeType = c_int()
    size = TRY(DLL.XDW_GetAnnotationCustomAttributeByOrder, annotationHandle, order, NULL, NULL, NULL, 0, NULL)
    attributeValue = create_string_buffer(size)
    TRY(DLL.XDW_GetAnnotationCustomAttributeByOrder, annotationHandle, order, byref(uAttributeName), byref(attributeType), byref(attributeValue), size, NULL)
    return (uAttributeName.value, attributeType.value, attributeValue.value)

@APPEND(NULL)
def XDW_GetAnnotationCustomAttributeNumber(annotationHandle):
    pass

@APPEND(NULL)
def XDW_SetAnnotationCustomAttribute(documentHandle, annotationHandle, uAttributeName, attributeType, attributeValue):
    pass

@UNICODE
def XDW_GetPageTextToMemoryW(documentHandle, page):
    pass

@APPEND(NULL)
def XDW_GetFullTextW(documentHandle, uOutputPath):
    pass

def XDW_GetAnnotationAttributeW(annotationHandle, attributeName, codepage):
    """XDW_GetAnnotationAttributeW(annotationHandle, attributeName, codepage) --> (uAttributeValue, textType)"""
    textType = c_int()
    size = TRY(DLL.XDW_GetAnnotationAttributeW, annotationHandle, attributeName, NULL, 0, NULL, codepage, NULL)
    uAttributeValue = create_unicode_buffer(size)
    TRY(DLL.XDW_GetAnnotationAttributeW, annotationHandle, attributeName, byref(uAttributeValue), size, byref(textType), codepage, NULL)
    return (uAttributeValue.value, textType.value)

@APPEND(0, NULL)
def XDW_SetAnnotationAttributeW(documentHandle, annotationHandle, attributeName, attributeType, uAttributeValue, textType, codepage):
    pass

def XDW_GetDocumentAttributeByNameW(documentHandle, uAttributeName, codepage):
    """XDW_GetDocumentAttributeByNameW(documentHandle, uAttributeName, codepage) --> (attributeType, uAttributeValue, textType)"""
    textType = c_int()
    attributeType = c_int()
    size = TRY(DLL.XDW_GetDocumentAttributeByNameW, documentHandle, uAttributeName, NULL, NULL, 0, NULL, codepage, NULL)
    uAttributeValue = create_unicode_buffer(size)
    TRY(DLL.XDW_GetDocumentAttributeByNameW, documentHandle, uAttributeName, byref(attributeType), byref(uAttributeValue), size, byref(textType), codepage, NULL)
    return (attributeType.value, uAttributeValue.value, textType.value)

def XDW_GetDocumentAttributeByOrderW(documentHandle, order, codepage):
    """XDW_GetDocumentAttributeByOrderW(documentHandle, order, codepage) --> (uAttributeName, attributeType, uAttributeValue, textType)"""
    textType = c_int()
    attributeType = c_int()
    uAttributeName = create_unicode_buffer(256)  # size MUST >= 256
    size = TRY(DLL.XDW_GetDocumentAttributeByOrderW, documentHandle, order, NULL, NULL, NULL, 0, NULL, codepage, NULL)
    uAttributeValue = create_unicode_buffer(size)
    TRY(DLL.XDW_GetDocumentAttributeByOrderW, documentHandle, order, byref(uAttributeName), byref(attributeType), byref(uAttributeValue), size, byref(textType), codepage, NULL)
    return (uAttributeName.value, attributeType.value, uAttributeValue.value, textType.value)

def XDW_GetDocumentAttributeByNameInBinderW(documentHandle, position, uAttributeName, codepage):
    """XDW_GetDocumentAttributeByNameInBinderW(documentHandle, position, uAttributeName, codepage) --> (attributeType, uAttributeValue, textType)"""
    textType = c_int()
    attributeType = c_int()
    size = TRY(DLL.XDW_GetDocumentAttributeByNameInBinderW, documentHandle, position, NULL, NULL, NULL, 0, NULL, codepage, NULL)
    uAttributeValue = create_unicode_buffer(size)
    TRY(DLL.XDW_GetDocumentAttributeByNameInBinderW, documentHandle, position, byref(uAttributeName), byref(attributeType), byref(uAttributeValue), size, byref(textType), codepage, NULL)
    return (attributeType.value, uAttributeValue.value, textType.value)

def XDW_GetDocumentAttributeByOrderInBinderW(documentHandle, position, order, codepage):
    """XDW_GetDocumentAttributeByOrderInBinderW(documentHandle, position, order, codepage) --> (uAttributeName, attributeType, uAttributeValue, textType)"""
    textType = c_int()
    attributeType = c_int()
    uAttributeName = create_unicode_buffer(256)  # size MUST >= 256
    size = TRY(DLL.XDW_GetDocumentAttributeByOrderInBinderW, documentHandle, position, order, NULL, NULL, NULL, 0, NULL, codepage, NULL)
    uAttributeValue = create_unicode_buffer(size)
    TRY(DLL.XDW_GetDocumentAttributeByOrderInBinderW, documentHandle, position, order, byref(uAttributeName), byref(attributeType), byref(uAttributeValue), size, byref(textType), codepage, NULL)
    return (uAttributeName.value, attributeType.value, uAttributeValue.value, textType.value)

@APPEND(NULL)
def XDW_SetDocumentAttributeW(documentHandle, uAttributeName, attributeType, uAttributeValue, textType, codepage):
    pass

def XDW_GetDocumentNameInBinderW(documentHandle, position, codepage):
    """XDW_GetDocumentNameInBinderW(documentHandle, position, codepage) --> (uDocName, textType)"""
    textType = c_int()
    size = TRY(DLL.XDW_GetDocumentNameInBinderW, documentHandle, position, NULL, 0, NULL, codepage, NULL)
    uDocName = create_unicode_buffer(size)
    TRY(DLL.XDW_GetDocumentNameInBinderW, documentHandle, position, byref(uDocName), size, byref(textType), codepage, NULL)
    return (uDocName.value, textType.value)

@APPEND(NULL)
def XDW_SetDocumentNameInBinderW(documentHandle, position, uDocName, textType, codepage):
    pass

def XDW_GetOriginalDataInformationW(documentHandle, originalData, codepage):
    """XDW_GetOriginalDataInformationW(documentHandle, originalData, codepage) --> (orgDataInfoW, textType)"""
    textType = c_int()
    orgDataInfoW = XDW_ORGDATA_INFOW()
    TRY(DLL.XDW_GetOriginalDataInfomationW, documentHandle, originalData, byref(orgDataInfoW), byref(textType), codepage, NULL)
    return (orgDataInfoW, textType.value)

