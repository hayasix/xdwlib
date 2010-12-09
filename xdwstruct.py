#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""xdwlib.py -- DocuWorks library for Python.

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

__all__ = ("XDWPoint", "XDWRect")


class XDWPoint(object):

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __str__(self):
        return "(%f, %f)" % (self.x, self.y)

    def __repr__(self):
        return "%s%s" % (self.__class__.__name__, str(self))

    def __mul__(self, n):
        if not isinstance(n, (int, float)):
            raise NotImplementedError
        return XDWPoint(self.x * n, self.y * n)

    def __div__(self, n):
        if not isinstance(n, (int, float)):
            raise NotImplementedError
        return XDWPoint(self.x / n, self.y / n)

    def shift(self, pnt, _y=0):
        if isinstance(pnt, XDWPoint):
            x, y = pnt.x, pnt.y
        elif isinstance(pnt, (tuple, list)):
            x, y = pnt[:2]
        elif isinstance(pnt, (int, float)) and isinstance(_y, (int, float)):
            x, y = pnt, _y
        else:
            raise NotImplementedError
        return XDWPoint(self.x + x, self.y + y)


class XDWRect(object):

    def __init__(self, left=0, top=0, right=0, bottom=0):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def __str__(self):
        return "((%f, %f)-(%f, %f))" % (
                self.left, self.top, self.right, self.bottom)

    def __repr__(self):
        return "%s%s" % (self.__class__.__name__, str(self))

    def size(self):
        return XDWPoint(self.right - self.left, self.bottom - self.top)

    def __mul__(self, n):
        if not isinstance(n, (int, float)):
            raise NotImplementedError
        return XDWRect(self.left, self.top,
                self.left + float(self.right - self.left) * n,
                self.top + float(self.bottom - self.top) * n)

    def __div__(self, n):
        if not isinstance(n, (int, float)):
            raise NotImplementedError
        return XDWRect(self.left, self.top,
                self.left + float(self.right - self.left) / n,
                self.top + float(self.bottom - self.top) / n)

    def shift(self, pnt, _y=0):
        if isinstance(pnt, XDWPoint):
            x, y = pnt.x, pnt.y
        elif isinstace(pnt, (tuple, list)):
            x, y = pnt
        elif isinstance(pnt, (int, float)) and isinstance(_y, (int, float)):
            x, y = pnt, _y
        else:
            raise NotImplementedError
        return XDWRect(self.left + x, self.top + y,
                       self.right + x, self.bottom + y)
