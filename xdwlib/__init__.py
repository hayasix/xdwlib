#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix :

"""__init__.py -- initiator for xdwlib, A DocuWorks library for Python.

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

from .struct import Point, Rect
from .common import environ
from .xdwtemp import XDWTemp
from .xdwfile import xdwopen, view, optimize, copy, create_sfx, extract_sfx
from .xdwfile import protection_info, protect, unprotect, sign
from .document import Document, create, merge
from .binder import Binder, create_binder
from .documentinbinder import DocumentInBinder
from .page import Page, PageCollection
from .annotation import Annotation, AnnotationCache


__author__ = "HAYASI Hideki"
__copyright__ = "Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>"
__license__ = "ZPL 2.1"
__version__ = "3.8.2.0"
__email__ = "linxs@linxs.org"
__status__ = "Development"
