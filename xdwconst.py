#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""xdwconst.py -- DocuWorks API constants

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

NULL = None

ANSI_CHARSET = 0
DEFAULT_CHARSET = 1
MAC_CHARSET = 77
OEM_CHARSET = 255
SHIFTJIS_CHARSET = 128
SYMBOL_CHARSET = 2


class XDWConst(object):

    """DocuWorks constant (internal ID) table with reverse lookup"""

    def __init__(self, constants, default=None):
        self.constants = constants
        self.reverse = dict([(v, k) for (k, v) in constants.items()])
        self.default = default

    def __contains__(self, key):
        return key in self.constants

    def __getitem__(self, key):
        return self.constants[key]  # Invalid key should raise exception.

    def inner(self, value):
        return self.reverse.get(value, self.default)

    def normalize(self, key_or_value):
        if isinstance(key_or_value, basestring):
            return self.reverse.get(str(key_or_value).upper(), self.default)
        return key_or_value


# DocuWorks constants from xdwapi.h

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

XDW_MAXPATH                         = 255
XDW_MAXINPUTIMAGEPATH               = 127

#------------------------------ common ------------------------------

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

XDW_TEXT_UNKNOWN                    = 0
XDW_TEXT_MULTIBYTE                  = 1
XDW_TEXT_UNICODE                    = 2
XDW_TEXT_UNICODE_IFNECESSARY        = 3

XDW_TEXT_TYPE = XDWConst({
        XDW_TEXT_UNKNOWN:       "UNKNOWN",
        XDW_TEXT_MULTIBYTE:     "MULTIBYTE",
        XDW_TEXT_UNICODE:       "UNICODE",
        }, default=XDW_TEXT_UNKNOWN)

#------------------------- XDWDocument -------------------------

XDW_DT_DOCUMENT                     = 0
XDW_DT_BINDER                       = 1

# XDWDocument/XDWBinder - open/create

XDW_OPEN_READONLY                   = 0
XDW_OPEN_UPDATE                     = 1

XDW_AUTH_NONE                       = 0
XDW_AUTH_NODIALOGUE                 = 1
XDW_AUTH_CONDITIONAL_DIALOGUE       = 2

XDW_PERM_DOC_EDIT                   = 0x02
XDW_PERM_ANNO_EDIT                  = 0x04
XDW_PERM_PRINT                      = 0x08
XDW_PERM_COPY                       = 0x10

XDW_CREATE_FITDEF                   = 0
XDW_CREATE_FIT                      = 1
XDW_CREATE_USERDEF                  = 2
XDW_CREATE_USERDEF_FIT              = 3
XDW_CREATE_FITDEF_DIVIDEBMP         = 4

XDW_CREATE_HCENTER                  = 0
XDW_CREATE_LEFT                     = 1
XDW_CREATE_RIGHT                    = 2

XDW_CREATE_VCENTER                  = 0
XDW_CREATE_TOP                      = 1
XDW_CREATE_BOTTOM                   = 2

XDW_CREATE_DEFAULT_SIZE             = 0
XDW_CREATE_A3_SIZE                  = 1
XDW_CREATE_2A0_SIZE                 = 2

XDW_CRTP_BEGINNING                  = 1
XDW_CRTP_PRINTING                   = 2
XDW_CRTP_PAGE_CREATING              = 3
XDW_CRTP_ORIGINAL_APPENDING         = 4
XDW_CRTP_WRITING                    = 5
XDW_CRTP_ENDING                     = 6
XDW_CRTP_CANCELING                  = 7
XDW_CRTP_FINISHED                   = 8
XDW_CRTP_CANCELED                   = 9

# XDWDocument/XDWBinder - size

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

# XDWBinder - color

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

# XDWDocument/XDWBinder - succession

XDW_SUMMARY_INFO        = 1
XDW_USER_DEF            = 2
XDW_ANNOTATION          = 4

# XDWDocument/XDWBinder - protection

XDW_PROTECT_PSWD            = 1
XDW_PROTECT_PSWD128         = 3
XDW_PROTECT_PKI             = 4
XDW_PROTECT_STAMP           = 5
XDW_PROTECT_CONTEXT_SERVICE = 6

# XDWDocument/XDWBinder - signature

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

XDW_DOCUMENT_TYPE = XDWConst({
        XDW_DT_DOCUMENT:        "DOCUMENT",
        XDW_DT_BINDER:          "BINDER",
        }, default=XDW_DT_DOCUMENT)

XDW_PROP_TITLE                  = "%Title"
XDW_PROP_SUBJECT                = "%Subject"
XDW_PROP_AUTHOR                 = "%Author"
XDW_PROP_KEYWORDS               = "%Keywords"
XDW_PROP_COMMENTS               = "%Comments"

XDW_PROPW_TITLE                 = u"%Title"
XDW_PROPW_SUBJECT               = u"%Subject"
XDW_PROPW_AUTHOR                = u"%Author"
XDW_PROPW_KEYWORDS              = u"%Keywords"
XDW_PROPW_COMMENTS              = u"%Comments"

