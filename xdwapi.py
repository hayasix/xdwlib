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

from xdwerror import *
from xdwconst import *
from xdwstruct import *


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

def XDW_GetDocumentAttributeByName(documentHandle, attributeName, default=None):
    """XDW_GetDocumentAttributeByName(documentHandle, attributeName) --> (attributeType, attributeValue)"""
    attributeType = c_int()
    size = DLL.XDW_GetDocumentAttributeByName(documentHandle, attributeName, byref(attributeType), NULL, 0, NULL)
    if 0 < size:
        attributeValue = create_string_buffer(size)
        TRY(DLL.XDW_GetDocumentAttributeByName, documentHandle, attributeName, byref(attributeType), byref(attributeValue), size, NULL)
        return (attributeType.value, attributeValue.value)
    if size == XDW_E_INVALIDARG and default:  # Specified attribute is missing / has no value.
        return (default, None, None)
    raise XDWError(size)

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

def XDW_GetDocumentAttributeByNameInBinder(documentHandle, position, attributeName, default=None):
    attributeType = c_int()
    size = DLL.XDW_GetDocumentAttributeByNameInBinder(documentHandle, position, attributeName, byref(attributeType), NULL, 0, NULL)
    if 0 < size:
        attributeValue = create_string_buffer(size)
        TRY(DLL.XDW_GetDocumentAttributeByNameInBinder, documentHandle, attributeName, byref(attributeType), byref(attributeValue), size, NULL)
        return (attributeType.value, attributeValue.value)
    if size == XDW_E_INVALIDARG and default:  # Specified attribute is missing / has no value.
        return (default, None, None)
    raise XDWError(size)

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

def XDW_GetDocumentAttributeByNameW(documentHandle, uAttributeName, codepage, default=None):
    """XDW_GetDocumentAttributeByNameW(documentHandle, uAttributeName, codepage) --> (attributeType, uAttributeValue, textType)"""
    textType = c_int()
    attributeType = c_int()
    size = DLL.XDW_GetDocumentAttributeByNameW(documentHandle, uAttributeName, byref(attributeType), NULL, 0, byref(textType), codepage, NULL)
    if 0 < size:
        uAttributeValue = create_unicode_buffer(size)
        TRY(DLL.XDW_GetDocumentAttributeByNameW, documentHandle, uAttributeName, byref(attributeType), byref(uAttributeValue), size, byref(textType), codepage, NULL)
        return (attributeType.value, uAttributeValue.value, textType.value)
    if size == XDW_E_INVALIDARG and default:  # Specified attribute is missing / has no value.
        return (default, None, None)
    raise XDWError(size)

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

