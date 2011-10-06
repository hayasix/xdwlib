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
import tempfile

from xdwapi import *
from observer import *
from timezone import JST


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


def inner_attribute_name(name):
    """Get XDWAPI style attribute name eg. font_name --> %FontName"""
    if name.startswith("%"):
        return name
    if "A" <= name[0] <= "Z":
        return "%" + name
    return "%" + "".join(map(lambda s: s.capitalize(), name.split("_")))


def outer_attribute_name(name):
    """Get xdwlib style attribute name eg. %FontName --> font_name"""
    import re
    if not name.startswith("%"):
        return name
    return re.sub("([A-Z])", r"_\1", name[1:])[1:].lower()


def adjust_path(path, default_dir="", coding=None):
    """Build a pathname by filename and default directory."""
    directory, basename = os.path.split(path)
    # Given no dir, create the new document in the same dir as original one.
    if not directory:
        path = os.path.join(default_dir, basename)
    if not os.path.splitext(basename)[1]:
        path += ".xdw"
    if coding:
        path = path.encode(coding)
    return path


class XDWTemp(object):

    """Temporary XDW file."""

    def __init__(self, dir, prefix="$$", suffix=".xdw"):
        self.fd, self.path = tempfile.mkstemp(suffix, prefix, dir)
        blank = join(dirname(abspath(__file__)), "__blank__.xdw")
        os.write(self.fd, data)
        return self.path

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    def close(self):
        os.fdopen(self.fd).close()
