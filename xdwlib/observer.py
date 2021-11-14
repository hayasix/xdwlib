#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix expandtab :

"""observer.py -- implementation for observer pattern

Copyright (C) 2010 HAYASHI Hideki <hideki@hayasix.com>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

__all__ = ("Subject", "Observer", "Notification")


class Subject(object):

    def __init__(self):
        self.observers = dict()

    def shift_keys(self, border, delete=False, count=1):
        for pos in sorted([p for p in self.observers.keys() if border < p],
                reverse=(not delete)):
            gap = -count if delete else count
            self.observers[pos + gap] = self.observers[pos]
            del self.observers[pos]

    def attach(self, observer, event):
        self.shift_keys(observer.pos)
        self.observers[observer.pos] = observer
        self.notify(event=Notification(event, observer.pos))

    def detach(self, observer, event=None):
        del self.observers[observer.pos]
        self.shift_keys(observer.pos, delete=True)
        self.notify(event=Notification(event, observer.pos))

    def notify(self, event=None):
        for pos in self.observers:
            self.observers[pos].update(event)


class Observer(object):

    def __init__(self, subject, event):
        pass

    def update(self, event):
        raise NotImplementedError  # abstract


class Notification(object):

    def __init__(self, type, *para):
        self.type = type
        self.para = para
