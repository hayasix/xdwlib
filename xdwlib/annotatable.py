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
from observer import Subject
from struct import Point


__all__ = ("Annotatable",)


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
        return self.annotation(pos)

    def __setitem__(self, pos, val):
        raise NotImplementedError()

    def __iter__(self):
        self._pos = 0
        return self

    def next(self):
        if self.annotations <= self._pos:
            raise StopIteration
        ann = self.annotation(self._pos)
        self._pos += 1
        return ann

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
        info = XDW_ANNOTATION_INFO()
        info.handle = ann_handle
        info.nHorPos = int(position.x * 100)
        info.nVerPos = int(position.y * 100)
        info.nWidth = 0
        info.nHeight = 0
        info.nAnnotationType = ann_type
        info.nChildAnnotations = 0
        pos = self.annotations  # TODO: Ensure this is correct.
        ann = Annotation(self.page, pos, parent=self, info=info)
        self.annotations += 1
        self.notify(event=Notification(EV_ANN_INSERTED, pos))
        return ann

    def add_text_annotation(self, text, position=Point(0, 0), **kw):
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
        return  joinf(ASEP, [self.content_text(), self.annotation_text(recursive=True)])

    def find_annotations(self, handles=None, types=None, rect=None,
            half_open=True, recursive=False):
        """Find annotations on self, page or annotation, which meets criteria given.

        find_annotations(handles=None, types=None, rect=None, half_open=True, recursive=False)
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

