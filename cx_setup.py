#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix :

import sys

try:
    from cx_Freeze import setup, Executable
except ImportError:
    print("cx_Freeze is not available.  Abort.")
    sys.exit(-1)

from xdwlib import __author__, __copyright__, __license__, __version__, __email__


if sys.platform != "win32":
    sys.stderr.write("xdwlib runs on win32 only.")
    sys.exit(-1)

copyDependentFiles = True
silent = True

setup(
    name="xdwlib",
    version=__version__,
    author=__author__,
    author_email=__email__,
    platforms=["win32",],
    packages=["xdwlib",],
    zipfile="xdwlib.zip",
    executables=[Executable("xdw2text.py", base=None)],
    options=dict(build_exe=dict(
        includes=[],
        excludes=[],
        packages=[],
        )),
    )
