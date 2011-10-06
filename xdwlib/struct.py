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

    """Point represented by 2D coordinate.

    >>> p = Point(0, 10)
    >>> p
    Point(0.00, 10.00)
    >>> p + Point(5, 10)
    Point(5.00, 20.00)
    >>> p - Point(5, 10)
    Point(-5.00, 0.00)
    >>> -p
    Point(0.00, -10.00)
    >>> p * 2
    Point(0.00, 20.00)
    >>> p / 2
    Point(0.00, 5.00)
    >>> p.shift(Point(20, 30))
    Point(20.00, 40.00)
    >>> p.shift([20, 30])
    Point(20.00, 40.00)
    >>> p.shift(20)
    Point(20.00, 10.00)
    >>> list(p)
    [0, 10]
    """

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

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __add__(self, pnt):
        return self.shift(pnt)

    def __sub__(self, pnt):
        return self.shift(-pnt)

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

    """Half-open rectangular region.

    A region is represented by half-open coodinate intervals.  Left-top
    coordinate is inclusive but right-bottom one is exclusive.

    >>> r = Rect(0, 10, 20, 30)
    >>> r
    Rect((0.00, 10.00)-(20.00, 30.00))
    >>> r.position()
    Point(0.00, 10.00)
    >>> r.size()
    Point(20.00, 20.00)
    >>> r = Rect(Point(0, 10), Point(20, 30))
    >>> r.size()
    Point(20.00, 20.00)
    >>> r.shift(Point(15, 25))
    Rect((15.00, 35.00)-(35.00, 55.00))
    >>> r * 2
    Rect((0.00, 10.00)-(40.00, 50.00))
    >>> r / 2
    Rect((0.00, 10.00)-(10.00, 20.00))
    >>> list(r)
    [0, 10, 20, 30]
    """

    def __init__(self, *args, **kw):
        if args:
            if len(args) == 2:
                ((left, top), (right, bottom)) = args
            elif len(args) == 4:
                left, top, right, bottom = args
            else:
                raise TypeError("argument should be 4 numerics or 2 Points")
        else:
            for k, v in kw.items():
                k = k.upper()
                if k in ("LEFT", "L"):
                    left = v
                elif k in ("TOP", "T"):
                    top = v
                elif k in ("RIGHT", "R"):
                    right = v
                elif k in ("BOTTOM", "B"):
                    bottom = v
                elif k in ("LEFTTOP", "LT"):
                    left, top = v
                elif k in ("RIGHTBOTTOM", "RB"):
                    right, bottom = v
                else:
                    raise TypeError("unexpected keyword '%s'", k)
        if right < left:
            left, right = right, left
        if bottom < top:
            top, bottom = bottom, top
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

    def position(self):
        return Point(self.left, self.top)

    def size(self):
        return Point(self.right - self.left, self.bottom - self.top)

    def position_and_size(self):
        return (self.position(), self.size())

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
