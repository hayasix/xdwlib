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
    options = dict(py2exe = py2exe_options),
    console = [ dict(
            script = "xdw2text.py",
            ), ],
    zipfile = None,
    )
