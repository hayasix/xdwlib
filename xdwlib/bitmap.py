#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""bitmap.py -- DIB (Device Independent Bitmap), aka BMP

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""


from ctypes import *


__all__ = ("Bitmap",)


class BitmapInfoHeader(Structure):

    """BITMAPINFOHEADER for Windows Bitmap data body."""

    _fields_ = [
            ("biSize", c_uint32),  # DWORD
            ("biWidth", c_int32),  # LONG
            ("biHeight", c_int32),  # LONG
            ("biPlanes", c_uint16),  # WORD
            ("biBitCount", c_uint16),  # WORD
            ("biCompression", c_uint32),  # DWORD
            ("biSizeImage", c_uint32),  # DWORD
            ("biXPelsPerMeter", c_int32),  # LONG
            ("biYPelsPerMeter", c_int32),  # LONG
            ("biClrUsed", c_uint32),  # DWORD
            ("biClrImportant", c_uint32),  # DWORD
            ]


class Bitmap(object):

    """DIB (Device Independent Bitmap)"""

    def __init__(self, bitmap_info_header_p):
        self.header = BitmapInfoHeader()
        memmove(pointer(self.header), bitmap_info_header_p, sizeof(self.header))
        self.data = create_string_buffer(self.header.biSizeImage)
        memmove(pointer(self.data),
                bitmap_info_header_p + sizeof(self.header),
                self.header.biSizeImage)

    def __getattr__(self, name):
        if name == "width": return self.header.biWidth
        if name == "height": return self.header.biHeight
        if name == "planes": return self.header.biPlanes
        if name == "depth": return self.header.biBitCount
        if name == "compression": return self.header.biCompression
        if name == "data_size": return self.header.biSizeImage
        if name == "resolution": return (self.header.biXPelsPerMeter, self.header.biYPelsPerMeter)
        if name == "color_used": return self.header.biClrUsed
        if name == "color_important": return self.header.biClrImportant
        raise AttributeError("'Bitmap' object has no attribute '%s'" % name)

    @staticmethod
    def _pack16(n):
        return chr(n & 0xff) + chr((n >> 8) & 0xff)

    @staticmethod
    def _pack32(n):
        s = []
        for _ in range(4):
            s.append(chr(n & 0xff))
            n >>= 8
        return "".join(s)

    def file_header(self):
        s = []
        s.append("BM")
        s.append(self._pack32(14 + 40 + self.data_size))
        s.append(self._pack16(0))
        s.append(self._pack16(0))
        s.append(self._pack32(14 + 40))
        return "".join(s)

    def info_header(self):
        header = create_string_buffer(40)
        memmove(header, pointer(self.header), 40)
        return header.raw

    def octet_stream(self):
        return "".join([self.file_header(), self.info_header(), self.data.raw])

    def save(self, stream):
        is_path = isinstance(stream, basestring)
        if is_path:
            stream = open(stream, "wb")
        stream.write(self.octet_stream())
        if is_path:
            stream.close()
