#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""annotation.py -- Annotation

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

    @staticmethod
    def all_types():
        """Returns all annotation types for convenience."""
        return XDW_ANNOTATION_TYPE

    @staticmethod
    def all_attributes():
        """Returns all annotation attributes for convenience."""
        return [outer_attribute_name(k) for k in XDW_ANNOTATION_ATTRIBUTE]

    @staticmethod
    def all_colors(stickey=False):
        """Returns all colors available."""
        return tuple(sorted(
                (XDW_COLOR_FUSEN if stickey else XDW_COLOR).values()))

    def __init__(self, pg, pos, parent=None):
        self.pos = pos
        Annotatable.__init__(self)
        Observer.__init__(self, pg, EV_ANN_INSERTED)
        self.page = pg.page if isinstance(pg, Annotation) else pg
        self.parent = parent if isinstance(parent, Annotation) else None
        self.reset_attr()

    def reset_attr(self):
        info = XDW_GetAnnotationInformation(
                self.page.doc.handle,
                self.page.absolute_page() + 1,
                self.parent.handle if self.parent else NULL,
                self.pos + 1)
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
        return u"Annotation({docname}[{pagepos}][{poslist}])".format(
                docname=self.page.doc.name,
                pagepos=self.page.pos,
                poslist="][".join(map(str, parents)))

    def __str__(self):
        return u"{0}:{1})".format(repr(self)[:-1], self.type)

    @staticmethod
    def _unicode_enabled(ann_type):
        return attrname in (
                XDW_ATN_Text,
                XDW_ATN_Caption, XDW_ATN_Url, XDW_ATN_XdwPath,
                XDW_ATN_XdwNameInXbd, XDW_ATN_Tooltip_String,
                XDW_ATN_LinkAtn_Title, XDW_ATN_OtherFilePath,
                XDW_ATN_MailAddress,
                XDW_ATN_TopField, XDW_ATN_BottomField,
                )

    def __getattr__(self, name):
        attrname = inner_attribute_name(name)
        if attrname in XDW_ANNOTATION_ATTRIBUTE:
            data_type, value, text_type = XDW_GetAnnotationAttributeW(
                    self.handle, attrname, codepage=CP)
            if data_type == XDW_ATYPE_INT:
                if self.type == "STICKEY" and attrname.endswith("Color"):
                    return XDW_COLOR_FUSEN[value]
                return scale(attrname, value, store=False)
            elif data_type == XDW_ATYPE_STRING:
                self.is_unicode = (text_type == XDW_TEXT_UNICODE)
                return value
            else:  # data_type == XDW_ATYPE_OTHER:  # Quick hack for points.
                points = [Point(
                        scale(attrname, p.x),
                        scale(attrname, p.y)) for p in value]
                return absolute_points(points)
        elif name == "margin":  # Abbreviation support like CSS.
            result = []
            for d in ("Top", "Right", "Bottom", "Left"):
                _, value, _ = XDW_GetAnnotationAttributeW(
                        self.handle, "%{0}Margin".format(d))
                result.append(value / 100.0)
            return tuple(result)
        elif name in ("position", "size"):
            info = XDW_GetAnnotationInformation(
                    self.page.doc.handle,
                    self.page.absolute_page() + 1,
                    self.parent.handle if self.parent else NULL,
                    self.pos + 1)
            if name == "position":
                value = Point(info.nHorPos, info.nVerPos)
            else:
                value = Point(info.nWidth, info.nHeight)
            self.__dict__[name] = value / 100.0  # mm;  update this property
        return self.__dict__[name]

    def __setattr__(self, name, value):
        attrname = inner_attribute_name(name)
        if attrname == XDW_ATN_Points:
            raise AttributeError(
                    "Points of polygon or marker cannot be updated.")
        if attrname in XDW_ANNOTATION_ATTRIBUTE:
            if self.type == "STICKEY" and attrname.endswith("Color"):
                value = XDW_COLOR_FUSEN.normalize(value)
            t, unit, limited = XDW_ANNOTATION_ATTRIBUTE[attrname]
            anntype = XDW_ANNOTATION_TYPE.inner(self.type)
            if limited and anntype not in limited:
                raise AttributeError(
                        "illegal attribute {0}.{1}".format(self.type, name))
            if t == 0 or isinstance(unit, XDWConst):
                if not isinstance(unit, XDWConst):
                    if not isinstance(value, (int, float)):
                        raise ValueError(
                                "numeric data required, text given")
                value = c_int(int(scale(attrname, value, store=True)))
                XDW_SetAnnotationAttributeW(
                        self.page.doc.handle,
                        self.handle,
                        attrname,
                        XDW_ATYPE_INT,
                        byref(value),
                        0,
                        0)
            elif t == 1:
                if not isinstance(value, basestring):
                    raise ValueError(
                            "text data required, numeric given")
                if self.is_unicode and unicode_enabled:
                    texttype = XDW_TEXT_UNICODE
                else:
                    texttype = XDW_TEXT_MULTIBYTE
                if isinstance(value, str):
                    value = unicode(value, CODEPAGE)
                XDW_SetAnnotationAttributeW(
                        self.page.doc.handle,
                        self.handle,
                        attrname,
                        XDW_ATYPE_STRING,
                        value,
                        texttype,
                        codepage=CP)
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
            self.__dict__[name] = value
        elif name == "size":
            if self.type not in (
                    "STICKEY", "RECTANGLE", "ARC", "TEXT", "LINK", "STAMP"):
                raise TypeError(
                        "can't resize {0} annotation".format(self.type))
            XDW_SetAnnotationSize(
                    self.page.doc.handle,
                    self.handle,
                    int(value.x * 100),
                    int(value.y * 100))
            self.__dict__[name] = value
        else:
            self.__dict__[name] = value

    def get_userattr(self, name):
        """Get annotationwise user defined attribute."""
        if isinstance(name, unicode):
            name = name.encode(CODEPAGE)
        return XDW_GetAnnotationUserAttribute(self.handle, name)

    def set_userattr(self, name, value):
        """Set annotationwise user defined attribute."""
        if isinstance(name, unicode):
            name = name.encode(CODEPAGE)
        XDW_SetAnnotationUserAttribute(
                self.page.doc.handle, self.handle, name, value)

    def get_property(self, name):
        """Get annotationwise custom (i.e. with-type) user defined property."""
        if isinstance(name, str):
            name = name.decode(CODEPAGE)
        if isinstance(name, unicode):
            t, v = XDW_GetAnnotationCustomAttributeByName(self.handle, name)
            return makevalue(t, v)
        if not isinstance(name, int):
            raise TypeError("name must be unicode or int")
        # Any custom attribute can be taken by order which starts with 0.
        attrs = self.customattrs()
        if name < 0:
            name += attrs
        if not (0 <= name < attrs):
            raise IndexError("attribute order out of range [0, %d)" % attrs)
        name, t, value = \
                XDW_GetAnnotationCustomAttributeByOrder(self.handle, name + 1)
        return (name, makevalue(t, value))

    def properties(self):
        """Get number of annotationwise custom user defined property."""
        return XDW_GetAnnotationCustomAttributeNumber(self.handle)

    def set_property(self, name, value):
        """Set annotationwise custom user defined property."""
        if isinstance(name, str):
            name = name.decode(CODEPAGE)
        if isinstance(value, str):
            value = value.decode(CODEPAGE)
        t, value = typevalue(value)
        XDW_SetAnnotationCustomAttribute(
                self.page.doc.handle, self.handle, name, t, value)

    getprop = get_property
    setprop = set_property
    props = properties

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
            raise ValueError("Illegal event type: {0}".format(event.type))

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
            return "{0} <DATE> {1}".format(
                    getattr(self, XDW_ATN_TopField),
                    getattr(self, XDW_ATN_BottomField))
        return None

    def peg(self, action="ON"):
        """Peg annotation on current position."""
        action = XDW_STARCH_ACTION.normalize(action)
        XDW_StarchAnnotation(self.page.doc.handle, self.handle, action)

    def shift(self, *args, **kw):
        self.position = self.position.shift(*args, **kw)

    def rotate(self, degree, origin=None, orientation=False):
        """Rotate annotation.

        degree      (int) rotation angle in clockwise degree
        origin      (Point) center of rotation; None = the current position.
        orientation (bool) also change orientation of content of annotation.
                    Effective only for text, straightline, marker and polygon.

        EXPERIMENTAL and WORK IN PROGROSS.

        For straightline, marker and polygon, this method generates a new
        annotation derived from the original.  Original one is deleted.
        This process may result in the change of annotation position.  But
        users usually points to an element of page or parent annotation's
        `observers' (list) attribute, so nothing is required after such change.

        Example (suppose there are 9 annotations in the page):
        >>> for ann in pg: print ann.type
        ...
        TEXT
        TEXT
        POLYGON
        MARKER
        STAMP
        CUSTOM
        BITMAP
        STRAIGHTLINE
        MARKER
        >>> ann = pg.annotation(2)  # POLYGON
        >>> ann.pos, ann.type, ann.position, ann.points
        (2, 'POLYGON', Point(52.12, 56.16), (Point(58.12, 62.16), Point(
        65.91, 99.76), Point(80.13, 75.37), Point(96.39, 79.10), Point(9
        7.06, 60.47)))
        >>> ann.rotate(30, orientation=True)
        >>> ann.pos, ann.type, ann.position, ann.points
        (8, 'POLYGON', Point(52.12, 56.16), (Point(54.31, 64.35), Point(
        42.26, 100.80), Point(66.76, 86.79), Point(78.98, 98.15), Point(
        88.87, 82.35)))
        >>> # Notice ann.pos is replaced automatically.
        ...
        >>> for ann in pg: print ann.type
        ...
        TEXT
        TEXT
        MARKER
        STAMP
        CUSTOM
        BITMAP
        STRAIGHTLINE
        MARKER
        POLYGON
        >>>  # Deleted the original POLYGON and added a new POLYGON in the end.
        ...
        """
        t = XDW_ANNOTATION_TYPE.normalize(self.type)
        if t == XDW_AID_TEXT:
            origin = origin or self.position
            self.position = self.position.rotate(degree, origin=origin)
            if orientation:
                degree += self.text_orientation
                self.text_orientation = int(degree) % 360
        elif t in (XDW_AID_STRAIGHTLINE, XDW_AID_MARKER, XDW_AID_POLYGON):
            # For these annotations, annotation position is determined
            # automatically by DocuWorks in consideration for margins.
            # So, we don't have to care for it.
            origin = origin or self.points[0]
            if not orientation:
                gap = self.points[0] - self.position
                p0 = self.points[0].rotate(degree, origin=origin)
                self.position = p0 - gap
                return
            points = [p.rotate(degree, origin=origin) for p in self.points]
            parent = self.parent or self.page
            action = {
                    XDW_AID_STRAIGHTLINE: parent.add_line,
                    XDW_AID_MARKER: parent.add_marker,
                    XDW_AID_POLYGON: parent.add_polygon,
                    }.get(t)
            copy = action(points=points)
            # Copy attributes.
            kw = self.attributes()
            for k, v in kw.items():
                if k in ("position", "size", "points"):
                    continue
                setattr(copy, k, v)
            # Acquire child annotations.
            for child in self:
                child.parent = copy
            # Update content information.
            parent.delete(self.pos)
            self.pos = copy.pos
            self.reset_attr()
        else:
            origin = origin or self.position
            self.position = self.position.rotate(degree, origin=origin)
