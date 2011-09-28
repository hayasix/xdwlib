#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""annotatable.py -- DocuWorks library for Python.

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import os

from common import *
from struct import Point, Rect
from observer import Subject


__all__ = ("Annotatable",)


DEFAULT_POSITION = Point(0, 0)
DEFAULT_RECT = Rect(0, 0)
DEFAULT_SIZE = Point(100, 100)
DEFAULT_WIDTH = 100
DEFAULT_POINTS = (DEFAULT_POSITION, DEFAULT_SIZE)

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


class Annotatable(Subject):

    """Annotatable objects ie. page or annotation"""

    def __len__(self):
        return self.annotations

    def __getitem__(self, pos):
        if pos < 0:
            pos += self.annotations
        return self.annotation(pos)

    def __setitem__(self, pos, val):
        raise NotImplementedError()

    def __iter__(self):
        for pos in xrange(self.annotations):
            yield self.annotation(pos)

    def annotation(self, pos):
        """annotation(pos) --> Annotation"""
        from annotation import Annotation
        if self.annotations <= pos:
            raise IndexError(
                    "Annotation number must be < %d, %d given" % (
                    self.annotations, pos))
        if pos not in self.observers:
            self.observers[pos] = Annotation(self, pos, parent=self)
        return self.observers[pos]

    def _add_annotation(self, ann_type, position, init_dat):  # abstract
        raise NotImplementedError()

    def add_annotation(self, ann_type, position, **kw):
        """Paste an annotation.

        add_annotation(ann_type, position, **kw)
            ann_type    annotation type
            position    Point; float, unit:mm
        """
        from annotation import Annotation
        ann_type = XDW_ANNOTATION_TYPE.normalize(ann_type)
        if isinstance(position, (tuple, list)):
            position = Point(*position)
        init_dat = initial_data(ann_type, **kw)
        ann_handle = self._add_annotation(ann_type, position, init_dat)
        pos = self.annotations  # TODO: Ensure this is correct.
        ann = Annotation(self.page, pos, parent=self)
        self.annotations += 1
        self.notify(event=Notification(EV_ANN_INSERTED, pos))
        return ann

    def add_text_annotation(self, text, position=DEFAULT_POSITION, **kw):
        """Paste a text annotation."""
        ann = self.add_annotation(XDW_AID_TEXT, position)
        ann.Text = text
        for k, v in kw.items():
            if k in ("ForeColor", "fore_color", "BackColor", "back_color"):
                setattr(ann, k, XDW_COLOR.normalize(v))
            elif k in ("FontPitchAndFamily", "font_pitch_and_family"):
                ann.FontPitchAndFamily = XDW_PITCH_AND_FAMILY.get(k, 0)
            elif k in ("FontName", "font_name"):
                ann.FontName = v
            elif k in ("FontCharSet", "font_char_set"):
                ann.FontCharSet = XDW_FONT_CHARSET.get("DEFAULT_CHARSET", 0)
        if hasattr(ann, "FontName") and not hasattr(ann, "FontCharSet"):
            raise ValueError("FontName must be specified with FontCharSet")
        return ann

    def add_fusen_annotation(self, position=DEFAULT_POSITION, size=DEFAULT_SIZE):
        self.add_annotation(XDW_AID_FUSEN, position,
                nWidth=size.x, nHeight=size.y)

    def add_line_annotation(self, points=(DEFAULT_POSITION, DEFAULT_SIZE)):
        self.add_annotation(XDW_AID_STRAIGHTLINE, points[0],
                nWidth=points[1].x, nHeight=point[1].y)

    add_straightline_annotation = add_line_annotation

    def add_rectangle_annotation(self, rect=DEFAULT_RECT):
        position, size = rect.position_and_size()
        self.add_annotation(XDW_AID_RECT, position,
                nWidth=size.x, nHeight=size.y)

    add_rect_annotation = add_rectangle_annotation

    def add_arc_annotation(self, rect=DEFAULT_RECT):
        position, size = rect.position_and_size()
        self.add_annotation(XDW_AID_ARC, position,
                nWidth=size.x, nHeight=size.y)

    def add_stamp_annotation(self, position=DEFAULT_POSITION, width=DEFAULT_WIDTH):
        self.add_annotation(XDW_AID_STAMP, position,
                nWidth=width)

    def add_receivedstamp_annotation(self, position=DEFAULT_POSITION, width=DEFAULT_WIDTH):
        self.add_annotation(XDW_AID_RECEIVEDSTAMP, position,
                nWidth=width)

    def add_custom_annotation(self, position=DEFAULT_POSITION,
                size=DEFAULT_SIZE, guid="???", data="???"):
        self.add_annotation(XDW_AID_CUSTOM, position,
                nWidth=size.x, nHeight=size.y, lpszGuid=byref(guid),
                nCustomDataSize=len(data), pCustomData=byref(data))

    def add_marker_annotation(self, position=DEFAULT_POSITION, points=DEFAULT_POINTS):
        self.add_annotation(XDW_AID_MARKER, position,
                nCounts=len(points), pPoints=byref(points))

    def add_polygon_annotation(self, position=DEFAULT_POSITION, points=DEFAULT_POINTS):
        self.add_annotation(XDW_AID_POLYGON, position,
                nCounts=len(points), pPoints=byref(points))

    def _delete_annotation(self, pos):  # abstract
        raise NotImplementedError()

    def delete_annotation(self, pos):
        """Remove an annotation."""
        ann = self.annotation(pos)
        self._delete_annotation(ann)
        self.detach(ann, EV_ANN_REMOVED)
        self.annotations -= 1

    def content_text(self, recursive=True):  # abstract
        raise NotImplementedError()

    def annotation_text(self, recursive=True):
        result = []
        for ann in self:
            result.append(ann.content_text())
            if ann.annotations and recursive:
                result.extend(ann.annotation_text(recursive=True))
        return joinf(ASEP, result)

    def fulltext(self):
        return  joinf(ASEP, [
                self.content_text(),
                self.annotation_text(recursive=True)])

    def find_annotations(self, handles=None, types=None, rect=None,
            half_open=True, recursive=False):
        """Find annotations on page or annotation, which meets criteria given.

        find_annotations(handles=None, types=None, rect=None, half_open=True,
                         recursive=False)
            handles     sequence of annotation handles.  None means all.
            types       sequence of types.  None means all.
            rect        XDWRect which includes annotations,
                        Note that right/bottom value are innermost of outside
                        unless half_open==False.  None means all.
            recursive   also return descendant (child) annotations.
        """
        if handles and not isinstance(handles, (tuple, list)):
            handles = list(handles)
        if types:
            if not isinstance(types, (list, tuple)):
                types = [types]
            types = [XDW_ANNOTATION_TYPE.normalize(t) for t in types]
        if rect and not half_open:
            rect.right += 1
            rect.bottom += 1
        annotation_list = []
        for i in range(self.annotations):
            annotation = self.annotation(i)
            sublist = []
            if recursive and annotation.annotations:
                sublist = find_annotations(annotation,
                        handles=handles,
                        types=types,
                        rect=rect, half_open=half_open,
                        recursive=recursive)
            if (not rect or annotation.inside(rect)) and \
                    (not types or annotation.type in types) and \
                    (not handles or annotation.handle in handles):
                if sublist:
                    sublist.insert(0, annotation)
                    annotation_list.append(sublist)
                else:
                    annotation_list.append(annotation)
            elif sublist:
                sublist.insert(0, None)
                annotation_list.append(sublist)
        return annotation_list
