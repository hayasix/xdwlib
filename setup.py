#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix :

import sys
from distutils.core import setup

try:
    from cx_Freeze import setup, Executable
except ImportError:
    pass

from xdwlib import __author__, __copyright__, __license__, __version__, __email__


if sys.platform != "win32":
    sys.stderr.write("xdwlib runs on win32 only.")
    sys.exit(0)

# cx_Freeze
copyDependentFiles = True
silent = True

setup(
    name="xdwlib",
    version=__version__,
    author=__author__,
    author_email=__email__,
    url="https://launchpad.net/xdwlib/3.0",
    description="A DocuWorks library.",
    long_description="""xdwlib is a DocuWorks library for Python.
It supports almost all functions of original XDWAPI library from Fuji Xerox.
You can handle documents or binders in object-oriented style.  Pages and
annotations are also handled as objects.  Plus, every object is iterable.

You can read brief description with Python's lovely help() function.
Further information is available in Japanese at http://xdwlib.linxs.org/""",
    license=__license__,
    platforms=["win32",],
    packages=["xdwlib",],
    #data_files=["README", "LICENSE",],
    zipfile="xdwlib.zip",
    # cx_Freeze
    options=dict(build_exe=dict(
        includes=[],
        excludes=[],
        packages=[],
        )),
    executables=[Executable("xdw2text.py", base=None)],
    )
