#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix :

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
import base64
import time
import datetime
from functools import reduce

from .xdwapi import *
from .observer import *
from .timezone import *


__all__ = (
        "PIL_ENABLED",
        "CP", "CODEPAGE", "DEFAULT_TZ",
        "EV_DOC_REMOVED", "EV_DOC_INSERTED",
        "EV_PAGE_REMOVED", "EV_PAGE_INSERTED",
        "EV_ANN_REMOVED", "EV_ANN_INSERTED",
        "PSEP", "ASEP", "BLANKPAGE",
        "mm2in", "in2mm", "mm2px", "px2mm",
        "environ", "get_viewer",
        "inner_attribute_name", "outer_attribute_name",
        "adjust_path", "cp", "uc", "derivative_path",
        "joinf", "flagvalue", "typevalue", "makevalue", "scale", "unpack",
        )


PIL_ENABLED = True
try:
    import Image
except ImportError:
    try:
        from PIL import Image
    except ImportError:
        PIL_ENABLED = False
if PIL_ENABLED:
    __all__ += ("Image",)


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

BLANKPAGE = base64.b64decode(
        b"YA6CAQeAAwDAE4MEAQ0KAWGCBK1jggSNBFFr4XC6JKM++++6O4EEUJcYphV1"
        b"osL07eKZEHLrKOXKqTPdU0hx157ungI4gKmjnlFRpjAsV5muZ2XThEGiGR2n"
        b"iF1zPnAKss5KtFsbNUpRnSqPv/3PjX7bNSJpY5XTaCsR0wSJKusrBWWdLyrE"
        b"Msou1vll1krNm2vooFQ/euyQ6/Urj/m8FZcWNbZCp/9nrY5egbL1DRm3sC3r"
        b"w5tosRYkMsqzcvVFyj4+jePde7dvX7NzxbfCjvZgrNBg+DjoebHSGez7WEsg"
        b"fpsV2J3ZizVos+4WY26y1cuta7SEtarad06t9DvJ+/fvdD1N1x5bgPLKSl4m"
        b"fwNBey7+w2Pz775qGZ3lf6E3M8H6bgrEjPMZ/zHkv4sk1jpHiY+FvbbHvm3v"
        b"SEK6tvi1chsqHLe33Kzm/s5konWpJ9ySgmtt2JDk7m842/1kWWiZ3nLz9ybH"
        b"SMn6N7lbLBvcP4N9bdr5aEvDiYGW+yhq/UcRKie8S+m7Gh3pZ+I8k67z8DRa"
        b"LMYeMyMWl+/EwXEPJlM8/qFlHHM3+s4KfKy7nQYeP+2alrTqceBJzkvl/G8l"
        b"jtuuv8lVZ0thyuzH3c72Kyw/SsoLtq3Yc0fBxJT633I+qcpvYyFzrf8fZ59P"
        b"c1rhRfusnH5ydVVsfjQYmr08Wf4HDvXnF3aNnruZ5Dh/4W/qYmY7mS+Gt03V"
        b"uZLIcupzNppOB62cxtlS6WpqJ2klevaWF5ue71f5m5iZ5XQTQTFrcdLn+nu8"
        b"/dPuXF7MncI9y8/XGOW+GnvXeUuam3w7aqkL+buO86Xxuj6dvZuLN3f9rx8H"
        b"YS8pNcTC3Tz9/D/2L/fb03R+j8rL3dVY76/5FZuPatuNt7K09fi5qroX2jqq"
        b"ra4GFvPj2Exc5LN+lfa2cuuTqYMPOrjQTOQmLuCs1E1dsJq2NavA61cuxwtp"
        b"CY4UyQhHgbEKxGxGftRnCE/hbvvTJ/3xQmCcKApV+hQmCcKApVaChME4UBSq"
        b"+FCYJwoClXUChME4UBSrshQmCcKApV3hnhgnCgKVYMKEwThQFKsQFCYJwoCl"
        b"WNChME4UBSrJBQmCcKApVlwoTBOFAUqzgzg1nhwoClUBChME4UBSqDBQmCcK"
        b"ApVCwoTBOFAUqiAUJgnCgKVRUKEwThQFKo0FjYJPG4gKVR8KEwThQFKpIFCY"
        b"JwoClUpChME4UBSqXBQmCcKApVMwoTBOFAUqnAWNBVEbBrPEqnoUJgnCgKVa"
        b"CChME4UBSrQ4UJgnCgKVaMChME4UBSrSIUJgnCgKVaWCxpQpjQZZwalWmwoT"
        b"BOFAUq1AFCYJwoClWpQoTBOFAUq1UFCYJwoClWrwoTBOFAUhG2ongq29s7iy"
        b"T0y00ndosCO02exytv0TF89Mbz7yPvs72a+gkHD2kd0tVAc6gVfNbZpvmW5W"
        b"/linqmfRtX+cwuu5h1+ryOlI9JRkpyUpIATEqCZMjgWZxG9Lr7F9LrRpS0+u"
        b"Iu15yzQVWGKYwqc/FqVIqdCNZ2GH78VOiq6O6Z6Kv4Ks7ukFTpKs9FTCp01V"
        b"KeAO5OV1pR017/sBaYtCOxaHgGUagAEAggEAgwIHJ4QCBI2FBFLFTQqGBBoA"
        b"AAA=")

