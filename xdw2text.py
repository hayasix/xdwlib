#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""xdwlib.py -- DocuWorks library for Python.

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import sys

from xdwlib import xdwopen
from xdwlib.xdwapi import XDWError, XDW_E_INVALIDARG


OPTION_ASK = False
OPTION_SILENT = False


def parse():

    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-a", "--all",
            action="store_const", dest="spec",
            const="Title,Subject,Author,Keywords,Comments,fulltext",
            help="all properties, content text and annotation text")
    parser.add_option("--text",
            action="store_const", dest="spec", const="fulltext",
            help="document text, OCR text and text annotations")
    parser.add_option("--content-text", "--page-text",
            action="store_const", dest="spec", const="content_text",
            help="document text and OCR text")
    parser.add_option("--annotation-text",
            action="store_const", dest="spec", const="annotation_text",
            help="text annotations")
    parser.add_option("--properties",
            action="store_const", dest="spec",
            const="Title,Subject,Author,Keywords,Comments",
            help="all properties ie. title, subject, author, keyword and comment")
    parser.add_option("--title",
            action="store_const", dest="spec", const="Title",
            help="document title")
    parser.add_option("--subject",
            action="store_const", dest="spec", const="Subject",
            help="document subject (or subtitle)")
    parser.add_option("--author",
            action="store_const", dest="spec", const="Author",
            help="document author")
    parser.add_option("--keyword",
            action="store_const", dest="spec", const="Keywords",
            help="document keywords")
    parser.add_option("--comment",
            action="store_const", dest="spec", const="Comments",
            help="document comments")
    parser.add_option("-u", action="store_true", dest="unicode",
            help="Unicode ie. UTF-16, not multibyte (MBCS)")
    parser.add_option("-d", action="store_true", dest="ask",
            help="ask if input is DocuWorks file or not; returns error code")
    parser.add_option("-v", action="store_true", dest="showversion",
            help="output version information to stdout")
    parser.add_option("-s", action="store_true", dest="silent",
            help="silent mode; no output, including error messages")
    parser.add_option("-p", action="store_true", dest="pipe",
            help="output to pipe")
    return parser.parse_args()


def exit(xdwerror, verbose=False):
    if verbose:
        print xdwerror
    sys.exit(xdwerror.error_code)


if __name__ == "__main__":

    options, args = parse()

    if len(args) < 1:
        exit(XDWError(XDW_E_INVALIDARG), not options.silent)

    if len(args) < 2:
        options.pipe = True

    try:
        doc = xdwopen(args[0], readonly=True, authenticate=False)
    except XDWError as e:
        if options.ask:
            exit(e, not options.silent)
        else:
            raise
    if options.ask:
        sys.exit(0)

    if not options.spec:
        options.spec = "fulltext"

    out = []
    for name in options.spec.split(","):
        try:
            text = getattr(doc, name)
            if callable(text):
                text = text()
            out.append("%s=%s" % (name, text))
        except KeyError:
            pass
    out = "".join(out)
    if options.pipe:
        print out
    else:
        with open(arg[1], "w") as of:
            of.writelines(out)
