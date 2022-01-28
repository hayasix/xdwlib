#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix expandtab :

"""struct.py -- Point and Rect

Copyright (C) 2010 HAYASHI Hideki <hideki@hayasix.com>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

from collections import namedtuple
import math


__all__ = ("Point", "Rect", "EPSILON")

PI = math.pi
EPSILON = 0.01  # mm


_Point = namedtuple("Point", "x y")


class Point(_Point):

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
    >>> p.rotate(30)
    Point(-5.00, 8.66)
    >>> p.rotate(30, origin=Point(10, 10))
    Point(1.34, 5.00)
    """

    def __str__(self):
        return f"({self.x:.2f}, {self.y:.2f})"

    def __repr__(self):
        return "Point" + self.__str__()

    def int(self):
        return Point(*map(int, self))

    fix = int

    def floor(self):
        return Point(*map(math.floor, self))

    def ceil(self):
        return Point(*map(math.ceil, self))

    @staticmethod
    def _round(f, places=0):
        # Round a number in accordance with the traditional way,
        # while Python's round() rounds to the nearest even number.
        return math.floor(f * math.pow(10, places) + .5) / math.pow(10, places)

    def round(self, places=0):
        return Point(self._round(self.x, places), self._round(self.y, places))

    def __bool__(self):
        return self != (0, 0)

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

    def __truediv__(self, n):
        if not isinstance(n, (int, float)):
            raise NotImplementedError
        return Point(self.x / n, self.y / n)

    def shift(self, pnt, _y = 0):
        if isinstance(pnt, (tuple, list)):
            return Point(self.x + pnt[0], self.y + pnt[1])
        elif isinstance(pnt, (int, float)) and isinstance(_y, (int, float)):
            return Point(self.x + pnt, self.y + _y)
        else:
            raise NotImplementedError

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


_Rect = namedtuple("_Rect", "left top right bottom")


class Rect(_Rect):

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
    >>> r.shift(Point(15, 25))
    Rect(15.00, 35.00, 35.00, 55.00)
    >>> r * 2
    Rect(0.00, 10.00, 40.00, 50.00)
    >>> r / 2
    Rect(0.00, 10.00, 10.00, 20.00)
    >>> list(r)
    [0, 10, 20, 30]
    >>> r == Rect(0, 10, 20, 30)
    True
    >>> r != Rect(0, 10, 20, 30)
    False
    >>> r.position()
    Point(0.00, 10.00)
    >>> r.size()
    Point(20.00, 20.00)
    >>> r.position_and_size()
    (Point(0.00, 10.00), Point(20.00, 20.00))
    """

    def __str__(self):
        return f"({', '.join(f'{x:.2f}' for x in self)})"

    def __repr__(self):
        return "Rect" + self.__str__()

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
        return Rect(*map(int, self))

    fix = int

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
                self.left + (self.right - self.left) * n,
                self.top + (self.bottom - self.top) * n)

    __rmul__ = __mul__

    def __truediv__(self, n):
        if not isinstance(n, (int, float)):
            raise NotImplementedError
        return Rect(self.left, self.top,
                self.left + (self.right - self.left) / n,
                self.top + (self.bottom - self.top) / n)

    def shift(self, pnt, _y=0):
        if isinstance(pnt, (tuple, list)):
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
