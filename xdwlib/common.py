#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""common.py -- common utility functions

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import os
import re
from tempfile import mkstemp, mkdtemp
import base64
import time
import datetime

from xdwapi import *
from observer import *
from timezone import *


__all__ = (
        "CP", "CODEPAGE", "DEFAULT_TZ",
        "EV_DOC_REMOVED", "EV_DOC_INSERTED",
        "EV_PAGE_REMOVED", "EV_PAGE_INSERTED",
        "EV_ANN_REMOVED", "EV_ANN_INSERTED",
        "PSEP", "ASEP", "BLANKPAGE",
        "mm2in", "in2mm", "mm2px", "px2mm",
        "environ", "get_viewer",
        "inner_attribute_name", "outer_attribute_name",
        "adjust_path", "cp", "uc", "derivative_path", "mktemp", "rmtemp",
        "joinf", "flagvalue", "typevalue", "makevalue", "scale", "unpack",
        "XDWTemp",
        )


PSEP = "\f"  # page separator
ASEP = "\v"  # annotation separator

CP = 932
CODEPAGE = "cp{0}".format(CP)

DEFAULT_TZ = JST

# Observer pattern event
EV_DOC_REMOVED = 11
EV_DOC_INSERTED = 12
EV_PAGE_REMOVED = 21
EV_PAGE_INSERTED = 22
EV_ANN_REMOVED = 31
EV_ANN_INSERTED = 32
EV_ATT_REMOVED = 41
EV_ATT_INSERTED = 42

BLANKPAGE = (
        "YA6CAQeAAwDAE4MEAQ0KAWGCBK1jggSNBFFr4XC6JKM++++6O4EEUJcYphV1"
        "osL07eKZEHLrKOXKqTPdU0hx157ungI4gKmjnlFRpjAsV5muZ2XThEGiGR2n"
        "iF1zPnAKss5KtFsbNUpRnSqPv/3PjX7bNSJpY5XTaCsR0wSJKusrBWWdLyrE"
        "Msou1vll1krNm2vooFQ/euyQ6/Urj/m8FZcWNbZCp/9nrY5egbL1DRm3sC3r"
        "w5tosRYkMsqzcvVFyj4+jePde7dvX7NzxbfCjvZgrNBg+DjoebHSGez7WEsg"
        "fpsV2J3ZizVos+4WY26y1cuta7SEtarad06t9DvJ+/fvdD1N1x5bgPLKSl4m"
        "fwNBey7+w2Pz775qGZ3lf6E3M8H6bgrEjPMZ/zHkv4sk1jpHiY+FvbbHvm3v"
        "SEK6tvi1chsqHLe33Kzm/s5konWpJ9ySgmtt2JDk7m842/1kWWiZ3nLz9ybH"
        "SMn6N7lbLBvcP4N9bdr5aEvDiYGW+yhq/UcRKie8S+m7Gh3pZ+I8k67z8DRa"
        "LMYeMyMWl+/EwXEPJlM8/qFlHHM3+s4KfKy7nQYeP+2alrTqceBJzkvl/G8l"
        "jtuuv8lVZ0thyuzH3c72Kyw/SsoLtq3Yc0fBxJT633I+qcpvYyFzrf8fZ59P"
        "c1rhRfusnH5ydVVsfjQYmr08Wf4HDvXnF3aNnruZ5Dh/4W/qYmY7mS+Gt03V"
        "uZLIcupzNppOB62cxtlS6WpqJ2klevaWF5ue71f5m5iZ5XQTQTFrcdLn+nu8"
        "/dPuXF7MncI9y8/XGOW+GnvXeUuam3w7aqkL+buO86Xxuj6dvZuLN3f9rx8H"
        "YS8pNcTC3Tz9/D/2L/fb03R+j8rL3dVY76/5FZuPatuNt7K09fi5qroX2jqq"
        "ra4GFvPj2Exc5LN+lfa2cuuTqYMPOrjQTOQmLuCs1E1dsJq2NavA61cuxwtp"
        "CY4UyQhHgbEKxGxGftRnCE/hbvvTJ/3xQmCcKApV+hQmCcKApVaChME4UBSq"
        "+FCYJwoClXUChME4UBSrshQmCcKApV3hnhgnCgKVYMKEwThQFKsQFCYJwoCl"
        "WNChME4UBSrJBQmCcKApVlwoTBOFAUqzgzg1nhwoClUBChME4UBSqDBQmCcK"
        "ApVCwoTBOFAUqiAUJgnCgKVRUKEwThQFKo0FjYJPG4gKVR8KEwThQFKpIFCY"
        "JwoClUpChME4UBSqXBQmCcKApVMwoTBOFAUqnAWNBVEbBrPEqnoUJgnCgKVa"
        "CChME4UBSrQ4UJgnCgKVaMChME4UBSrSIUJgnCgKVaWCxpQpjQZZwalWmwoT"
        "BOFAUq1AFCYJwoClWpQoTBOFAUq1UFCYJwoClWrwoTBOFAUhG2ongq29s7iy"
        "T0y00ndosCO02exytv0TF89Mbz7yPvs72a+gkHD2kd0tVAc6gVfNbZpvmW5W"
        "/linqmfRtX+cwuu5h1+ryOlI9JRkpyUpIATEqCZMjgWZxG9Lr7F9LrRpS0+u"
        "Iu15yzQVWGKYwqc/FqVIqdCNZ2GH78VOiq6O6Z6Kv4Ks7ukFTpKs9FTCp01V"
        "KeAO5OV1pR017/sBaYtCOxaHgGUagAEAggEAgwIHJ4QCBI2FBFLFTQqGBBoA"
        "AAA=").decode("base64")

