#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""timezone.py -- time zone

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import time
import datetime


__all__ = ("Timezone", "UTC", "JST", "unixtime", "fromunixtime")


class Timezone(datetime.tzinfo):

    def __init__(self, tzname, utcoffset, dst=0):
        self._tzname = tzname
        self._utcoffset = datetime.timedelta(hours=-utcoffset)
        self._dst = datetime.timedelta(dst)

    def tzname(self, dt=None):
        return self._tzname

    def utcoffset(self, dt=None):
        return self._utcoffset

    def dst(self, dt=None):
        return self._dst


UTC = Timezone("UTC", 0)
JST = Timezone("JST", -9)


def unixtime(dt):
    return time.mktime(dt.utctimetuple())


def fromunixtime(t):
    return datetime.datetime.utcfromtimestamp(t)
