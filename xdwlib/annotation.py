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

import re

from xdwapi import *
from common import *
from observer import *
from struct import Point, Rect
from annotatable import Annotatable


__all__ = ("Annotation",)


def decode_fake_unicode(ustring):
    """Unpack a 16bit-data sequence and decode it by CODEPAGE."""
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
    """Encode unicode in CODEPAGE and pack it in a 16bit-data sequence."""
    s = ustring.encode(CODEPAGE)
    ss = zip(s[::2], s[1::2])
    result = [unichr(ord(x) | (ord(y) << 8)) for x, y in ss]
    if len(s) % 2:
        result.append(unichr(ord(s[-1])))
    return "".join(result)


def flagvalue(table, flags):
    """Sum up flag values according to XDWConst table."""
    from operator import or_
    if not flags:
        return 0
    values = [table.normalize(f.strip()) for f in flags.split(",") if f]
    return reduce(or_, values) if values else 0


class Annotation(Annotatable, Observer):

    """Annotation on DocuWorks document page."""

    attrs = {
            "PageForm"          : XDW_PAGE_FORM,
            "LinkType"          : XDW_LINK_TYPE,
            "ArrowheadType"     : XDW_ARROWHEAD_TYPE,
            "ArrowheadStyle"    : XDW_ARROWHEAD_STYLE,
            "BorderType"        : XDW_BORDER_TYPE,
            "DateStyle"         : XDW_STAMP_DATE_STYLE,
            "BasisYearStyle"    : XDW_STAMP_BASISYEAR_STYLE,
            "DateOrder"         : XDW_STAMP_DATE_FORMAT,
            "FontCharSet"       : XDW_FONT_CHARSET,
            }

    @staticmethod
    def all_types():
        """Returns all annotation types for convenience."""
        return XDW_ANNOTATION_TYPE

    @staticmethod
    def all_attributes():
        """Returns all annotation attributes for convenience."""
        return [outer_attribute_name(k) for k in XDW_ANNOTATION_ATTRIBUTE]

    @staticmethod
    def all_colors(fusen=False):
        """Returns all colors available."""
        return tuple(sorted(c.lower() for c
                in (XDW_COLOR_FUSEN if fusen else XDW_COLOR).values()))

    @staticmethod
    def scale(attrname, value, store=False):
        """Scale actual size (length) to stored value and vice versa."""
        unit = XDW_ANNOTATION_ATTRIBUTE[attrname][1]
        if not unit: return value
        inv, unit = re.match(r"(1/)?([\d.]+)", unit).groups()
        return value / float(unit) if bool(inv) ^ store else value * float(unit)

    def __init__(self, page, pos, parent=None):
        self.pos = pos
        Annotatable.__init__(self)
        Observer.__init__(self, page, EV_ANN_INSERTED)
        self.page = page.page if isinstance(page, Annotation) else page
        self.parent = parent if isinstance(parent, Annotation) else None
        info = XDW_GetAnnotationInformation(
                self.page.doc.handle, self.page.absolute_page() + 1,
                self.parent.handle if self.parent else NULL, pos + 1)
        self.handle = info.handle
        self.type = XDW_ANNOTATION_TYPE[info.nAnnotationType]
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
        return u"Annotation(%s[%d]:%s)" % (
                self.page.doc.name, self.page.pos, self.type)

    def __getattr__(self, name):
        attrname = inner_attribute_name(name)
        if attrname in XDW_ANNOTATION_ATTRIBUTE:
            if attrname == "%FontName":  # TODO: investigate...
                v = XDW_GetAnnotationAttribute(self.handle, attrname)
                return unicode(v, CODEPAGE)
            t, v, tt = XDW_GetAnnotationAttributeW(
                    self.handle, attrname, codepage=CP)
            if t == XDW_ATYPE_INT:
                if attrname.endswith("Color"):
                    if self.type == "FUSEN":
                        return XDW_COLOR_FUSEN[v]
                    else:
                        return XDW_COLOR[v]
                if attrname.endswith("FontStyle"):
                    return ",".join(XDW_FONT_STYLE[b] for b in (1, 2, 4, 8) if b & v)
                elif attrname.endswith("FontPitchAndFamily"):
                    result = []
                    pitch = XDW_PITCH_AND_FAMILY.get(v & 0x0f, "UNKNOWN")
                    if pitch != "DEFAULT":
                        result.append(pitch)
                    family = XDW_PITCH_AND_FAMILY.get(v & 0xf0, "UNKNOWN")
                    if family != "DEFAULT":
                        result.append(family)
                    return ",".join(result)
                for typename, table in Annotation.attrs.items():
                    if attrname.endswith(typename):
                        return table[v]  # Convert to symbol string.
                return Annotation.scale(attrname, v)
            elif t == XDW_ATYPE_STRING:
                self.is_unicode = (tt == XDW_TEXT_UNICODE)
                return v
            else:  # t == XDW_ATYPE_OTHER:  # Quick hack for points.
                return [Point(p.x, p.y) for p in v]
        elif name == "margin":  # Abbreviation support like CSS.
            result = []
            for d in ("Top", "Right", "Bottom", "Left"):
                _, v, _ = XDW_GetAnnotationAttributeW(self.handle, "%{0}Margin".format(d))
                result.append(v / 100.0)
            return tuple(result)
        elif name in ("position", "size"):
            info = XDW_GetAnnotationInformation(
                    self.page.doc.handle, self.page.absolute_page() + 1,
                    self.parent.handle if self.parent else NULL, self.pos + 1)
            v = Point(info.nHorPos, info.nVerPos) if name == "position" \
                    else Point(info.nWidth, info.nHeight)
            self.__dict__[name] = v / 100.0  # mm;  update this property
        return self.__dict__[name]

    def __setattr__(self, name, value):
        attrname = inner_attribute_name(name)
        if attrname in XDW_ANNOTATION_ATTRIBUTE:
            if attrname.endswith("Color"):
                if self.type == "FUSEN":
                    value = XDW_COLOR_FUSEN.normalize(value)
                else:
                    value = XDW_COLOR.normalize(value)
            elif attrname.endswith("FontStyle"):
                value = flagvalue(XDW_FONT_STYLE, value)
            elif attrname.endswith("FontPitchAndFamily"):
                value = flagvalue(XDW_PITCH_AND_FAMILY, value)
            elif attrname.endswith("FontCharSet"):
                value = XDW_FONT_CHARSET.normalize(value)
            else:
                for typename, table in Annotation.attrs.items():
                    if attrname.endswith(typename):
                        value = table.normalize(value)
                        break
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
                value = c_int(int(Annotation.scale(attrname, value, store=True)))
                XDW_SetAnnotationAttributeW(
                        self.page.doc.handle, self.handle,
                        attrname, XDW_ATYPE_INT, byref(value), 0, 0)
            else:
                raise TypeError("Invalid type to set attribute value: " + \
                                str(value))
        elif name == "margin":  # Abbreviation support like CSS.
            if not isinstance(value, (list, tuple)):  # Assuming a scalar.
                value = [value] * 4
            elif len(value) == 1:
                value = value * 4
            elif len(value) == 2:
                value = [value[0], value[1]] * 2
            elif len(value) == 3:
                value = [value[0], value[1], value[2], value[1]]
            else:
                value = value[:4]
            for i, d in enumerate("Top Right Bottom Left".split()):
                setattr(self, "%{0}Margin".format(d), value[i])
        elif name == "position":
            XDW_SetAnnotationPosition(self.page.doc.handle, self.handle,
                    int(value.x * 100), int(value.y * 100))
        elif name == "size":
            XDW_SetAnnotationSize(self.page.doc.handle, self.handle,
                    int(value.x * 100), int(value.y * 100))
        else:
            self.__dict__[name] = value

    def update(self, event):
        """Update self as an observer."""
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

    def attributes(self):
        """Returns annotation attribute names for covenience."""
        return [outer_attribute_name(k) for (k, v)
                in XDW_ANNOTATION_ATTRIBUTE.items()
                if self.type in v[2]]

    def inside(self, rect):  # Assume rect is half-open.
        """Returns if annotation is placed inside rect."""
        if isinstance(rect, tuple):
            rect = Rect(rect.left, rect.top, rect.right, rect.bottom)
        return rect.left <= self.position.x <= rect.right - self.size.x and \
               rect.top <= self.position.y <= rect.bottom - self.size.y

    def _add(self, ann_type, position, init_dat):
        """Concrete method over _add() for add()."""
        ann_type = XDW_ANNOTATION_TYPE.normalize(ann_type)
        return XDW_AddAnnotationOnParentAnnotation(
                self.page.doc.handle, self.handle, ann_type,
                int(position.x * 100), int(position.y * 100), init_dat)

    def _delete(self, ann):
        """Concrete method over delete()."""
        XDW_RemoveAnnotation(self.page.doc.handle, ann.handle)

    def content_text(self):
        """Returns content text of annotation.

        Text annotation --> text
        Link annotation --> caption
        Stamp annotation --> [TopField] <DATE> [BottomField]
        """
        if self.type == "TEXT":
            return getattr(self, XDW_ATN_Text)
        elif self.type == "LINK":
            return getattr(self, XDW_ATN_Caption)
        elif self.type == "STAMP":
            return "%s <DATE> %s" % (
                    getattr(self, XDW_ATN_TopField),
                    getattr(self, XDW_ATN_BottomField))
        return None

    def peg(self, action="ON"):
        """Peg current annotation on current position."""
        action = XDW_STARCH_ACTION.normalize(action)
        XDW_StarchAnnotation(self.page.doc.handle, self.handle, action)
