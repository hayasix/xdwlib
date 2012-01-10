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
from struct import *
from annotatable import Annotatable


__all__ = ("Annotation",)


def absolute_points(points):
    """Convert xdwapi-style point sequence in absolute coordinates."""
    if len(points) < 2:
        return points
    p0 = points[0]
    return tuple([p0] + [p0 + p for p in points[1:]])


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

    def __init__(self, pg, pos, parent=None):
        self.pos = pos
        Annotatable.__init__(self)
        Observer.__init__(self, pg, EV_ANN_INSERTED)
        self.page = pg.page if isinstance(pg, Annotation) else pg
        self.parent = parent if isinstance(parent, Annotation) else None
        info = XDW_GetAnnotationInformation(
                self.page.doc.handle,
                self.page.absolute_page() + 1,
                self.parent.handle if self.parent else NULL,
                pos + 1)
        self.handle = info.handle
        self.type = XDW_ANNOTATION_TYPE[info.nAnnotationType]
        self.annotations = info.nChildAnnotations
        self.is_unicode = False

    def __repr__(self):
        parents = []
        ann = self
        while ann is not None:
            parents.insert(0, ann.pos)
            ann = ann.parent
        return u"Annotation(%s[%d][%s])" % (
                self.page.doc.name,
                self.page.pos,
                "][".join(map(str, parents)))

    def __str__(self):
        return u"%s:%s)" % (repr(self)[:-1], self.type)

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
                    return ",".join(XDW_FONT_STYLE[b]
                            for b in (1, 2, 4, 8) if b & v)
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
                return scale(attrname, v, store=False)
            elif t == XDW_ATYPE_STRING:
                self.is_unicode = (tt == XDW_TEXT_UNICODE)
                return v
            else:  # t == XDW_ATYPE_OTHER:  # Quick hack for points.
                points = [Point(
                        scale(attrname, p.x),
                        scale(attrname, p.y)) for p in v]
                return absolute_points(points)
        elif name == "margin":  # Abbreviation support like CSS.
            result = []
            for d in ("Top", "Right", "Bottom", "Left"):
                _, v, _ = XDW_GetAnnotationAttributeW(
                        self.handle, "%{0}Margin".format(d))
                result.append(v / 100.0)
            return tuple(result)
        elif name in ("position", "size"):
            info = XDW_GetAnnotationInformation(
                    self.page.doc.handle,
                    self.page.absolute_page() + 1,
                    self.parent.handle if self.parent else NULL,
                    self.pos + 1)
            if name == "position":
                v = Point(info.nHorPos, info.nVerPos)
            else:
                v = Point(info.nWidth, info.nHeight)
            self.__dict__[name] = v / 100.0  # mm;  update this property
        return self.__dict__[name]

    def __setattr__(self, name, value):
        attrname = inner_attribute_name(name)
        if attrname == XDW_ATN_Points:
            raise AttributeError(
                    "Points of polygon or marker cannot be updated.")
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
                if self.is_unicode:
                    texttype = XDW_TEXT_UNICODE
                else:
                    texttype = XDW_TEXT_MULTIBYTE
                if isinstance(value, str):
                    value = unicode(value, CODEPAGE)
                if name in ("FontName", "font_name"):  # TODO: investigate...
                    value = value.encode(CODEPAGE)
                    XDW_SetAnnotationAttribute(
                            self.page.doc.handle,
                            self.handle,
                            attrname,
                            XDW_ATYPE_STRING,
                            value)
                else:
                    XDW_SetAnnotationAttributeW(
                            self.page.doc.handle,
                            self.handle,
                            attrname,
                            XDW_ATYPE_STRING,
                            value,
                            texttype,
                            codepage=CP)
            elif isinstance(value, (int, float)):
                value = int(scale(attrname, value, store=True))
                value = c_int(value)
                XDW_SetAnnotationAttributeW(
                        self.page.doc.handle,
                        self.handle,
                        attrname,
                        XDW_ATYPE_INT,
                        byref(value),
                        0,
                        0)
            else:
                raise TypeError(
                        "Invalid type to set attribute value: " + str(value))
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
            XDW_SetAnnotationPosition(
                    self.page.doc.handle,
                    self.handle,
                    int(value.x * 100),
                    int(value.y * 100))
        elif name == "size":
            XDW_SetAnnotationSize(
                    self.page.doc.handle,
                    self.handle,
                    int(value.x * 100),
                    int(value.y * 100))
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
        """Returns dict of annotation attribute names and values."""
        tv = XDW_ANNOTATION_TYPE.normalize(self.type)
        return dict(
                (outer_attribute_name(k), getattr(self, k))
                for (k, v) in XDW_ANNOTATION_ATTRIBUTE.iteritems()
                if tv in v[2])

    def inside(self, rect):  # Assume rect is half-open.
        """Returns if annotation is placed inside rect."""
        if isinstance(rect, (list, tuple)):
            rect = Rect(*rect[:4])
        if hasattr(self, "points"):
            xs = [p.x for p in self.points]
            ys = [p.y for p in self.points]
            l, t = min(xs), min(ys)
            r, b = max(xs), max(ys)
        elif hasattr(self, "size"):
            l, t = self.position
            r, b = self.position + self.size
        rect = Rect(*(x * 100 for x  in rect))
        l, t, r, b = l * 100, t * 100, r * 100, b * 100
        return (rect.left <= l and r < rect.right and
                rect.top <= t and b < rect.bottom)

    def _add(self, ann_type, position, init_dat):
        """Concrete method over _add() for add()."""
        ann_type = XDW_ANNOTATION_TYPE.normalize(ann_type)
        return XDW_AddAnnotationOnParentAnnotation(
                self.page.doc.handle,
                self.handle,
                ann_type,
                int(position.x * 100),
                int(position.y * 100),
                init_dat)

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
        """Peg annotation on current position."""
        action = XDW_STARCH_ACTION.normalize(action)
        XDW_StarchAnnotation(self.page.doc.handle, self.handle, action)

    def rotate(self, degree, origin=None):
        """Rotate annotation.

        EXPERIMENTAL and WORK IN PROGROSS
        """
        if origin is None:
            origin = self.position
        t = XDW_ANNOTATION_TYPE.normalize(self.type)
        if t in (XDW_AID_BITMAP, XDW_AID_STAMP):
            self.position = self.position.rotate(degree, origin=origin)
            # Copy attributes.
            for k, v in kw.items():
                if k in ("position", "size", "points"):
                    continue
                setattr(copy, k, v)
            self = parent.annotation(pos)
        elif t == XDW_AID_TEXT:
            self.position = self.position.rotate(degree, origin=origin)
            degree += self.text_orientation
            self.text_orientation = int(degree) % 360
            # Copy attributes.
            for k, v in kw.items():
                if k in ("position", "size", "points", "text_orientation"):
                    continue
                setattr(copy, k, v)
            self = parent.annotation(pos)
        elif t in (XDW_AID_STRAIGHTLINE, XDW_AID_RECTANGLE, XDW_AID_ARC):
            """EXPERIMENTAL and WORK IN PROGROSS"""
            self.position = self.position.rotate(degree, origin=origin)
            self.size = self.size.rotate(degree)
            # Copy attributes.
            for k, v in kw.items():
                if k in ("position", "size", "points"):
                    continue
                setattr(copy, k, v)
            self = parent.annotation(pos)
        elif t == XDW_AID_POLYGON:
            """EXPERIMENTAL and WORK IN PROGROSS"""
            points = [p.rotate(degree, origin=origin) for p in self.points]
            parent = self.parent or self.page
            pos = self.pos
            copy = parent.add_polygon(position=self.position, points=points)
            kw = self.attributes()
            # Copy attributes.
            for k, v in kw.items():
                if k in ("position", "size", "points"):
                    continue
                setattr(copy, k, v)
            parent.delete(pos)
            self = copy
        elif t == XDW_AID_MARKER:
            """EXPERIMENTAL and WORK IN PROGROSS"""
            points = [p.rotate(degree, origin=origin) for p in self.points]
            parent = self.parent or self.page
            pos = self.pos
            copy = parent.add_marker(position=self.position, points=points)
            self = parent.annotation(pos)
            # Copy attributes.
            for k, v in kw.items():
                if k in ("position", "size", "points"):
                    continue
                setattr(copy, k, v)
            parent.delete(pos)
            self = copy