INCH = 25.4
mm2in = lambda v: v / INCH
in2mm = lambda v: v * INCH
mm2px = lambda v, dpi: v / INCH * dpi
px2mm = lambda v, dpi: v / dpi * INCH


def environ(name=None):
    """DocuWorks environment information."""
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
        except InfoNotFoundError as e:
                continue
    return values


def get_viewer(light=False, lightonly=False):
    """Get pathname of DocuWorks Viewer (Light).

    light       (bool) force to use DocuWorks Viewer Light.  Note that
                DocuWorks Viewer is used if Light version is not avaiable.
    """
    env = environ()
    viewer = env.get("DWVIEWERPATH")
    if light or not viewer:
        viewer = env.get("DWVLTPATH", viewer)
    if not viewer:
        raise NotInstalledError("DocuWorks Viewer (Light) is not installed")
    return viewer


def joinf(sep, seq):
    """sep.join(seq), omitting None, null or so."""
    return sep.join([s for s in filter(bool, seq)]) or None


def inner_attribute_name(name):
    """Get XDWAPI style attribute name e.g. font_name --> %FontName"""
    if name.startswith("%"):
        return name
    if "A" <= name[0] <= "Z":
        return "%" + name
    return "%" + "".join(map(lambda s: s.capitalize(), name.split("_")))


def outer_attribute_name(name):
    """Get xdwlib style attribute name e.g. %FontName --> font_name"""
    if not name.startswith("%"):
        return name
    return re.sub("([A-Z])", r"_\1", name[1:])[1:].lower()


def adjust_path(path, dir="", ext=".xdw", coding=None):
    """Build a new pathname with filename and directory name.

    path    (unicode) pathname
            Full pathname is acceptable as well as bare filename (basename);
            only its basename is taken.
    dir     (unicode) directory part of new pathname
            If dir is given, directory part of path is ignored.
    ext     (unicode) default extension to append if original path has no one
    coding  (str/unicode) encoding of the result; None = unicode
    """
    directory, basename = os.path.split(path)
    directory = dir or directory or os.getcwd()
    path = os.path.abspath(os.path.join(directory, basename))
    if not os.path.splitext(basename)[1]:
        path += "." + ext.lstrip(".")
    if coding and isinstance(path, unicode):
        path = path.encode(coding)
    return path


def cp(s):
    """Coerce unicode into str."""
    if not s:
        return ""
    if isinstance(s, unicode):
        return s.encode(CODEPAGE)
    if not isinstance(s, str):
        raise TypeError("str or unicode expected")
    return s


def uc(s):
    """Coerce str into unicode."""
    if not s:
        return u""
    if isinstance(s, str):
        return s.decode(CODEPAGE)
    if not isinstance(s, unicode):
        raise TypeError("str or unicode expected")
    return s


