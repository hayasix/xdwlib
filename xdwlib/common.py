#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""common.py -- DocuWorks library for Python.

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import os

from xdwapi import *
from struct import Point, Rect
from observer import Subject, Observer, Notification
from timezone import Timezone, UTC, JST, unixtime, fromunixtime


PSEP = "\f"
ASEP = "\v"

CP = 932
CODEPAGE = "cp%d" % CP
DEFAULT_TZ = JST


# Observer pattern event
EV_DOC_REMOVED = 11
EV_DOC_INSERTED = 12
EV_PAGE_REMOVED = 21
EV_PAGE_INSERTED = 22
EV_ANN_REMOVED = 31
EV_ANN_INSERTED = 32


def create(
        inputPath,
        outputPath,
        size=XDW_SIZE_A4_PORTRAIT,
        fit_image=XDW_CREATE_FIT,
        compress=XDW_COMPRESS_LOSSLESS,
        zoom=100,
        width=0.0, height=0.0,
        horizontal_position=XDW_CREATE_HCENTER,
        vertical_position=XDW_CREATE_VCENTER,
        ):
    """A XDW generator"""
    opt = XDW_CREATE_OPTION()
    opt.nSize = normalize_binder_size(size)
    opt.nFitImage = fit_image
    opt.nCompress = compress
    opt.nZoom = int(zoom)
    opt.nWidth = int(width * 100)
    opt.nHeight = int(height * 100)
    opt.nHorPos = int(horizontal_position * 100)
    opt.nVerPos = int(vertical_position * 100)
    XDW_CreateXdwFromImageFile(inputPath, outputPath, opt)


def create_binder(path, color=XDW_BINDER_COLOR_0, size=XDW_SIZE_FREE, coding=CODEPAGE):
    """The XBD generator"""
    data = XDW_BINDER_INITIAL_DATA()
    data.nBinderColor = color
    data.nBinderSize = size
    XDW_CreateBinder(path.encode(coding), data)


def environ(name=None):
    """DocuWorks environment information"""
    if name:
        value = XDW_GetInformation(XDW_ENVIRON.normalize(name))
        if name == XDW_ENVIRON[XDW_GI_DWDESK_FILENAME_DIGITS]:
            value = ord(value)
        return value
    values = dict()
    for k, v in XDW_ENVIRON.items():
        try:
            value = XDW_GetInformation(k)
            if k == XDW_GI_DWDESK_FILENAME_DIGITS:
                value = ord(value)
            values[v] = value
        except XDWError as e:
            if e.error_code == XDW_E_INFO_NOT_FOUND:
                continue
            else:
                raise
    return values
def joinf(sep, seq):
    """sep.join(seq), omitting None, null or so."""
    return sep.join([s for s in filter(bool, seq)]) or None


def find_annotations(obj, handles=None, types=None, rect=None,
        half_open=True, recursive=False):
    """Find annotations on obj, page or annotation, which meets criteria given.

    find_annotations(object, handles=None, types=None, rect=None,
            half_open=True, recursive=False)
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
    for i in range(obj.annotations):
        annotation = obj.annotation(i)
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


def inner_attribute_name(name):
    if name.startswith("%"):
        return name
    if "A" <= name[0] <= "Z":
        return "%" + name
    return "%" + "".join(map(lambda s: s.capitalize(), name.split("_")))


def outer_attribute_name(name):
    import string, re
    if not name.startswith("%"):
        return name
    return re.sub("([A-Z])", r"_\1", name[1:])[1:].lower()

def new_filename(path, dir="", coding=None):
    dirname, name = os.path.split(path)
    # Given no dir, create the new document in the same dir as original one.
    if not dirname: path = os.path.join(dir, name)
    if not os.path.splitext(name)[1]: path += ".xdw"
    if coding: path = path.encode(coding)
    return path

