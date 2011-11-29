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
import atexit
import tempfile
import base64

from xdwapi import *
from observer import *
from timezone import JST


__all__ = (
        "CP", "CODEPAGE", "DEFAULT_TZ",
        "EV_DOC_REMOVED", "EV_DOC_INSERTED",
        "EV_PAGE_REMOVED", "EV_PAGE_INSERTED",
        "EV_ANN_REMOVED", "EV_ANN_INSERTED",
        "PSEP", "ASEP",
        "BLANKPAGE",
        "XDWTemp",
        "inner_attribute_name", "outer_attribute_name",
        "adjust_path",
        "joinf",
        )


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


BLANKPAGE = base64.b64decode(
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
        "AAA=")


@atexit.register
def atexithandler():
    """Perform finalization before finishing this process."""
    XDW_Finalize()


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

    """Temporary XDW file with optional single blank page."""

    def __init__(self, suffix=".xdw", dir=None, blank_page=False):
        args = [suffix, "", dir] if dir else [suffix]
        self.fd, self.path = tempfile.mkstemp(*args)
        if blank_page:
            os.write(self.fd, BLANKPAGE)
        return self.path

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    def close(self):
        os.fdopen(self.fd).close()