def derivative_path(path):
    """Convert pathname to n-th derivative e.g. somedocument-2.xdw or so.

    Addtional number (2, 3, ...) is determined automatically.
    If pathname given does not exist, original pathname is returned.
    """
    if not os.path.exists(path):
        return path
    root, ext = os.path.splitext(path)
    n = 2
    derivative = "{0}-{1}{2}".format(root, n, ext)
    while os.path.exists(derivative):
        n += 1
        derivative = "{0}-{1}{2}".format(root, n, ext)
    return derivative


def mktemp(suffix=".xdw", prefix="", nofile=False):
    fd, temp = mkstemp(suffix=suffix, prefix=prefix, dir=mkdtemp())
    os.close(fd)
    if nofile:
        os.remove(temp)  # Directory is not removed.
    return temp


def rmtemp(path):
    if os.path.exists(path):
        os.remove(path)
    os.rmdir(os.path.split(path)[0])


def flagvalue(table, value, store=True):
    """Sum up flag values according to XDWConst table."""
    if store and isinstance(value, (int, float)):
        return int(value)
    if store:
        if not value:
            return 0
        value = [table.normalize(f.strip()) for f in value.split(",") if f]
        if not value:
            return 0
        return reduce(lambda x, y: x | y, value)
    return ",".join(table[b] for b in sorted(table.keys()) if b & value)


def typevalue(value):
    """Determine object type by object itself."""
    if isinstance(value, bool):
        return (XDW_ATYPE_BOOL, c_int(-1 if value else 0))
    if isinstance(value, int):
        return (XDW_ATYPE_INT, c_int(value))
    elif isinstance(value, str):
        return (XDW_ATYPE_STRING, value)
    elif isinstance(value, unicode):
        return (XDW_ATYPE_STRING, value)
    elif isinstance(value, datetime.date):
        value = int(time.mktime(value.timetuple()) - time.timezone)
        return (XDW_ATYPE_DATE, c_int(value))
    else:
        return (XDW_ATYPE_OTHER, value)


def makevalue(t, value):
    t = XDW_ATTRIBUTE_TYPE.normalize(t)
    if t == XDW_ATYPE_INT:
        return int(value)
    elif t == XDW_ATYPE_STRING:
        return unicode(value)
    elif t == XDW_ATYPE_DATE:
        return datetime.date.fromtimestamp(value + time.timezone)
    elif t == XDW_ATYPE_BOOL:
        return bool(value)
    return value


def scale(attrname, value, store=False):
    """Scale actual size (length) to stored value and vice versa."""
    unit = XDW_ANNOTATION_ATTRIBUTE[attrname][1]
    if not unit:
        return value
    if isinstance(unit, XDWConst):
        if attrname in (XDW_ATN_FontStyle, XDW_ATN_FontPitchAndFamily):
            return flagvalue(unit, value, store=store)
        if store:
            return unit.normalize(value)
        return unit[value]
    mo = re.match(r"(1/)?([\d.]+)", unit)
    if not mo:
        return float(value)
    inv, unit = mo.groups()
    if bool(inv) ^ store:
        return value / float(unit)
    else:
        return value * float(unit)


def unpack(s):
    """Unpack little-endian octets into int."""
    n = 0
    for c in s:
        n <<= 8
        n += ord(c)
    return n


class XDWTemp(object):

    """Temporary XDW file with optional single blank page."""

    def __init__(self, suffix=".xdw", dir=None, blank_page=False):
        args = [suffix, "", dir] if dir else [suffix]
        self.fd, self.path = mkstemp(*args)
        if blank_page:
            os.write(self.fd, BLANKPAGE)

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    def __del__(self):
        try:
            os.fdopen(self.fd).close()
        except:
            pass
        os.remove(self.path)

    def close(self):
        os.fdopen(self.fd).close()

    def seek(self, pos, how=0):
        """Change read/write pointer in the temporary file.

        pos     position in stream by bytes
        how     base; 0=top, 1=current, 2=bottom
        """
        os.lseek(self.fd, pos, how)

    def read(self, size):
        return os.read(self.fd, size)
