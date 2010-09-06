#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""xdwstruct.py -- DocuWorks API structures

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

from ctypes import *


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
