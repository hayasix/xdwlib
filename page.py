#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""xdwlib.py -- DocuWorks library for Python.

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import sys
from os.path import splitext, basename
import datetime

from xdwapi import *
from annotation import XDWAnnotation, find_annotations


__all__ = ("XDWPage",)

CODEPAGE = 932


class XDWPage(object):

    """A page of DocuWorks document"""

    @staticmethod
    def normalize_resolution(n):
        if n <= 6:
            return (100, 200, 400, 200, 300, 400, 200)[n]
        return n

    def __init__(self, xdw, page):
        self.xdw = xdw
        self.page = page
        page_info = XDW_GetPageInformation(
                xdw.document_handle, page + 1, extend=True)
        self.width = page_info.nWidth  # 1/100 mm
        self.height = page_info.nHeight  # 1/100 mm
        # XDW_PGT_FROMIMAGE/FROMAPPL/NULL
        self.page_type = page_info.nPageType
        self.horizontal_resolution = XDWPage.normalize_resolution(
                page_info.nHorRes)  # dpi
        self.vertical_resolution = XDWPage.normalize_resolution(
                page_info.nVerRes)  # dpi
        self.compress_type = page_info.nCompressType
        self.annotations = page_info.nAnnotations
        self.degree = page_info.nDegree
        self.original_width = page_info.nOrgWidth  # 1/100 mm
        self.original_height = page_info.nOrgHeight  # 1/100 mm
        self.original_horizontal_resolution = XDWPage.normalize_resolution(
                page_info.nOrgHorRes)  # dpi
        self.original_vertical_resolution = XDWPage.normalize_resolution(
                page_info.nOrgVerRes)  # dpi
        self.image_width = page_info.nImageWidth  # px
        self.image_height = page_info.nImageHeight  # px

    def __getattr__(self, name):
        if name == "text":
            return XDW_GetPageTextToMemoryW(self.xdw.document_handle,
                    self.page + 1)
        if name == "annotation_text":
            return "\v".join([
                a.text for a in self.find_annotations() if a.text])
        if name == "annotation_fulltext":
            return "\v".join([
                a.fulltext for a in self.find_annotations() if a.fulltext])
        raise AttributeError("'%s' object has no attribute '%s'" % (
                self.__class__.__name__, name))

    def __str__(self):
        return "XDWPage(page %d: %.2f*%.2fmm, %s, %d annotations)" % (
                self.page,
                self.width / 100.0, self.height / 100.0,
                XDW_PAGE_TYPE[self.page_type],
                self.annotations,
                )

    def annotation(self, index):
        """annotation(n) --> XDWAnnotation"""
        if self.annotations <= index:
            if self.annotations < 1:
                raise AttributeError("page object has no annotations")
            else:
                raise IndexError(
                        "annotation index %d out of range(0..%d)" % (
                        index, self.annotations - 1))
        return XDWAnnotation(self, index)

    def find_annotations(*args, **kw):
        return find_annotations(*args, **kw)
