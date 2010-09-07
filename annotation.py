#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""annotation.py -- DocuWorks library for Python.

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

__all__ = ("find_annotations", "XDWAnnotation")

CODEPAGE = 932


def annotation_in(annotation, rect):  # Assume rect is half-open.
    return (rect.left <= annotation.horizontal_position \
                     <= rect.right - annotation.width \
            and \
            rect.top <= annotation.vertical_position \
                     <= rect.bottom - annotation.height)


def find_annotations(object,
        recursive=False, rect=None, types=None,
        half_open=True):
    if rect and not half_open:
        rect.right += 1
        rect.bottom += 1
    if types:
        if not isinstance(types, (list, tuple)):
            types = [types]
        types = [XDW_ANNOTATION_TYPE.normalize(t) for t in types]
    annotation_list = []
    for i in range(object.annotations):
        annotation = object.annotation(i)
        sublist = []
        if recursive and annotation.annotations:
            sublist = find_annotations(annotation,
                    recursive=recursive, rect=rect, types=types,
                    half_open=half_open)
        if (not rect or annotation_in(annotation, rect)) and \
                (not types or annotation.annotation_type in types):
            if sublist:
                sublist.insert(0, annotation)
                annotation_list.append(sublist)
            else:
                annotation_list.append(annotation)
        elif sublist:
            sublist.insert(0, None)
            annotation_list.append(sublist)
    return annotation_list


class XDWAnnotation(object):

    """An annotation on DocuWorks document page"""

    def __init__(self, page, index, parent_annotation=None):
        self.page = page
        self.parent_annotation = parent_annotation
        self.index = index
        if parent_annotation:
            pah = parent_annotation.annotation_handle
        else:
            pah = None
        info = XDW_GetAnnotationInformation(
                page.xdw.document_handle,
                page.page + 1,
                pah,
                index + 1)
        self.annotation_handle = info.handle
        self.horizontal_position = info.nHorPos
        self.vertical_position = info.nVerPos
        self.width = info.nWidth
        self.height = info.nHeight
        self.annotation_type = info.nAnnotationType
        self.annotations = info.nChildAnnotations

    def __str__(self):
        return "XDWAnnotation(%s P%d: type=%s)" % (
                self.page.xdw.name,
                self.page.page,
                XDW_ANNOTATION_TYPE[self.annotation_type],
                )

    def __getattr__(self, name):
        if name == "text":
            at = self.annotation_type
            ah = self.annotation_handle
            ga = XDW_GetAnnotationAttributeW
            if at == XDW_AID_STAMP:
                text = "%s <DATE> %s" % (
                        ga(ah, XDW_ATN_TopField, CODEPAGE)[0],
                        ga(ah, XDW_ATN_BottomField, CODEPAGE)[0],
                        )
            elif at == XDW_AID_TEXT:
                text = ga(ah, XDW_ATN_Text, CODEPAGE)[0]
            elif at == XDW_AID_LINK:
                text = ga(ah, XDW_ATN_Caption, CODEPAGE)[0]
            else:
                text = None
            return text
        if name == "fulltext":
            if self.annotations:
                text = [self.text]
                text.extend([self.annotation(i).fulltext \
                        for i in range(self.annotations)])
                return "\v".join([
                        t for t in text if isinstance(t, basestring)])
            else:
                return self.text
        attribute_name = "%" + name
        if attribute_name in XDW_ANNOTATION_ATTRIBUTE:
            return XDW_GetAnnotationAttributeW(
                    self.annotation_handle, unicode(attribute_name), CODEPAGE)
        raise AttributeError("'%s' object has no attribute '%s'" % (
                self.__class__.__name__, name))

    def __setattr__(self, name, value):
        attribute_name = "%" + name
        if attribute_name in XDW_ANNOTATION_ATTRIBUTE:
            if isinstance(value, basestring):
                attribute_type = XDW_ATYPE_STRING
            else:
                attribute_type = XDW_ATYPE_INT
            XDW_SetAnnotationAttributeW(
                    self.page.xdw.document_handle, self.annotation_handle,
                    unicode(attribute_name), attribute_type, byref(value),
                    XDW_TEXT_MULTIBYTE, CODEPAGE)
            return
        self.__dict__[name] = value
        #raise AttributeError("'%s' object has no attribute '%s'" % (
        #        self.__class__.__name__, name))

    def annotation(self, index):
        if self.annotations <= index:
            if self.annotations < 1:
                raise AttributeError("annotation object has no children")
            else:
                raise IndexError(
                        "annotation index %d out of range(0..%d)" % (
                        index, self.annotations - 1))
        return XDWAnnotation(self.page, index, parent_annotation=self)

    def find_annotations(*args, **kw):
        return find_annotations(*args, **kw)
