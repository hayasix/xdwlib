#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""struct.py -- Point and Rect

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import math


__all__ = ("Point", "Rect", "EPSILON")

PI = math.pi
EPSILON = 0.01  # mm


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
    Point(-0.00, -10.00)
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
    [0.0, 10.0]
    >>> p == Point(0, 10)
    True
    >>> p != Point(0, 10)
    False
    >>> p == Point(5, 10)
    False
    >>> p != Point(5, 10)
    True
    >>> bool(p)
    True
    >>> bool(Point(0, 0))
    False
    """

    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)

    def __str__(self):
        return "({0:.2f}, {1:.2f})".format(self.x, self.y)

    def __repr__(self):
        return "{cls}({pts})".format(
                cls=self.__class__.__name__,
                pts=", ".join("{0:.2f}".format(f) for f in self))

    def __iter__(self):
        for f in (self.x, self.y):
            yield f

    def int(self):
        """Special method to adapt to XDW_POINT."""
        result = Point()
        result.x = int(self.x)
        result.y = int(self.y)
        return result

    def floor(self):
        return Point(math.floor(self.x), math.floor(self.y))

    def ceil(self):
        return Point(math.ceil(self.x), math.ceil(self.y))

    def fix(self):
        return Point(int(self.x), int(self.y))

    @staticmethod
    def _round(f, places=0):
        return math.floor(f * math.pow(10, places) + .5) / math.pow(10, places)

    def round(self, places=0):
        return Point(self._round(self.x, places), self._round(self.y, places))

    def __eq__(self, pnt):
        return self.x == pnt.x and self.y == pnt.y

    def __ne__(self, pnt):
        return self.x != pnt.x or self.y != pnt.y

    def __nonzero__(self):
        return self.x != 0 or self.y != 0

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

    __rmul__ = __mul__

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

    def rotate(self, degree, origin=None):
        p = Point(*self)
        if origin is not None:
            p -= origin
        rad = PI * degree / 180.0
        sin, cos = math.sin(rad), math.cos(rad)
        p = Point(p.x * cos - p.y * sin, p.x * sin + p.y * cos)
        if origin is not None:
            p += origin
        return p


class Rect(object):

    """Half-open rectangular region.

    A region is represented by half-open coodinate intervals.  Left-top
    coordinate is inclusive but right-bottom one is exclusive.

    >>> r = Rect(0, 10, 20, 30)
    >>> r
    Rect(0.00, 10.00, 20.00, 30.00)
    >>> r.position()
    Point(0.00, 10.00)
    >>> r.size()
    Point(20.00, 20.00)
    >>> r = Rect(Point(0, 10), Point(20, 30))
    >>> r.size()
    Point(20.00, 20.00)
    >>> r.shift(Point(15, 25))
    Rect(15.00, 35.00, 35.00, 55.00)
    >>> r * 2
    Rect(0.00, 10.00, 40.00, 50.00)
    >>> r / 2
    Rect(0.00, 10.00, 10.00, 20.00)
    >>> list(r)
    [0.0, 10.0, 20.0, 30.0]
    >>> r == Rect(0, 10, 20, 30)
    True
    >>> r != Rect(0, 10, 20, 30)
    False
    """

    def __init__(self, *args, **kw):
        left = top = right = bottom = 0
        half_open = True
        if args:
            if len(args) == 2:
                ((left, top), (right, bottom)) = args
            elif len(args) == 4:
                left, top, right, bottom = args
            else:
                raise TypeError("argument must be 4 numerics or 2 Points")
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
                elif k == "HALF_OPEN":
                    half_open = v
                else:
                    raise TypeError("unexpected keyword '{0}'".format(k))
        if right < left:
            left, right = right, left
        if bottom < top:
            top, bottom = bottom, top
        self.left = float(left)
        self.top = float(top)
        self.right = float(right)
        self.bottom = float(bottom)
        if not half_open:  # Enforce half open.
            self.right += EPSILON
            self.bottom += EPSILON

    def __str__(self):
        return "({0:.2f}, {1:.2f})-({2:.2f}, {3:.2f})".format(
                self.left, self.top, self.right, self.bottom)

    def __repr__(self):
        return "{cls}({pts})".format(
                cls=self.__class__.__name__,
                pts=", ".join("{0:.2f}".format(f) for f in self))

    def __iter__(self):
        for f in (self.left, self.top, self.right, self.bottom):
            yield f

    def half_open(self):
        """Get half-open version i.e. right-bottom is excluded."""
        return Rect(self.left, self.top,
                self.right + EPSILON, self.bottom + EPSILON)

    def closed(self):
        """Get closed version i.e. rigit-bottom is included."""
        return Rect(self.left, self.top,
                self.right - EPSILON, self.bottom - EPSILON)

    def int(self):
        """Special method to adapt to XDW_RECT."""
        result = Rect()
        result.left = int(self.left)
        result.top = int(self.top)
        result.right = int(self.right)
        result.bottom = int(self.bottom)
        return result

    def position(self):
        return Point(self.left, self.top)

    def size(self):
        return Point(self.right - self.left, self.bottom - self.top)

    def position_and_size(self):
        return (self.position(), self.size())

    def __eq__(self, rect):
        return (self.left == rect.left and self.top == rect.top and
                self.right == rect.right and self.bottom == rect.bottom)

    def __ne__(self, rect):
        return (self.left != rect.left or self.top != rect.top or
                self.right != rect.right or self.bottom != rect.bottom)

    def __mul__(self, n):
        if not isinstance(n, (int, float)):
            raise NotImplementedError
        return Rect(self.left, self.top,
                self.left + (self.right - self.left) * n,
                self.top + (self.bottom - self.top) * n)

    __rmul__ = __mul__

    def __div__(self, n):
        if not isinstance(n, (int, float)):
            raise NotImplementedError
        return Rect(self.left, self.top,
                self.left + (self.right - self.left) / n,
                self.top + (self.bottom - self.top) / n)

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

    def rotate(self, degree, origin=None):
        return Rect(p.rotate(degree, origin=origin) for p in self)


if __name__ == "__main__":

    import doctest
    doctest.testmod()
