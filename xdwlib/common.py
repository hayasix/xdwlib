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