XDW_DOCUMENT_ATTRIBUTE = XDWConst({
        XDW_PROPW_TITLE:        u"%Title",
        XDW_PROPW_SUBJECT:      u"%Subject",
        XDW_PROPW_AUTHOR:       u"%Author",
        XDW_PROPW_KEYWORDS:     u"%Keywords",
        XDW_PROPW_COMMENTS:     u"%Comments",
        }, default=None)

XDW_BINDER_SIZE = XDWConst({
        XDW_SIZE_FREE:          "FREE",
        XDW_SIZE_A3_PORTRAIT:   "A3R",
        XDW_SIZE_A3_LANDSCAPE:  "A3",
        XDW_SIZE_A4_PORTRAIT:   "A4R",
        XDW_SIZE_A4_LANDSCAPE:  "A4",
        XDW_SIZE_A5_PORTRAIT:   "A5R",
        XDW_SIZE_A5_LANDSCAPE:  "A5",
        XDW_SIZE_B4_PORTRAIT:   "B4R",
        XDW_SIZE_B4_LANDSCAPE:  "B4",
        XDW_SIZE_B5_PORTRAIT:   "B5R",
        XDW_SIZE_B5_LANDSCAPE:  "B5",
        }, default=XDW_SIZE_FREE)

XDW_BINDER_COLOR = XDWConst({
        # Here we describe colors in RRGGBB format, though DocuWorks
        # inner color representation is BBGGRR.
        XDW_BINDER_COLOR_0:     "003366",   # neutral navy (紺)
        XDW_BINDER_COLOR_1:     "006633",   # neutral green (緑)
        XDW_BINDER_COLOR_2:     "3366FF",   # neutral bule (青)
        XDW_BINDER_COLOR_3:     "FFFF66",   # neutral yellow (黄)
        XDW_BINDER_COLOR_4:     "FF6633",   # neutral orange (オレンジ)
        XDW_BINDER_COLOR_5:     "FF3366",   # neutral red (赤)
        XDW_BINDER_COLOR_6:     "FF00FF",   # fuchsia (赤紫)
        XDW_BINDER_COLOR_7:     "FFCCFF",   # neutral pink (ピンク)
        XDW_BINDER_COLOR_8:     "CC99FF",   # neutral purple (紫)
        XDW_BINDER_COLOR_9:     "663333",   # neutral brown (茶)
        XDW_BINDER_COLOR_10:    "999933",   # neutral olive (オリーブ)
        XDW_BINDER_COLOR_11:    "00FF00",   # lime (緑)
        XDW_BINDER_COLOR_12:    "00FFFF",   # aqua (水色)
        XDW_BINDER_COLOR_13:    "FFFFCC",   # neutral lightyellow (クリーム)
        XDW_BINDER_COLOR_14:    "BBBBBB",   # neutral silver (灰色)
        XDW_BINDER_COLOR_15:    "FFFFFF",   # white (白)
        }, default=XDW_BINDER_COLOR_5)

#------------------------------ XDWPage ------------------------------

XDW_GPTI_TYPE_EMF           = 0
XDW_GPTI_TYPE_OCRTEXT       = 1

XDW_IMAGE_MONO              = 0
XDW_IMAGE_COLOR             = 1
XDW_IMAGE_MONO_HIGHQUALITY  = 2

# XDWPage - rotation
XDW_ROT_0                           = 0
XDW_ROT_90                          = 90
XDW_ROT_180                         = 180
XDW_ROT_270                         = 270

# XDWPage - OCR

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

# XDWPage - page type

XDW_PGT_NULL                        = 0
XDW_PGT_FROMIMAGE                   = 1
XDW_PGT_FROMAPPL                    = 2

XDW_PAGE_TYPE = XDWConst({
        XDW_PGT_FROMIMAGE:      "IMAGE",
        XDW_PGT_FROMAPPL:       "APPLICATION",
        XDW_PGT_NULL:           "UNKNOWN",
        }, default=XDW_PGT_NULL)

#--------------------------- XDWAnnotation -------------------------

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

# Constants from xdwapian.h

XDW_IGNORE_CASE                 = 0x02
XDW_IGNORE_WIDTH                = 0x04
XDW_IGNORE_HIRAKATA             = 0x08

XDW_STARCH                      = 1
XDW_STARCH_OFF                  = 0

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

XDW_ANNOTATION_TYPE = XDWConst({
        XDW_AID_FUSEN:          "FUSEN",
        XDW_AID_TEXT:           "TEXT",
        XDW_AID_STAMP:          "STAMP",
        XDW_AID_STRAIGHTLINE:   "STRAIGHTLINE",
        XDW_AID_RECTANGLE:      "RECTANGLE",
        XDW_AID_ARC:            "ARC",
        XDW_AID_POLYGON:        "POLYGON",
        XDW_AID_MARKER:         "MARKER",
        XDW_AID_LINK:           "LINK",
        XDW_AID_PAGEFORM:       "PAGEFORM",
        XDW_AID_OLE:            "OLE",
        XDW_AID_BITMAP:         "BITMAP",
        XDW_AID_RECEIVEDSTAMP:  "RECEIVEDSTAMP",
        XDW_AID_CUSTOM:         "CUSTOM",
        XDW_AID_TITLE:          "TITLE",
        XDW_AID_GROUP:          "GROUP",
        }, default=XDW_AID_TEXT)