INCH = 25.4
mm2in = lambda v: v / INCH
in2mm = lambda v: v * INCH
mm2px = lambda v, dpi: v / INCH * dpi
px2mm = lambda v, dpi: v / dpi * INCH


def environ(name=None):
    """DocuWorks environment information."""
    it = XDW_GI_DWDESK_FILENAME_DIGITS
    if name:
        value = XDW_GetInformation(XDW_ENVIRON.normalize(name))
        return ord(value) if name == XDW_ENVIRON[it] else uc(value)
    values = dict()
    for k, v in XDW_ENVIRON.items():
        try:
            value = XDW_GetInformation(k)
            values[v] = ord(value) if k == it else uc(value)
        except InfoNotFoundError as e:
            continue
    return values


def linkfolders():
    result = dict()
    for i in range(XDW_GetLinkRootFolderNumber()):
        info = XDW_GetLinkRootFolderInformation(i + 1)
        result[info.szLinkRootFolderName.decode(CODEPAGE)] = info.szPath.decode(CODEPAGE)
    return result


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
    if isinstance(name, bytes):
        return name
    if name.startswith("%"):
        return cp(name)
    if "A" <= name[0] <= "Z":
        return cp("%" + name)
    return cp("%" + "".join([s.capitalize() for s in name.split("_")]))


def outer_attribute_name(name):
    """Get xdwlib style attribute name e.g. %FontName --> font_name"""
    if isinstance(name, str):
        return name
    name = uc(name)
    if not name.startswith("%"):
        return name
    return re.sub("([A-Z])", r"_\1", name[1:])[1:].lower()


def adjust_path(path, dir="", ext=".xdw", coding=None):
    """Build a new pathname with filename and directory name.

    path    (str) pathname
            Full pathname is acceptable as well as bare filename (basename).
    dir     (str) replacement directory
    ext     (str) default extension to append if original path has no one
    coding  (str) encoding of the result as bytes; None = str (don't encode)

    Returns a full pathname.

    Example:

    >>> import os; os.getcwd()
    'C:\\your\\favorite\\directory'
    >>> adjust_path('')
    ''
    >>> adjust_path('example.xdw')
    'C:\\your\\favorite\\directory\\example.xdw'
    >>> adjust_path('example.xdw', dir='C:\\another\\directory')
    'C:\\another\\directory\\example.xdw'
    >>> adjust_path('C:\\your\\favorite\\directory\\example.xdw',
    ...     dir='C:\\another\\directory')
    'C:\\another\\directory\\example.xdw'
    >>> adjust_path('example.xdw', dir='C:\\another\\directory', ext='.pdf')
    'C:\\another\\directory\\example.xdw'
    >>> adjust_path('example', dir='C:\\another\\directory', ext='.pdf')
    'C:\\another\\directory\\example.pdf'
    """
    if not (path or dir):
        return ""
    directory, basename = os.path.split(path)
    directory = dir or directory or os.getcwd()
    path = os.path.abspath(os.path.join(directory, basename))
    if basename and not os.path.splitext(basename)[1]:
        path += "." + ext.lstrip(".")
    if coding and isinstance(path, str):
        path = path.encode(coding)
    return path


def cp(s):
    """Coerce str into bytes."""
    if not s:
        return b""
    if isinstance(s, str):
        return s.encode(CODEPAGE)
    if isinstance(s, bytes):
        return s
    raise TypeError("str or bytes expected, {0} given".format(s.__class__))


def uc(s):
    """Coerce bytes into str."""
    if not s:
        return ""
    if isinstance(s, bytes):
        return s.decode(CODEPAGE)
    if isinstance(s, str):
        return s
    raise TypeError("str or bytes expected, {0} given".format(s.__class__))


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
    """Get XDWAPI-compatible type and ctypes-compatible value."""
    if isinstance(value, bool):
        return (XDW_ATYPE_BOOL, c_int(-1 if value else 0))
    if isinstance(value, int):
        return (XDW_ATYPE_INT, c_int(value))
    #elif isinstance(value, bytes):
    #    return (XDW_ATYPE_STRING, value)
    elif isinstance(value, str):
        return (XDW_ATYPE_STRING, value)
    elif isinstance(value, datetime.date):
        value = int(time.mktime(value.timetuple()) - time.timezone)
        return (XDW_ATYPE_DATE, c_int(value))
    else:
        return (XDW_ATYPE_OTHER, value)


def makevalue(t, value):
    """Get value of ctypes-compatible value in XDWAPI-compatible type."""
    t = XDW_ATTRIBUTE_TYPE.normalize(t)
    if t == XDW_ATYPE_INT:
        return int(value)
    elif t == XDW_ATYPE_STRING:
        return str(value)
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
