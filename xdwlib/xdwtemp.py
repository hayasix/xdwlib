#!/usr/bin/env python
# vim: fileencoding=cp932 fileformat=dos

"""xdwtemp.py -- yet another tempfile module suitable for XDWAPI

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import sys
import os
from tempfile import mkstemp, mkdtemp


__all__ = ("XDWTemp",)


class XDWTemp(object):

    """Reusable pathname for a temporary file.

    Unlike tempfile.TemporaryFile, XDWTemp() provides a valid temporary
    pathname in a actually existing temporary directory.  Why XDWTemp()
    does not supply an existing file is that DocuWorks cannot handle
    shared files, even if it gets the write access.

    Technically, XDWTemp() creates a temporary directory in the standard
    temporary directory, like $TEMP or %TEMP%, creates a temporary file,
    delete the file immediately and returns the pathname of the deleted
    temporary file.  Uniqueness of the pathname of the temporary file is
    assured by its parent directory name.

    Example:

        temp = XDWTemp()  # Creates $TEMP/tmp-dir
        some_xdw_page.export(temp.path)  # Creates $TEMP/tmp-dir/tmp-file
        do_some_work(temp.path)
        temp.close()  # Deletes $TEMP/tmp-dir/tmp-file and $TEMP/tmp-dir

    or shortly,

        with XDWTemp() as temp:
            some_xdw_page.export(temp.path)
            do_some_work(temp.path)

    CAUTION: If XDWTemp object is deleted before close(), the associated
             temporary directory and file will still remain.

    ATTRIBUTES
    ----------

    path        (str) pathname of temporary file
    dir         (str) temporary directory name = os.path.split(path)[0]
    """

    def __init__(self, suffix=".xdw", prefix=""):
        """Initiator.

        suffix      (str or unicode) suffix of temporary file name
        prefix      (str or unicode) prefix of temporary file name
        """
        fd, path = mkstemp(suffix=suffix, prefix=prefix, dir=mkdtemp())
        os.close(fd)
        os.remove(path)  # Directory is not removed.
        self.path = path
        self.dir = os.path.split(path)[0]

    def __del__(self):
        self.close()

    def close(self):
        """Remove temporary file and directory."""
        if os.path.exists(self.path):
            os.remove(self.path)
        try:
            os.rmdir(self.dir)
        except Exception as e:
            import time
            sys.stderr.write("""\
{0}:xdwlib:can't delete temporary directory '{1}'\n""".format(
time.strftime("%Y-%m-%d %H:%M:%S"), self.dir))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
