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

import datetime

from common import *


__all__ = ("Annotation",)


def split_unit(unit):
    import re
    factor = re.match(r"(1/)?[\d.]*", unit).group(0)
    unit = unit[len(factor):]
    return (factor, unit)


def decode_fake_unicode(ustring):
    result = []
    for c in ustring:
        c = ord(c)
        if c < 256:
            result.append(c)
        else:
            result.append(c & 0xff)
            result.append(c >> 8)
    result = ''.join(map(chr, result))
    result = unicode(result, "mbcs")
    return result


class Annotation(Subject, Observer):

    """Annotation on DocuWorks document page"""

    @staticmethod
    def all_types():
        return XDW_ANNOTATION_TYPE

    @staticmethod
    def all_attributes():
        return [outer_attribute_name(k) for k in XDW_ANNOTATION_ATTRIBUTE]

    @staticmethod
    def initial_data(ann_type, **kw):
        ann_type = XDW_ANNOTATION_TYPE.normalize(ann_type)
        cls = XDW_AID_INITIAL_DATA.get(ann_type, None)
        if cls:
            init_dat = cls()
            init_dat.common.nAnnotationType = ann_type
        else:
            init_dat = NULL
        for k, v in kw.items():
            if k.startswith("n"):
                v = int(v)
            elif k.startswith("sz"):
                v = str(v)
            elif k.startswith("lpsz"):
                v = byref(v)
            elif k.startswith("p"):
                v = byref(v)
            setattr(init_dat, k, v)
        return init_dat

    @staticmethod
    def scale(attrname, value, store=False):
        unit = XDW_ANNOTATION_ATTRIBUTE[attrname][1]
        if unit:
            factor = split_unit(unit)[0]
            if factor:
                factor = 1 / float(factor[2:]) if factor.startswith("1/") \
                        else float(factor)
                value = value / factor if store else value * factor
        return int(value)

    def __init__(self, page, pos, parent=None, info=None):
        self.pos = pos
        Subject.__init__(self)
        Observer.__init__(self, page, EV_ANN_INSERTED)
        self.page = page
        self.parent = parent
        if not info:
            pah = parent.handle if parent else NULL
            info = XDW_GetAnnotationInformation(
                    page.xdw.handle, page.pos + 1, pah, pos + 1)
        self.handle = info.handle
        self.type = info.nAnnotationType
        self.annotations = info.nChildAnnotations
        self.is_unicode = False

    def __str__(self):
        return "Annotation(%s P%d: type=%s)" % (
                self.page.xdw.name,
                self.page.pos,
                XDW_ANNOTATION_TYPE[self.type])

    def __getattr__(self, name):
        attrname = inner_attribute_name(name)
        if attrname in XDW_ANNOTATION_ATTRIBUTE:
            t, v, tt = XDW_GetAnnotationAttributeW(
                    self.handle, attrname, codepage=CP)
            if t == XDW_ATYPE_INT:
                v = Annotation.scale(attrname, v)
            elif t == XDW_ATYPE_STRING:
                self.is_unicode = (tt == XDW_TEXT_UNICODE)
                if name == "font_name":
                    v = decode_fake_unicode(v)  # TODO: investigate...
            else:  # t == XDW_ATYPE_OTHER:  # Quick hack for points.
                v = [Point(p.x, p.y) for p in v]
            return v
        if name in ("position", "size"):
            pah = self.parent.handle if self.parent else NULL
            info = XDW_GetAnnotationInformation(
                    self.page.xdw.handle, self.page.pos + 1, pah, self.pos + 1)
            self.__dict__[name] = Point(info.nWidth, info.nHeight) / 100.0 # mm
        return self.__dict__[name]

    def __setattr__(self, name, value):
        attrname = inner_attribute_name(name)
        if attrname in XDW_ANNOTATION_ATTRIBUTE:
            if isinstance(value, basestring):
                texttype = XDW_TEXT_UNICODE if self.is_unicode \
                            else XDW_TEXT_MULTIBYTE
                if isinstance(value, str):
                    value = unicode(value, CODEPAGE)
                XDW_SetAnnotationAttributeW(
                        self.page.xdw.handle, self.handle,
                        attrname, XDW_ATYPE_STRING, value,
                        texttype, codepage=CP)
            elif isinstance(value, (int, float)):
                value = c_int(Annotation.scale(attrname, value, store=True))
                XDW_SetAnnotationAttributeW(
                        self.page.xdw.handle, self.handle,
                        attrname, XDW_ATYPE_INT, byref(value), 0, 0)
            else:
                raise TypeError("Invalid type to set attribute value: " + \
                                str(value))
            return
        if name == "position":
            XDW_SetAnnotationPosition(self.page.xdw.handle, self.handle,
                    int(value.x * 100), int(value.y * 100))
        elif name == "size":
            XDW_SetAnnotationSize(self.page.xdw.handle, self.handle,
                    int(value.x * 100), int(value.y * 100))
        self.__dict__[name] = value

    def update(self, event):
        if not isinstance(event, Notification):
            raise TypeError("not an instance of Notification class")
        if event.type == EV_ANN_REMOVED:
            if event.para[0] < self.pos:
                self.pos -= 1
        elif event.type == EV_ANN_INSERTED:
            if event.para[0] < self.pos:
                self.pos += 1
        else:
            raise ValueError("Illegal event type: %d" % event.type)

    def typename(self):
        return XDW_ANNOTATION_TYPE[self.type]

    def attributes(self):
        return [outer_attribute_name(k) for (k, v)
                in XDW_ANNOTATION_ATTRIBUTE.items()
                if self.type in v[2]]

    def annotation(self, pos):
        """annotation(pos) --> Annotation"""
        if pos not in self.observers:
            self.observers[pos] = Annotation(self.page, pos, parent=self)
        return self.observers[pos]

    def inside(self, rect):  # Assume rect is half-open.
        if isinstance(rect, tuple):
            rect = Rect(rect.left, rect.top, rect.right, rect.bottom)
        return rect.left <= self.position.x <= rect.right - self.size.x and \
               rect.top <= self.position.y <= rect.bottom - self.size.y

    def find_annotations(self, *args, **kw):
        return find_annotations(self, *args, **kw)

    def add_annotation(self, ann_type, position, **kw):
        """Add an annotation.

        add_annotation(ann_type, position, **kw)
            position    Point; unit:mm
        """
        ann_type = XDW_ANNOTATION_TYPE.normalize(ann_type)
        if isinstance(position, (tuple, list)):
            position = Point(*position)
        init_dat = Annotation.initial_data(ann_type, **kw)
        ann_handle = XDW_AddAnnotationOnParentAnnotation(
                self.page.xdw.handle, self.handle, ann_type,
                int(position.x * 100), int(position.y * 100), init_dat)
        info = XDW_ANNOTATION_INFO()
        info.handle = ann_handle
        info.nHorPos = int(position.x * 100)
        info.nVerPos = int(position.y * 100)
        info.nWidth = 0
        info.nHeight = 0
        info.nAnnotationType = ann_type
        info.nChildAnnotations = 0
        pos = self.annotations  # TODO: Ensure this is correct.
        ann = Annotation(self, pos, parent=self, info=info)
        self.annotations += 1
        self.notify(event=Notification(EV_ANN_INSERTED, pos))
        return ann

    def delete_annotation(self, pos):
        """Delete a child annotation given by pos."""
        ann = self.annotation(pos)
        XDW_RemoveAnnotation(self.page.xdw.handle, ann.handle)
        self.detach(ann, EV_ANN_REMOVED)
        self.annotations -= 1

    def content_text(self, recursive=True):
        if self.type == XDW_AID_TEXT:
            s = getattr(self, XDW_ATN_Text)
        elif self.type == XDW_AID_LINK:
            s = getattr(self, XDW_ATN_Caption)
        elif self.type == XDW_AID_STAMP:
            s = "%s <DATE> %s" % (
                    getattr(self, XDW_ATN_TopField),
                    getattr(self, XDW_ATN_BottomField))
        else:
            s = None
        if recursive and self.annotations:
            s = [s]
            s.extend([self.annotation(i).content_text(recursive=True) \
                    for i in range(self.annotations)])
            s = joinf(ASEP, s)
        return s