XDW_ANNOTATION_ATTRIBUTE = XDWConst({
        XDW_ATN_Text:                   "%Text",
        XDW_ATN_FontName:               "%FontName",
        XDW_ATN_FontStyle:              "%FontStyle",
        XDW_ATN_FontSize:               "%FontSize",
        XDW_ATN_ForeColor:              "%ForeColor",
        XDW_ATN_FontPitchAndFamily:     "%FontPitchAndFamily",
        XDW_ATN_FontCharSet:            "%FontCharSet",
        XDW_ATN_BackColor:              "%BackColor",
        XDW_ATN_Caption:                "%Caption",
        XDW_ATN_Url:                    "%Url",
        XDW_ATN_XdwPath:                "%XdwPath",
        XDW_ATN_ShowIcon:               "%ShowIcon",
        XDW_ATN_LinkType:               "%LinkType",
        XDW_ATN_XdwPage:                "%XdwPage",
        XDW_ATN_Tooltip:                "%Tooltip",
        XDW_ATN_Tooltip_String:         "%TooltipString",
        XDW_ATN_XdwPath_Relative:       "%XdwPathRelative",
        XDW_ATN_XdwLink:                "%XdwLink",
        XDW_ATN_LinkAtn_Title:          "%LinkAtnTitle",
        XDW_ATN_OtherFilePath:          "%OtherFilePath",
        XDW_ATN_OtherFilePath_Relative: "%OtherFilePathRelative",
        XDW_ATN_MailAddress:            "%MailAddress",
        XDW_ATN_BorderStyle:            "%BorderStyle",
        XDW_ATN_BorderWidth:            "%BorderWidth",
        XDW_ATN_BorderColor:            "%BorderColor",
        XDW_ATN_BorderTransparent:      "%BorderTransparent",
        XDW_ATN_BorderType:             "%BorderType",
        XDW_ATN_FillStyle:              "%FillStyle",
        XDW_ATN_FillColor:              "%FillColor",
        XDW_ATN_FillTransparent:        "%FillTransparent",
        XDW_ATN_ArrowheadType:          "%ArrowheadType",
        XDW_ATN_ArrowheadStyle:         "%ArrowheadStyle",
        XDW_ATN_WordWrap:               "%WordWrap",
        XDW_ATN_TextDirection:          "%TextDirection",
        XDW_ATN_TextOrientation:        "%TextOrientation",
        XDW_ATN_LineSpace:              "%LineSpace",
        XDW_ATN_AutoResize:             "%AutoResize",
        XDW_ATN_Invisible:              "%Invisible",
        XDW_ATN_PageFrom:               "%PageFrom",
        XDW_ATN_XdwNameInXbd:           "%XdwNameInXbd",
        XDW_ATN_TopField:               "%TopField",
        XDW_ATN_BottomField:            "%BottomField",
        XDW_ATN_DateStyle:              "%DateStyle",
        XDW_ATN_YearField:              "%YearField",
        XDW_ATN_MonthField:             "%MonthField",
        XDW_ATN_DayField:               "%DayField",
        XDW_ATN_BasisYearStyle:         "%BasisYearStyle",
        XDW_ATN_BasisYear:              "%BasisYear",
        XDW_ATN_DateField_FirstChar:    "%DateFieldFirstChar",
        XDW_ATN_Alignment:              "%Alignment",
        XDW_ATN_LeftRightMargin:        "%LeftRightMargin",
        XDW_ATN_TopBottomMargin:        "%TopBottomMargin",
        XDW_ATN_VerPosition:            "%VerPosition",
        XDW_ATN_StartingNumber:         "%StartingNumber",
        XDW_ATN_Digit:                  "%Digit",
        XDW_ATN_PageRange:              "%PageRange",
        XDW_ATN_BeginningPage:          "%BeginningPage",
        XDW_ATN_EndingPage:             "%EndingPage",
        XDW_ATN_Zoom:                   "%Zoom",
        XDW_ATN_ImageFile:              "%ImageFile",
        XDW_ATN_Points:                 "%Points",
        XDW_ATN_DateFormat:             "%DateFormat",
        XDW_ATN_DateOrder:              "%DateOrder",
        XDW_ATN_TextSpacing:            "%Spacing",
        XDW_ATN_TextTopMargin:          "%TopMargin",
        XDW_ATN_TextLeftMargin:         "%LeftMargin",
        XDW_ATN_TextBottomMargin:       "%BottomMargin",
        XDW_ATN_TextRightMargin:        "%RightMargin",
        XDW_ATN_TextAutoResizeHeight:   "%AutoResizeHeight",
        XDW_ATN_GUID:                   "%CustomAnnGuid",
        XDW_ATN_CustomData:             "%CustomAnnCustomData",
        }, default=None)


