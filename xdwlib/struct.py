#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""struct.py -- DocuWorks library for Python.

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

__all__ = ("Point", "Rect")


class Point(object):

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __str__(self):
        return "(%.2f, %.2f)" % (self.x, self.y)

    def __repr__(self):
        return "%s%s" % (self.__class__.__name__, str(self))

    def __iter__(self):
        for pos in range(2):
            yield (self.x, self.y)[pos]

    def __mul__(self, n):
        if not isinstance(n, (int, float)):
            raise NotImplementedError
        return Point(self.x * n, self.y * n)

    def __div__(self, n):
        if not isinstance(n, (int, float)):
            raise NotImplementedError
        return Point(self.x / n, self.y / n)

    def shift(self, pnt, _y=0):
        if isinstance(pnt, Point):
            x, y = pnt.x, pnt.y
        elif isinstance(pnt, (tuple, list)):
            x, y = pnt[:2]
        elif isinstance(pnt, (int, float)) and isinstance(_y, (int, float)):
            x, y = pnt, _y
        else:
            raise NotImplementedError
        return Point(self.x + x, self.y + y)


class Rect(object):

    def __init__(self, left=0, top=0, right=0, bottom=0):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def __str__(self):
        return "((%.2f, %.2f)-(%.2f, %.2f))" % (
                self.left, self.top, self.right, self.bottom)

    def __repr__(self):
        return "%s%s" % (self.__class__.__name__, str(self))

    def __iter__(self):
       for pos in range(4):
            yield (self.left, self.top, self.right, self.bottom)[pos]

    def size(self):
        return Point(self.right - self.left, self.bottom - self.top)

    def __mul__(self, n):
        if not isinstance(n, (int, float)):
            raise NotImplementedError
        return Rect(self.left, self.top,
                self.left + float(self.right - self.left) * n,
                self.top + float(self.bottom - self.top) * n)

    def __div__(self, n):
        if not isinstance(n, (int, float)):
            raise NotImplementedError
        return Rect(self.left, self.top,
                self.left + float(self.right - self.left) / n,
                self.top + float(self.bottom - self.top) / n)

    def shift(self, pnt, _y=0):
        if isinstance(pnt, Point):
            x, y = pnt.x, pnt.y
        elif isinstace(pnt, (tuple, list)):
            x, y = pnt
        elif isinstance(pnt, (int, float)) and isinstance(_y, (int, float)):
            x, y = pnt, _y
        else:
            raise NotImplementedError
        return Rect(self.left + x, self.top + y,
                       self.right + x, self.bottom + y)
