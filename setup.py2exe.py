#!python.exe
# vim:fileencoding=utf-8

from distutils.core import setup
import py2exe

py2exe_options = dict(
    compressed = 1,
    optimize = 2,
    bundle_files = 1,
    )

setup(
    name="xdwlib",
    version="2.3.10",
    author="HAYASI Hideki",
    author_email="linxs@linxs.org",
    url="https://launchpad.net/xdwlib",
    description="xdwlib -- DocuWorks library for Python.",
    long_description="""xdwlib is a DocuWorks library for Python.
It supports almost all functions of original XDWAPI library from Fuji Xerox.
You can handle documents or binders in object-oriented style.  Pages and
annotations are also handled as objects.  Plus, every object is iterable.
""",
    license="ZPL 2.1",
    platforms=["win"],
    packages=["xdwlib",],
    options=dict(py2exe=py2exe_options),
    console=[ dict(
            script = "xdw2text.py",
            ), ],
    zipfile=None,
    )
