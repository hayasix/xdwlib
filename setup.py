#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix expandtab :

import sys
from setuptools import setup


if sys.platform != "win32":
    sys.stderr.write("warning: xdwlib runs on win32 only.")

setup()
