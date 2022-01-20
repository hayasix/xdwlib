#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix expandtab :

"""annotatable.py -- Annotatable, base class for Page and Annotation

Copyright (C) 2010 HAYASHI Hideki <hideki@hayasix.com>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import os
import warnings

from .xdwapi import *
from .common import *
from .xdwtemp import XDWTemp
from .observer import *
from .struct import *


__all__ = ("Annotatable",)


MIN_ANN_SIZE = 3
ANN_TOO_SMALL = f"Annotation size must be >= {MIN_ANN_SIZE}mm square"
MIN_FUSEN_SIZE = 5
FUSEN_TOO_SMALL = f"Stickey size must be >= {MIN_FUSEN_SIZE}mm square"

_WIDTH = 75
_HEIGHT = 25
_POSITION = Point(_HEIGHT, _HEIGHT)
_SIZE = Point(_WIDTH, _HEIGHT)
_RECT = Rect(_HEIGHT, _HEIGHT, _HEIGHT + _WIDTH, _HEIGHT + _HEIGHT)
_POINTS = (
        _POSITION,
        _POSITION + Point(_WIDTH, 0),
        _POSITION + _SIZE,
        _POSITION + Point(0, _HEIGHT))


def relative_points(points):
    """Convert point sequence in absolute coordinate to xdwapi-style."""
    if len(points) < 2:
        return points
    p0 = points[0]
    return tuple([p0] + [p - p0 for p in points[1:]])


class Annotatable(Subject):

    """Annotatable objects i.e. page or annotation."""

    def _pos(self, pos, append=False):
        append = 1 if append else 0
        if not (-self.annotations <= pos < self.annotations + append):
            raise IndexError(
                    "Annotation number {0} not in [{1}, {2})".format(
                    pos, -self.annotations, self.annotations + append))
        if pos < 0:
            pos += self.annotations
        return pos

    def _slice(self, pos):
        if pos.step == 0 and pos.start != pos.stop:
            raise ValueError("slice.step must not be 0")
        return slice(
                self._pos(pos.start or 0),
                self.annotations if pos.stop is None else pos.stop,
                1 if pos.step is None else pos.step)

    def __len__(self):
        return self.annotations

    def __getitem__(self, pos):
        if isinstance(pos, slice):
            pos = self._slice(pos)
            return tuple(self.annotation(p)
                    for p in range(pos.start, pos.stop, pos.step or 1))
        return self.annotation(pos)

    def __setitem__(self, pos, val):
        raise NotImplementedError()

    def __delitem__(self, pos):
        if isinstance(pos, slice):
            deleted = 0
            for p in range(pos.start, pos.stop, pos.step or 1):
                self.delete(p - deleted)
                deleted += 1
        return self.delete(pos)

    def __iter__(self):
        for pos in range(self.annotations):
            yield self.annotation(pos)

    def annotation(self, pos):
        """Get an annotation by position."""
        from .annotation import Annotation
        pos = self._pos(pos)
        if pos not in self.observers:
            self.observers[pos] = Annotation(self, pos, parent=self)
        return self.observers[pos]

    @staticmethod
    def initial_data(ann_type, **kw):
        """Generate annotation-type-specific initialization data."""
        try:
            cls = XDW_AID_INITIAL_DATA[ann_type]
        except KeyError:
            raise ValueError(f"illegal annotation type {ann_type}")
        if cls is None:
            return None
        init_dat = cls()
        init_dat.common.nAnnotationType = \
                XDW_ANNOTATION_TYPE.normalize(ann_type)
        for k, v in kw.items():
            if k.startswith("n"):
                v = int(v)
            elif k.startswith("sz"):
                v = cp(v)
            elif k.startswith("wsz"):
                k = k[1:]
                v = str(v)
            elif k.startswith("lpsz"):
                v = byref(cp(v))
            elif k.startswith("lpwsz"):
                k = "lpsz" + k[5:]
                v = byref(v)
            elif k.startswith("p"):
                v = pointer(v[0])
            else:
                raise TypeError(f"unknown type '{k}'")
            setattr(init_dat, k, v)
        return init_dat

    def _add(self, ann_type, position, init_dat):
        """Abstract method as a stub for add()."""
        raise NotImplementedError()

    def add(self, ann_type, position, **kw):
        """Paste an annotation.

        ann_type    annotation type by inner code
        position    (Point, unit=mm) location to paste
        **kw        initial data; varies by ann_type
        """
        from .annotation import Annotation
        ann_type = XDW_ANNOTATION_TYPE.normalize(ann_type)
        if isinstance(position, (tuple, list)):
            position = Point(*position)
        init_dat = Annotatable.initial_data(ann_type, **kw)
        ann_handle = self._add(ann_type, position, init_dat)
        pos = self.annotations  # TODO: Ensure this is correct.
        self.annotations += 1
        ann = self.annotation(pos)
        return ann

    def add_text(self, position=_POSITION, **kw):
        """Paste a text annotation.

        position    (Point, unit=mm)
        kw          (dict) initial attributes
        """
        ann = self.add(XDW_AID_TEXT, position)
        for k, v in kw.items():
            setattr(ann, k, v)
        return ann

    def add_link(self, position=_POSITION, **kw):
        """Paste a link annotation.

        position    (Point, unit=mm)
        kw          (dict) initial attributes
        """
        ann = self.add(XDW_AID_LINK, position)
        for k, v in kw.items():
            setattr(ann, k, v)
        return ann

    def add_stickey(self, position=_POSITION, size=_SIZE, **kw):
        """Paste a stickey annotation.

        position    (Point, unit=mm)
        size        (Point, unit=mm)
        kw          (dict) initial attributes
        """
        if size.x < MIN_FUSEN_SIZE or size.y < MIN_FUSEN_SIZE:
            raise ValueError(FUSEN_TOO_SMALL)
        ann = self.add(XDW_AID_FUSEN, position,
                nWidth=(size.x * 100), nHeight=(size.y * 100))
        for k, v in kw.items():
            setattr(ann, k, v)
        return ann

    def add_line(self, points=_POINTS[:2], **kw):
        """Paste a straight line annotation.

        points      (2-element sequence of Point, unit=mm)
        kw          (dict) initial attributes

        Note that `position' attribute is determined automatically.
        """
        if 2 < len(points):
            raise ValueError("> 2 points given; consider add_lines()")
        points = relative_points(points)
        ann = self.add(XDW_AID_STRAIGHTLINE, points[0],
                nHorVec=(points[1].x * 100), nVerVec=(points[1].y * 100))
        for k, v in kw.items():
            setattr(ann, k, v)
        return ann

    add_straightline = add_line

    def add_rectangle(self, rect=_RECT, **kw):
        """Paste a rectangular annotation.

        rect        (Rect, unit=mm)
        kw          (dict) initial attributes
        """
        position, size = rect.position_and_size()
        if size.x < MIN_ANN_SIZE or size.y < MIN_ANN_SIZE:
            raise ValueError(ANN_TOO_SMALL)
        ann = self.add(XDW_AID_RECTANGLE, position,
                nWidth=(size.x * 100), nHeight=(size.y * 100))
        for k, v in kw.items():
            setattr(ann, k, v)
        return ann

    add_rect = add_rectangle

    def add_arc(self, rect=_RECT, **kw):
        """Paste an ellipse annotation.

        rect        (Rect, unit=mm)
        kw          (dict) initial attributes
        """
        position, size = rect.position_and_size()
        if size.x < MIN_ANN_SIZE or size.y < MIN_ANN_SIZE:
            raise ValueError(ANN_TOO_SMALL)
        ann = self.add(XDW_AID_ARC, position,
                nWidth=(size.x * 100), nHeight=(size.y * 100))
        for k, v in kw.items():
            setattr(ann, k, v)
        return ann

    add_ellipse = add_arc

    def add_bitmap(self, position=_POSITION, path=None, **kw):
        """Paste an image annotation.

        position    (Point, unit=mm)
        path        (str) path to image file
        kw          (dict) initial attributes
        """
        if 8 <= XDWVER:
            ann = self.add(XDW_AID_BITMAP, position, wszImagePath=path)
        else:
            ann = self.add(XDW_AID_BITMAP, position, szImagePath=path)
        for k, v in kw.items():
            setattr(ann, k, v)
        return ann

    def add_stamp(self, position=_POSITION, width=_WIDTH, **kw):
        """Paste a (date) stamp annotation.

        position    (Point, unit=mm)
        width       (float, unit=mm)
        kw          (dict) initial attributes
        """
        ann = self.add(XDW_AID_STAMP, position,
                nWidth=(width * 100))
        for k, v in kw.items():
            setattr(ann, k, v)
        return ann

    '''
    def add_receivedstamp(self, position=_POSITION, width=_WIDTH, **kw):
        """Paste a received stamp annotation.

        position    (Point, unit=mm)
        width       (float, unit=mm)
        kw          (dict) initial attributes
        """
        ann = self.add(XDW_AID_RECEIVEDSTAMP, position,
                nWidth=(width * 100))
        for k, v in kw.items():
            setattr(ann, k, v)
        return ann

    def add_custom(self, position=_POSITION,
                size=_SIZE, guid="???", data="???", **kw):
        """Paste a custom specification annotation.

        position    (Point, unit=mm)
        size        (Point, unit=mm)
        guid        (str)
        data        (str)
        kw          (dict) initial attributes
        """
        ann = self.add(XDW_AID_CUSTOM, position,
                nWidth=(size.x * 100), nHeight=(size.y * 100),
                lpszGuid=guid,
                nCustomDataSize=len(data), pCustomData=data)
        for k, v in kw.items():
            setattr(ann, k, v)
        return ann
    '''

    def add_marker(self, points=_POINTS, **kw):
        """Paste a marker annotation.

        points      (sequence of Point, unit=mm)
        kw          (dict) initial attributes

        Note that `position' attribute is determined automatically.
        """
        points = relative_points(points)
        c_points = (XDW_POINT * len(points))()
        for i, p in enumerate(points):
            c_points[i].x = int(p.x * 100)
            c_points[i].y = int(p.y * 100)
        ann = self.add(XDW_AID_MARKER, _POSITION,  # position is dummy
                nCounts=len(points), pPoints=c_points)
        for k, v in kw.items():
            setattr(ann, k, v)
        return ann

    add_lines = add_marker  # add a series of straight lines

    def add_polygon(self, points=_POINTS, **kw):
        """Paste a polygon annotation.

        points      (sequence of Point, unit=mm)
        kw          (dict) initial attributes

        Note that `position' attribute is determined automatically.
        """
        points = relative_points(points)
        c_points = (XDW_POINT * len(points))()
        for i, p in enumerate(points):
            c_points[i].x = int(p.x * 100)
            c_points[i].y = int(p.y * 100)
        ann = self.add(XDW_AID_POLYGON, _POSITION,  # position is dummy
                nCounts=len(points), pPoints=c_points)
        for k, v in kw.items():
            setattr(ann, k, v)
        return ann

    def copy_annotation(self, ann, strategy=1):
        """Copy an annotation with the same position and attributes.

        ann         (Annotation)

        BITMAP can be copied, but it takes great time to process image.
        PAGEFORM, OLE, CUSTOM and RECEIVEDSTAMP are not copyable.
        """
        t = XDW_ANNOTATION_TYPE.normalize(ann.type)
        if t == XDW_AID_TEXT:
            copy = self.add_text(position=ann.position)  # updated later
        elif t == XDW_AID_STAMP:
            copy = self.add_stamp(position=ann.position, width=ann.size.x)
        elif t in (XDW_AID_FUSEN, XDW_AID_RECTANGLE, XDW_AID_ARC):
            copy = self.add(t, position=ann.position,
                    nWidth=(self.size.x * 100), nHeight=(self.size.y * 100))
        elif t == XDW_AID_STRAIGHTLINE:
            copy = self.add_line(ann.points)
        elif t == XDW_AID_MARKER:
            copy = self.add_marker(ann.points)
        elif t == XDW_AID_POLYGON:
            copy = self.add_polygon(ann.points)
        elif t == XDW_AID_LINK:
            copy = self.add_link(position=ann.position)
        elif t == XDW_AID_BITMAP:
            if not PIL_ENABLED:
                warnings.warn("install Pillow before copying bitmap annotation",
                        UserWarning, stacklevel=2)
                return None
            pg = ann.page
            dpi = max(pg.resolution)
            lt, rb = ann.position, ann.position + ann.size
            rect = [int(round(mm2px(v, dpi))) for v in (lt.x, lt.y, rb.x, rb.y)]
            if strategy == 1:
                with XDWTemp(suffix=".bmp") as temp:
                    pg.doc.export_image(pg.pos, temp.path,
                            dpi=dpi, format="bmp", compress="nocompress")
                    Image.open(temp.path).crop(rect).save(temp.path, "BMP")
                    # PIL BmpImagePlugin sets resolution to 1, so fix it.
                    self._fix_bmp_resolution(temp.path, dpi)
            elif strategy == 2:
                with XDWTemp(suffix=".tif") as temp:
                    in_ = StringIO(pg.doc.bitmap(pg.pos).octet_stream())
                    Image.open(in_).crop(rect).\
                            save(temp.path, "TIFF", resolution=dpi)
                    in_.close()
            else:
                raise ValueError("illegal strategy")
            copy = self.add(t, position=ann.position, szImagePath=temp.path)
        else:  # XDW_AID_PAGEFORM, XDW_AID_OLE, XDW_AID_RECEIVEDSTAMP, XDW_AID_CUSTOM
            warnings.warn(
                    f"copying {ann.type} annotation is not supported",
                    DeprecationWarning, stacklevel=2)
            return None
        kw = ann.attributes()
        for k, v in kw.items():
            if k in ("points",):  # This attribute cannot be updated.
                continue
            if k == "size":
                if (t == XDW_AID_TEXT and (
                            not ann.word_wrap or ann.text_orientation != 0) or
                        t == XDW_AID_LINK and ann.auto_resize):
                    continue
            setattr(copy, k, v)
        return copy

    @staticmethod
    def _fix_bmp_resolution(path, dpi):
        """Fix resolutions stored in BMP file.

        path    (str) path to Windows Bitmap file
        dpi     (int) resolution in DPI
        """
        ppm = int(round(dpi * mm2in(1000)))
        ppms = []
        for _ in range(4):
            ppms.append(chr(ppm & 0xff))
            ppm >>= 8
        ppm = "".join(ppms)
        with open(path, "r+b") as im:
            im.seek(0x26)
            im.write(ppm)  # horizontal resolution
            im.write(ppm)  # vertical resolution

    def _delete(self, pos):
        """Abstract method as a stub for delete()."""
        raise NotImplementedError()

    def delete(self, pos):
        """Remove an annotation.

        pos         (int) annotation position in page
        """
        pos = self._pos(pos)
        ann = self.annotation(pos)
        self._delete(ann)
        self.detach(ann, EV_ANN_REMOVED)
        self.annotations -= 1

    def content_text(self, recursive=True):
        """Abstract method for concrete content_text()."""
        raise NotImplementedError()

    def annotation_text(self, recursive=True):
        """Get text in child/descendant annotations.

        recursive   (bool) get content text of descendants also
        """
        result = []
        for ann in self:
            result.append(ann.content_text())
            if ann.annotations and recursive:
                result.append(ann.annotation_text(recursive=True))
        return joinf(ASEP, result)

    def fulltext(self):
        """Get text in this object and all descendant annotations."""
        return  joinf(ASEP, [
                self.content_text(),
                self.annotation_text(recursive=True)])

    def find_annotations(self, criteria=None,
            handles=None, types=None, rect=None,
            half_open=True, recursive=False):
        """Find annotations on page or annotation by criteria.

        criteria    Function to determine if annotation is chosen.
                    The function should take one argument as Annotation
                    and return True (chosen) or False.
                    None means all.
        handles     Sequence of annotation handles.  None means all.
        types       Sequence of types.  None means all.
        rect        Rect which includes annotations.
                    Note that right and bottom values are innermost of
                    outside unless half_open==False.  None means all.
        recursive   also return descendant (child) annotations.
        """
        if handles and not isinstance(handles, (tuple, list)):
            handles = list(handles)
        if types:
            if not isinstance(types, (list, tuple)):
                types = [types]
        if rect and not half_open:
            rect = rect.half_open()
        ann_list = []
        for ann in self:
            # TODO: test by rect is currently done in relative coordinate.
            # Absolute coordinate would be preferable.
            if not ((not rect or ann.inside(rect)) and
                    (not types or ann.type in types) and
                    (not handles or ann.handle in handles) and
                    (not criteria or criteria(ann))):
                continue
            ann_list.append(ann)
            if recursive and ann.annotations:
                ann_list.extend(
                        ann.find_annotations(criteria=criteria,
                                handles=handles, types=types, rect=rect,
                                half_open=half_open, recursive=recursive))
        return ann_list
