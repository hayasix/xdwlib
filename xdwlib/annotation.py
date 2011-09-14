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

from common import *
from observer import Subject, Observer
from struct import Point, Rect
from annotatable import Annotatable


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
    result = "".join(map(chr, result))
    result = unicode(result, CODEPAGE)
    return result


def encode_fake_unicode(ustring):
    s = ustring.encode(CODEPAGE)
    ss = zip(s[::2], s[1::2])
    result = [unichr(ord(x) | (ord(y) << 8)) for x, y in ss]
    if len(s) % 2:
        result.append(unichr(ord(s[-1])))
    return "".join(result)


class Annotation(Annotatable, Observer):

    """Annotation on DocuWorks document page"""

    @staticmethod
    def all_types():
        return XDW_ANNOTATION_TYPE

    @staticmethod
    def all_attributes():
        return [outer_attribute_name(k) for k in XDW_ANNOTATION_ATTRIBUTE]

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
        Annotatable.__init__(self)
        Observer.__init__(self, page, EV_ANN_INSERTED)
        self.page = page.page if isinstance(page, Annotation) else page
        self.parent = parent if isinstance(parent, Annotation) else None
        if not info:
            pah = self.parent.handle if self.parent else NULL
            info = XDW_GetAnnotationInformation(
                    self.page.doc.handle, self.page.absolute_page() + 1,
                    pah, pos + 1)
        self.handle = info.handle
        self.type = info.nAnnotationType
        self.annotations = info.nChildAnnotations
        self.is_unicode = False

    def __repr__(self):
        parent_pos = [self.pos]
        ann = self
        while ann.parent:
            parent_pos.append(ann.pos)
            ann = ann.parent
        return u"Annotation(%s[%d]%s)" % (self.page.doc.name, self.page.pos,
                "".join("[%d]" % pos for pos in reversed(parent_pos)))

    def __str__(self):
        return u"Annotation(%s P%d: type=%s)" % (
                self.page.doc.name, self.page.pos, XDW_ANNOTATION_TYPE[self.type])

    def __getattr__(self, name):
        attrname = inner_attribute_name(name)
        if attrname in XDW_ANNOTATION_ATTRIBUTE:
            if name in ("FontName", "font_name"):  # TODO: investigate...
                v = XDW_GetAnnotationAttribute(self.handle, attrname)
                return unicode(v, CODEPAGE)
            t, v, tt = XDW_GetAnnotationAttributeW(
                    self.handle, attrname, codepage=CP)
            if t == XDW_ATYPE_INT:
                v = Annotation.scale(attrname, v)
            elif t == XDW_ATYPE_STRING:
                self.is_unicode = (tt == XDW_TEXT_UNICODE)
            else:  # t == XDW_ATYPE_OTHER:  # Quick hack for points.
                v = [Point(p.x, p.y) for p in v]
            return v
        if name in ("position", "size"):
            pah = self.parent.handle if self.parent else NULL
            info = XDW_GetAnnotationInformation(
                    self.page.doc.handle, self.page.absolute_page() + 1, pah, self.pos + 1)
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
                if name in ("FontName", "font_name"):  # TODO: investigate...
                    value = value.encode(CODEPAGE)
                    XDW_SetAnnotationAttribute(
                            self.page.doc.handle, self.handle,
                            attrname, XDW_ATYPE_STRING, value)
                else:
                    XDW_SetAnnotationAttributeW(
                            self.page.doc.handle, self.handle,
                            attrname, XDW_ATYPE_STRING, value,
                            texttype, codepage=CP)
            elif isinstance(value, (int, float)):
                value = c_int(Annotation.scale(attrname, value, store=True))
                XDW_SetAnnotationAttributeW(
                        self.page.doc.handle, self.handle,
                        attrname, XDW_ATYPE_INT, byref(value), 0, 0)
            else:
                raise TypeError("Invalid type to set attribute value: " + \
                                str(value))
            return
        if name == "position":
            XDW_SetAnnotationPosition(self.page.doc.handle, self.handle,
                    int(value.x * 100), int(value.y * 100))
        elif name == "size":
            XDW_SetAnnotationSize(self.page.doc.handle, self.handle,
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

    def inside(self, rect):  # Assume rect is half-open.
        if isinstance(rect, tuple):
            rect = Rect(rect.left, rect.top, rect.right, rect.bottom)
        return rect.left <= self.position.x <= rect.right - self.size.x and \
               rect.top <= self.position.y <= rect.bottom - self.size.y

    def _add_annotation(self, ann_type, position, init_dat):
        return XDW_AddAnnotationOnParentAnnotation(
                self.page.doc.handle, self.handle, ann_type,
                int(position.x * 100), int(position.y * 100), init_dat)

    def _delete_annotation(self, ann):
        XDW_RemoveAnnotation(self.page.doc.handle, ann.handle)

    def content_text(self):
        if self.type == XDW_AID_TEXT:
            return getattr(self, XDW_ATN_Text)
        elif self.type == XDW_AID_LINK:
            return getattr(self, XDW_ATN_Caption)
        elif self.type == XDW_AID_STAMP:
            return "%s <DATE> %s" % (
                    getattr(self, XDW_ATN_TopField),
                    getattr(self, XDW_ATN_BottomField))
        return None
