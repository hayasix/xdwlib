#!python.exe
# vim:fileencoding=utf-8

from distutils.core import setup
import py2exe

from xdwlib import __author__, __copyright__, __license__, __version__, __email__

setup(
    name="xdwlib",
    version=__version__,
    author=__author__,
    author_email=__email__,
    url="https://launchpad.net/xdwlib",
    description="xdwlib -- DocuWorks library for Python.",
    long_description="""xdwlib is a DocuWorks library for Python.
It supports almost all functions of original XDWAPI library from Fuji Xerox.
You can handle documents or binders in object-oriented style.  Pages and
annotations are also handled as objects.  Plus, every object is iterable.""",
    license=__license__,
    platforms=["win32",],
    packages=["xdwlib",],
    console=["xdw2text.py",],
    options={"py2exe": {"optimize": 1},},
    zipfile="xdwlib.zip",
    )
