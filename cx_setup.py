#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix expandtab :

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
    url="https://github.com/hayasix/xdwlib",
    description="A DocuWorks library.",
    long_description="""xdwlib is a DocuWorks library for Python.
It supports almost all functions of original XDWAPI library from Fuji Xerox.
You can handle documents or binders in object-oriented style.  Pages and
annotations are also handled as objects.  Plus, every object is iterable.

You can read brief description with Python's lovely help() function.
Further information is available in Japanese at https://github.com/hayasix/xdwlib/docs/""",
    license=__license__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Office/Business',
        'Topic :: Documentation',
        ],
    python_requires=">=3.7",
    platforms=["win32",],
    packages=["xdwlib",],
    #install_requires=["pillow>=3.3.3",],
    #data_files=["README.rst", "LICENSE.rst",],
    zipfile="xdwlib.zip",
    executables=[Executable("scripts/xdw2text.py", base=None)],
    options=dict(build_exe=dict(
        includes=[],
        excludes=[],
        packages=[],
        )),
    )
