#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix expandtab :

"""__init__.py -- initiator for xdwlib, A DocuWorks library for Python.

Copyright (C) 2010 HAYASHI Hideki <hideki@hayasix.com>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import sys

from .__setup__ import *
from .struct import Point, Rect
from .common import environ
from .xdwtemp import XDWTemp
from .xdwfile import xdwopen, view, optimize, copy, create_sfx, extract_sfx
from .xdwfile import protection_info, protect, unprotect, sign
from .document import Document, create, merge, Container
from .binder import Binder, create, create_binder
from .documentinbinder import DocumentInBinder
from .page import Page, PageCollection
from .annotation import Annotation, AnnotationCache
