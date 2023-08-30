=============
Xdwlib README
=============

2023-08-30 HAYASHI Hideki <hideki@hayasix.com>


Welcome to the xdwlib source release
====================================

Xdwlib is a DocuWorks library for Python.

This document provides some general information about xdwlib source release.
Detailed description is available in docs/ only in Japanese at the moment.

Report problems with this release to the author.


License
-------

Copyright (C) 2010 HAYASHI Hideki

Xdwlib is provided under The Zope Public License (ZPL) Version 2.1,
which is included in 'LICENSE.rst'.  Send your feedback about the license
to the author.


Installation
============

System Requirements
-------------------

    - Microsoft Windows (versions compatible with DocuWorks 7+)

    - Python 3.7+

    - DocuWorks 7+ (Japanese version; English version may also work)

Install from archive
--------------------

Set PATH environment variable properly and issue the following command::

    python3 setup.py install

This will install xdwlib in $PYTHONPATH/xdwlib.

Install from PyPI
-----------------

Xdwlib is also delivered via Python Package Index (PyPI).  The latest
version of xdwlib will be installed by issuing::

    pip3 install xdwlib

If you have installed older version of xdwlib already, try::

    pip3 install --upgrade xdwlib

Optional Modules
----------------

PIL (Python Imaging Library)
''''''''''''''''''''''''''''

Xdwlib has been working with PIL (Python Imaging Library) if available,
to rotate pages for desired degrees other than right angles, and to copy
bitmap annotations.  Unfortunately the original PIL has not been ported
on Python 3 yet.

There is an alternative library called `Pillow` which will be a good
substitution.  Install Pillow by issuing::

    pip3 install pillow

cx_Freeze
'''''''''

The attached command line tool ``xdw2text.py`` can be compiled to .exe
with cx_Freeze package, a popular successor of py2exe.  To build your
own ``xdw2text.exe``, try::

    pip3 install cx_Freeze
    python3 cx_setup.py build

google-cloud-vision
'''''''''''''''''''

Native OCR is not available in DocuWorks >=9.1, so xdwlib offers OCR
by Microsoft Azure AI Vision or Google Cloud Vision (credentials required
for the services).  To use Google Cloud Vision, install this module::

    pip3 install google-cloud-vision


Documentation
=============

Detailed documents are available in Japanese at
`Read the Docs <https://xdwlib.readthedocs.io/ja/latest>`_.

Python's help() also gives brief descriptions in English.


Typical Use
===========

The following code will appy OCR and paste a date stamp on every page
as an annotation::

    import time

    from xdwlib import xdwopen, Point

    ...

    with xdwopen(PATHNAME, autosave=True) as doc:
        position = Point(pg.size - 100, pg.size - 20)
        datestamp = time.strftime("%Y-%m-%d")
        for pg in doc:
            pg.rotate(auto=True)
            pg.ocr(strategy="accuracy")
            ann = pg.add_text(position=position, text=datestamp)
            ann.fore_color = "red"


Reporting bugs
==============

The author appreciate bugs reports from you by email.


Have fun!
