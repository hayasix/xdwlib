#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""xdwlib -- DocuWorks library for Python.

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

from os.path import splitext, basename

from common import *
from binder import Binder, copy_pages_to_binder
from document import Document
from documentinbinder import DocumentInBinder
from page import Page
from annotation import Annotation


def xdwopen(path, readonly=False, authenticate=True):
    """General opener"""
    types = {
            ".XDW": Document,
            ".XBD": Binder,
            }
    ext = splitext(basename(path))[1].upper()
    if ext not in types:
        raise XDWError(XDW_E_INVALIDARG)
    return types[ext](path, readonly=readonly, authenticate=authenticate)
