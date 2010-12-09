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
from os.path import splitext, basename
import datetime

from xdwapi import *
from xdwstruct import XDWPoint, XDWRect
from xdwobserver import XDWSubject, XDWObserver, XDWNotification
from xdwtimezone import Timezone, UTC, JST, unixtime, fromunixtime


__all__ = (
        "XDWDocument", "XDWDocumentInBinder", "XDWBinder",
        "XDWError",
        "environ", "xdwopen", "create", "create_binder",
        "PSEP", "ASEP",
        )

PSEP = "\f"
ASEP = "\v"

CP = 932
CODEPAGE = "cp%d" % CP
DEFAULT_TZ = JST


def DPRINT(*args):
    sys.stderr.write(" ".join(map(lambda x: str(x) \
            if hasattr(x, "__str__") and callable(x.__str__) \
            else "<???>", args)) + "\n")

# Observer pattern event
EV_DOC_REMOVED = 11
EV_DOC_INSERTED = 12
EV_PAGE_REMOVED = 21
EV_PAGE_INSERTED = 22
EV_ANN_REMOVED = 31
EV_ANN_INSERTED = 32

# The last resort to close documents in interactive session.
try:
    VALID_DOCUMENT_HANDLES
except NameError:
    VALID_DOCUMENT_HANDLES = []


def _join(sep, seq):
    """sep.join(seq), omitting None, null or so."""
    return sep.join([s for s in filter(bool, seq)]) or None


def environ(name=None):
    """DocuWorks environment information"""
    if name:
        value = XDW_GetInformation(XDW_ENVIRON.normalize(name))
        if name == XDW_ENVIRON[XDW_GI_DWDESK_FILENAME_DIGITS]:
            value = ord(value)
        return value
    values = dict()
    for k, v in XDW_ENVIRON.items():
        try:
            value = XDW_GetInformation(k)
            if k == XDW_GI_DWDESK_FILENAME_DIGITS:
                value = ord(value)
            values[v] = value
        except XDWError as e:
            if e.error_code == XDW_E_INFO_NOT_FOUND:
                continue
            else:
                raise
    return values


def xdwopen(path, readonly=False, authenticate=True):
    """General opener"""
    types = {
            ".XDW": XDWDocument,
            ".XBD": XDWBinder,
            }
    ext = splitext(basename(path))[1].upper()
    if ext not in types:
        raise XDWError(XDW_E_INVALIDARG)
    return types[ext](path, readonly=readonly, authenticate=authenticate)


def create(
        inputPath,
        outputPath,
        size=XDW_SIZE_A4_PORTRAIT,
        fit_image=XDW_CREATE_FIT,
        compress=XDW_COMPRESS_LOSSLESS,
        zoom=100,
        width=0.0, height=0.0,
        horizontal_position=XDW_CREATE_HCENTER,
        vertical_position=XDW_CREATE_VCENTER,
        ):
    """A XDW generator"""
    opt = XDW_CREATE_OPTION()
    opt.nSize = normalize_binder_size(size)
    opt.nFitImage = fit_image
    opt.nCompress = compress
    opt.nZoom = int(zoom)
    opt.nWidth = int(width * 100)
    opt.nHeight = int(height * 100)
    opt.nHorPos = int(horizontal_position * 100)
    opt.nVerPos = int(vertical_position * 100)
    XDW_CreateXdwFromImageFile(inputPath, outputPath, opt)


def create_binder(path, color=XDW_BINDER_COLOR_0, size=XDW_SIZE_FREE):
    """The XBD generator"""
    XDW_CreateBinder(path, color, size)


def find_annotations(obj, handles=None, types=None, rect=None,
        half_open=True, recursive=False):
    """Find annotations on obj, page or annotation, which meets criteria given.

    find_annotations(object, handles=None, types=None, rect=None,
            half_open=True, recursive=False)
        handles     sequence of annotation handles.  None means all.
        types       sequence of types.  None means all.
        rect        XDWRect which includes annotations,
                    Note that right/bottom value are innermost of outside
                    unless half_open==False.  None means all.
        recursive   also return descendant (child) annotations.
    """
    if handles and not isinstance(handles, (tuple, list)):
        handles = list(handles)
    if types:
        if not isinstance(types, (list, tuple)):
            types = [types]
        types = [XDW_ANNOTATION_TYPE.normalize(t) for t in types]
    if rect and not half_open:
        rect.right += 1
        rect.bottom += 1
    annotation_list = []
    for i in range(obj.annotations):
        annotation = obj.annotation(i)
        sublist = []
        if recursive and annotation.annotations:
            sublist = find_annotations(annotation,
                    handles=handles,
                    types=types,
                    rect=rect, half_open=half_open,
                    recursive=recursive)
        if (not rect or annotation.inside(rect)) and \
                (not types or annotation.type in types) and \
                (not handles or annotation.handle in handles):
            if sublist:
                sublist.insert(0, annotation)
                annotation_list.append(sublist)
            else:
                annotation_list.append(annotation)
        elif sublist:
            sublist.insert(0, None)
            annotation_list.append(sublist)
    return annotation_list


def inner_attribute_name(name):
    if name.startswith("%"):
        return name
    if "A" <= name[0] <= "Z":
        return "%" + name
    return "%" + "".join(map(lambda s: s.capitalize(), name.split("_")))


def outer_attribute_name(name):
    import string, re
    if not name.startswith("%"):
        return name
    return re.sub("([A-Z])", r"_\1", name[1:])[1:].lower()


def split_unit(unit):
    import re
    factor = re.match(r"(1/)?[\d.]*", unit).group(0)
    unit = unit[len(factor):]
    return (factor, unit)


def decode_fake_unicode(ustring):
    result = []
    for c in ustring:
        c = ord(c)
        if c < 256:
            result.append(c)
        else:
            result.append(c & 0xff)
            result.append(c >> 8)
    result = ''.join(map(chr, result))
    result = unicode(result, "mbcs")
    return result


class XDWAnnotation(XDWSubject, XDWObserver):

    """Annotation on DocuWorks document page"""

    @staticmethod
    def all_types():
        return XDW_ANNOTATION_TYPE

    @staticmethod
    def all_attributes():
        return [outer_attribute_name(k) for k in XDW_ANNOTATION_ATTRIBUTE]

    @staticmethod
    def initial_data(ann_type, **kw):
        ann_type = XDW_ANNOTATION_TYPE.normalize(ann_type)
        cls = XDW_AID_INITIAL_DATA.get(ann_type, None)
        if cls:
            init_dat = cls()
            init_dat.common.nAnnotationType = ann_type
        else:
            init_dat = NULL
        for k, v in kw.items():
            if k.startswith("n"):
                v = int(v)
            elif k.startswith("sz"):
                v = str(v)
            elif k.startswith("lpsz"):
                v = byref(v)
            elif k.startswith("p"):
                v = byref(v)
            setattr(init_dat, k, v)
        return init_dat

    @staticmethod
    def scale(attrname, value, store=False):
        unit = XDW_ANNOTATION_ATTRIBUTE[attrname][1]
        if unit:
            factor = split_unit(unit)[0]
            if factor:
                factor = 1 / float(factor[2:]) if factor.startswith("1/") \
                        else float(factor)
                value = value / factor if store else value * factor
        return int(value)

    def __init__(self, page, pos, parent=None, info=None):
        self.pos = pos
        XDWSubject.__init__(self)
        XDWObserver.__init__(self, page, EV_ANN_INSERTED)
        self.page = page
        self.parent = parent
        if not info:
            pah = parent.handle if parent else NULL
            info = XDW_GetAnnotationInformation(
                    page.xdw.handle, page.pos + 1, pah, pos + 1)
        self.handle = info.handle
        self.position = XDWPoint(info.nHorPos / 100.0, info.nVerPos / 100.0)  # mm
        self.size = XDWPoint(info.nWidth / 100.0, info.nHeight / 100.0)  # mm
        self.type = info.nAnnotationType
        self.annotations = info.nChildAnnotations
        self.is_unicode = False

    def __str__(self):
        return "XDWAnnotation(%s P%d: type=%s)" % (
                self.page.xdw.name,
                self.page.pos,
                XDW_ANNOTATION_TYPE[self.type])

    def __getattr__(self, name):
        attrname = inner_attribute_name(name)
        try:
            t, v, tt = XDW_GetAnnotationAttributeW(
                    self.handle, attrname, codepage=CP)
            if t == XDW_ATYPE_INT:
                v = XDWAnnotation.scale(attrname, v)
            if t == XDW_ATYPE_STRING:
                self.is_unicode = (tt == XDW_TEXT_UNICODE)
                if name == "font_name":
                    v = decode_fake_unicode(v)  # TODO: investigate...
            return v
        except XDWError as e:
            if e.error_code != XDW_E_INVALIDARG:
                raise
        return self.__dict__[name]

    def __setattr__(self, name, value):
        attrname = inner_attribute_name(name)
        if attrname == "position":
            XDW_SetAnnotationPosition(self.page.xdw.handle, self.handle,
                    int(value.x * 100), int(value.y * 100))
            self.position = value
        elif attrname == "size":
            XDW_SetAnnotationSize(self.page.xdw.handle, self.handle,
                    int(value.x * 100), int(value.y * 100))
            self.size = value
        elif attrname in XDW_ANNOTATION_ATTRIBUTE:
            if isinstance(value, basestring):
                texttype = XDW_TEXT_UNICODE if self.is_unicode \
                            else XDW_TEXT_MULTIBYTE
                if isinstance(value, str):
                    value = unicode(value, CODEPAGE)
                XDW_SetAnnotationAttributeW(
                        self.page.xdw.handle, self.handle,
                        attrname, XDW_ATYPE_STRING, value,
                        texttype, codepage=CP)
            else:
                value = c_int(XDWAnnotation.scale(attrname, value, store=True))
                XDW_SetAnnotationAttributeW(
                        self.page.xdw.handle, self.handle,
                        attrname, XDW_ATYPE_INT, byref(value), 0, 0)
            return
        # Other attributes, not saved in xdw files.
        self.__dict__[name] = value  # volatile

    def update(self, event):
        if not isinstance(event, XDWNotification):
            raise TypeError("not an instance of XDWNotification class")
        if event.type == EV_ANN_REMOVED:
            if event.para[0] < self.pos:
                self.pos -= 1
        elif event.type == EV_ANN_INSERTED:
            if event.para[0] < self.pos:
                self.pos += 1
        else:
            raise ValueError("Illegal event type: %d" % event.type)

    def typename(self):
        return XDW_ANNOTATION_TYPE[self.type]

    def attributes(self):
        return [outer_attribute_name(k) for (k, v)
                in XDW_ANNOTATION_ATTRIBUTE.items()
                if self.type in v[2]]

    def annotation(self, pos):
        """annotation(pos) --> XDWAnnotation"""
        if pos not in self.observers:
            self.observers[pos] = XDWAnnotation(self.page, pos, parent=self)
        return self.observers[pos]

    def inside(self, rect):  # Assume rect is half-open.
        if isinstance(rect, tuple):
            rect = XDWRect(rect.left, rect.top, rect.right, rect.bottom)
        return rect.left <= self.position.x <= rect.right - self.size.x and \
               rect.top <= self.position.y <= rect.bottom - self.size.y

    def find_annotations(self, *args, **kw):
        return find_annotations(self, *args, **kw)

    def add_annotation(self, ann_type, position, **kw):
        """Add an annotation.

        add_annotation(ann_type, position, **kw)
            position    XDWPoint; unit:mm
        """
        ann_type = XDW_ANNOTATION_TYPE.normalize(ann_type)
        if isinstance(position, (tuple, list)):
            position = XDWPoint(*position)
        init_dat = XDWAnnotation.initial_data(ann_type, **kw)
        ann_handle = XDW_AddAnnotationOnParentAnnotation(
                self.page.xdw.handle, self.handle, ann_type,
                int(position.x * 100), int(position.y * 100), init_dat)
        info = XDW_ANNOTATION_INFO()
        info.handle = ann_handle
        info.nHorPos = int(position.x * 100)
        info.nVerPos = int(position.y * 100)
        info.nWidth = 0
        info.nHeight = 0
        info.nAnnotationType = ann_type
        info.nChildAnnotations = 0
        pos = self.annotations  # TODO: Ensure this is correct.
        ann = XDWAnnotation(self, pos, parent=self, info=info)
        self.annotations += 1
        self.notify(event=XDWNotification(EV_ANN_INSERTED, pos))
        return ann

    def delete_annotation(self, pos):
        """Delete a child annotation given by pos."""
        ann = self.annotation(pos)
        XDW_RemoveAnnotation(self.page.xdw.handle, ann.handle)
        self.detach(ann, EV_ANN_REMOVED)
        self.annotations -= 1

    def content_text(self, recursive=True):
        if self.type == XDW_AID_TEXT:
            s = getattr(self, XDW_ATN_Text)
        elif self.type == XDW_AID_LINK:
            s = getattr(self, XDW_ATN_Caption)
        elif self.type == XDW_AID_STAMP:
            s = "%s <DATE> %s" % (
                    getattr(self, XDW_ATN_TopField),
                    getattr(self, XDW_ATN_BottomField))
        else:
            s = None
        if recursive and self.annotations:
            s = [s]
            s.extend([self.annotation(i).content_text(recursive=True) \
                    for i in range(self.annotations)])
            s = _join(ASEP, s)
        return s


class XDWPage(XDWSubject, XDWObserver):

    """Page of DocuWorks document"""

    @staticmethod
    def norm_res(n):
        if n <= 6:
            return (100, 200, 400, 200, 300, 400, 200)[n]
        return n

    def reset_attr(self):
        page_info = XDW_GetPageInformation(
                self.xdw.handle, self.pos + 1, extend=True)
        self.size = XDWPoint(page_info.nWidth / 100.0,
                             page_info.nHeight / 100.0)  # float, in mm
        # XDW_PGT_FROMIMAGE/FROMAPPL/NULL
        self.page_type = page_info.nPageType
        self.resolution = (XDWPage.norm_res(page_info.nHorRes),
                           XDWPage.norm_res(page_info.nVerRes))  # dpi
        self.compress_type = page_info.nCompressType
        self.annotations = page_info.nAnnotations
        self.degree = page_info.nDegree
        self.original_size = (page_info.nOrgWidth / 100.0,
                              page_info.nOrgHeight / 100.0)  # mm
        self.original_resolution = (
                XDWPage.norm_res(page_info.nOrgHorRes),
                XDWPage.norm_res(page_info.nOrgVerRes))  # dpi
        self.image_size = (page_info.nImageWidth,
                           page_info.nImageHeight)  # px

    def __init__(self, xdw, pos):
        self.pos = pos
        XDWSubject.__init__(self)
        XDWObserver.__init__(self, xdw, EV_PAGE_INSERTED)
        self.xdw = xdw
        self.reset_attr()

    def __str__(self):
        return "XDWPage(page %d: %.2f*%.2fmm, %s, %d annotations)" % (
                self.pos,
                self.width, self.height,
                XDW_PAGE_TYPE[self.page_type],
                self.annotations)

    def update(self, event):
        if not isinstance(event, XDWNotification):
            raise TypeError("not an instance of XDWNotification class")
        if event.type == EV_PAGE_REMOVED:
            if event.para[0] < self.pos:
                self.pos -= 1
        elif event.type == EV_PAGE_INSERTED:
            if event.para[0] < self.pos:
                self.pos += 1
        else:
            raise ValueError("illegal event type: %d" % event.type)

    def annotation(self, pos):
        """annotation(pos) --> XDWAnnotation"""
        if pos not in self.observers:
            self.observers[pos] = XDWAnnotation(self, pos)
        return self.observers[pos]

    def find_annotations(self, *args, **kw):
        return find_annotations(self, *args, **kw)

    def add_annotation(self, ann_type, position, **kw):
        """Add an annotation.

        add_annotation(ann_type, position, **kw)
            ann_type    annotation type
            position    XDWPoint; float, unit:mm
        """
        ann_type = XDW_ANNOTATION_TYPE.normalize(ann_type)
        if isinstance(position, (tuple, list)):
            position = XDWPoint(*position)
        init_dat = XDWAnnotation.initial_data(ann_type, **kw)
        ann_handle = XDW_AddAnnotation(self.xdw.handle,
                    ann_type, self.pos + 1,
                    int(position.x * 100), int(position.y * 100),
                    init_dat)
        info = XDW_ANNOTATION_INFO()
        info.handle = ann_handle
        info.nHorPos = int(position.x * 100)
        info.nVerPos = int(position.y * 100)
        info.nWidth = 0
        info.nHeight = 0
        info.nAnnotationType = ann_type
        info.nChildAnnotations = 0
        pos = self.annotations  # TODO: Ensure this is correct.
        ann = XDWAnnotation(self, pos, parent=None, info=info)
        self.annotations += 1
        self.notify(event=XDWNotification(EV_ANN_INSERTED, pos))
        return ann

    def delete_annotation(self, pos):
        """Delete an annotation given by pos.

        delete_annotation(pos)
        """
        ann = self.annotation(pos)
        XDW_RemoveAnnotation(self.xdw.handle, ann.handle)
        self.detach(ann, EV_ANN_REMOVED)
        self.annotations -= 1

    def content_text(self):
        return XDW_GetPageTextToMemoryW(self.xdw.handle, self.pos + 1)

    def annotation_text(self, recursive=True):
        return _join(ASEP, [
                a.content_text(recursive=recursive) for a
                        in self.find_annotations()])

    def fulltext(self):
        return  _join(ASEP, [self.content_text(), self.annotation_text()])

    def rotate(self, degree=0, auto=False):
        """Rotate a page.

        rotate(degree=0, auto=False)
            degree  90, 180 or 270
            auto    True/False
        """
        if auto:
            XDW_RotatePageAuto(self.xdw.handle, self.pos + 1)
            self.xdw.finalize = True
        else:
            XDW_RotatePage(self.xdw.handle, self.pos + 1, degree)
        self.reset_attr()

    def reduce_noise(self, level=XDW_REDUCENOISE_NORMAL):
        """Process a page by noise reduction engine.

        reduce_noise(self, level=XDW_REDUCENOISE_NORMAL)
            level   XDW_REDUCENOISE_NORMAL
                    XDW_REDUCENOISE_WEAK
                    XDW_REDUCENOISE_STRONG
        """
        level = XDW_OCR_NOISEREDUCTION.normalize(level)
        XDW_ReducePageNoise(self.handle, self.pos + 1, level)

    def ocr(self,
            engine=XDW_OCR_ENGINE_DEFAULT,
            strategy=XDW_OCR_ENGINE_LEVEL_SPEED,
            preprocessing=XDW_PRIORITY_SPEED,
            noise_reduction=XDW_REDUCENOISE_NONE,
            deskew=True,
            form=XDW_OCR_FORM_AUTO,
            column=XDW_OCR_COLUMN_AUTO,
            rects=None,
            language=XDW_OCR_LANGUAGE_AUTO,
            main_language=XDW_OCR_MIXEDRATE_BALANCED,
            use_ascii=True,
            insert_space=False,
            verbose=False,
            ):
        """Process a page by OCR engine."""
        opt = XDW_OCR_OPTION_V7()
        engine = XDW_OCR_ENGINE.normalize(engine)
        opt.nEngineLevel = XDW_OCR_STRATEGY.normalize(strategy)
        opt.nPriority = XDW_OCR_PREPROCESSING.normalize(preprocessing)
        opt.nNoiseReduction = XDW_OCR_NOISEREDUCTION.normalize(noise_reduction)
        opt.nAutoDeskew = bool(deskew)
        opt.nForm = XDW_OCR_FORM.normalize(form)
        opt.nColumn = XDW_OCR_COLUMN.normalize(column)
        opt.nLanguage = XDW_OCR_LANGUAGE.normalize(language)
        opt.nLanguageMixedRate = XDW_OCR_MAIN_LANGUAGE.normalize(main_language)
        opt.nHalfSizeChar = bool(use_ascii)
        opt.nInsertSpaceCharacter = bool(insert_space)
        opt.nDisplayProcess = bool(verbose)
        if rects:
            opt.nAreaNum = len(rects)
            rectlist = XDW_RECT() * len(rects)
            for r, rect in zip(rectlist, rects):
                r.left = rect.left
                r.top = rect.top
                r.right = rect.right
                r.bottom = rect.bottom
            opt.pAreaRects = byref(rectlist)
        else:
            opt.pAreaRects = NULL
        XDW_ApplyOcr(self.xdw.handle, self.pos + 1, engine, byref(opt))
        self.finalize = True


class XDWDocument(XDWSubject):

    """DocuWorks document"""

    @staticmethod
    def all_types():
        return XDW_DOCUMENT_TYPE

    @staticmethod
    def all_attributes():
        return [outer_attribute_name(k) for k in XDW_DOCUMENT_ATTRIBUTE_W]

    def register(self):
        VALID_DOCUMENT_HANDLES.append(self.handle)

    def free(self):
        VALID_DOCUMENT_HANDLES.remove(self.handle)

    def __init__(self, path, readonly=False, authenticate=True):
        XDWSubject.__init__(self)
        open_mode = XDW_OPEN_MODE_EX()
        if readonly:
            open_mode.nOption = XDW_OPEN_READONLY
        else:
            open_mode.nOption = XDW_OPEN_UPDATE
        if authenticate:
            open_mode.nAuthMode = XDW_AUTH_NODIALOGUE
        else:
            open_mode.nAuthMode = XDW_AUTH_NONE
        if isinstance(path, str):
            path = unicode(path, CODEPAGE)
        self.handle = XDW_OpenDocumentHandle(path, open_mode)
        self.register()
        self.name = splitext(basename(path))[0]
        # Set document properties.
        document_info = XDW_GetDocumentInformation(self.handle)
        self.pages = document_info.nPages
        self.version = document_info.nVersion - 3  # DocuWorks version
        self.original_data = document_info.nOriginalData
        self.type = document_info.nDocType
        self.editable = bool(document_info.nPermission & XDW_PERM_DOC_EDIT)
        self.annotatable = bool(document_info.nPermission & XDW_PERM_ANNO_EDIT)
        self.printable = bool(document_info.nPermission & XDW_PERM_PRINT)
        self.copyable = bool(document_info.nPermission & XDW_PERM_COPY)
        self.show_annotations = bool(document_info.nShowAnnotations)
        # Followings are effective only for binders.
        self.documents = document_info.nDocuments
        self.binder_color = document_info.nBinderColor
        self.binder_size = document_info.nBinderSize
        # Document attributes.
        self.attributes = XDW_GetDocumentAttributeNumber(self.handle)
        # Remember if this must be finalized.
        self.finalize = False

    def __str__(self):
        return "XDWDocument(%s: %d pages, %d files attached)" % (
                self.name, self.pages, self.documents)

    def __getattr__(self, name):
        name = unicode(name)
        attribute_name = inner_attribute_name(name)
        try:
            return XDW_GetDocumentAttributeByNameW(
                    self.handle, attribute_name, codepage=CP)[1]
        except XDWError as e:
            if e.error_code != XDW_E_INVALIDARG:
                raise
        return self.__dict__[name]

    def __setattr__(self, name, value):
        name = unicode(name)
        attribute_name = inner_attribute_name(name)
        if isinstance(value, basestring):
            attribute_type = XDW_ATYPE_STRING
        elif isinstance(value, bool):
            attribute_type = XDW_ATYPE_BOOL
        elif isinstance(value, datetime.datetime):
            attribute_type = XDW_ATYPE_DATE
            if not value.tzinfo:
                value = value.replace(tzinfo=DEFAULT_TZ)  # TODO: Care locale.
            value = unixtime(value)
        else:
            attribute_type = XDW_ATYPE_INT  # TODO: Scaling may be required.
        # TODO: XDW_ATYPE_OTHER should also be valid.
        if attribute_name in XDW_DOCUMENT_ATTRIBUTE_W:
            XDW_SetDocumentAttributeW(
                    self.handle, attribute_name, attribute_type, value,
                    XDW_TEXT_MULTIBYTE, codepage=CP)
            return
        self.__dict__[name] = value

    def __len__(self):
        return self.pages

    def __iter__(self):
        self.current_pos = 0
        return self

    def next(self):
        if self.pages <= self.current_pos:
            raise StopIteration
        pos = self.current_pos
        self.current_pos += 1
        return self.page(pos)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def typename(self):
        return XDW_DOCUMENT_TYPE[self.type]

    def save(self):
        """Save document regardless of whether it is modified or not."""
        XDW_SaveDocument(self.handle)

    def close(self):
        """Finalize document if neccesary, and close document."""
        if self.finalize:
            XDW_Finalize(self.handle)
        XDW_CloseDocumentHandle(self.handle)
        self.free()

    def is_document(self):
        """Always True."""
        return True

    def is_binder(self):
        """Always False."""
        return False

    def page(self, pos):
        """page(pos) --> XDWPage"""
        if pos not in self.observers:
            self.observers[pos] = XDWPage(self, pos)
        return self.observers[pos]

    def add_page(self, *args):
        raise NotImplementedError()

    def delete_page(self, pos):
        """Delete a page given by pos.

        delete_page(pos)
        """
        page = self.page(pos)
        XDW_DeletePage(self.handle, page.pos + 1)
        self.detach(page, EV_PAGE_REMOVED)
        self.pages -= 1

    def content_text(self):
        return _join(PSEP, [page.content_text() for page in self])

    def annotation_text(self):
        return _join(PSEP, [page.annotation_text() for page in self])

    def fulltext(self):
        return _join(PSEP, [
                _join(ASEP, [page.content_text(), page.annotation_text()])
                for page in self])


class XDWDocumentInBinder(XDWSubject, XDWObserver):

    """Document part of DocuWorks binder"""

    def __init__(self, binder, pos):
        self.pos = pos
        XDWSubject.__init__(self)
        XDWObserver.__init__(self, binder, EV_DOC_INSERTED)
        self.binder = binder
        self.page_offset = sum(binder.document_pages[:pos])
        self.name = XDW_GetDocumentNameInBinderW(
                self.binder.handle, pos + 1, codepage=CP)[0]
        document_info = XDW_GetDocumentInformationInBinder(
                self.binder.handle, pos + 1)
        self.pages = document_info.nPages
        self.original_data = document_info.nOriginalData

    def __str__(self):
        return "XDWDocumentInBinder(" \
                "%s = %s[%d]: %d pages, %d attachments)" % (
                self.name,
                self.binder.name, self.pos,
                self.pages,
                self.original_data,
                )

    def __len__(self):
        return self.pages

    def __iter__(self):
        self.current_pos = 0
        return self

    def next(self):
        if self.pages <= self.current_pos:
            raise StopIteration
        pos = self.page_offset + self.current_pos
        self.current_pos += 1
        return self.binder.page(pos)

    def update(self, event):
        if not isinstance(event, XDWNotification):
            raise TypeError("not an instance of XDWNotification class")
        if event.type == EV_PAGE_REMOVED and event.para[0] < self.page_offset:
                self.page_offset -= 1
        if event.type == EV_PAGE_INSERTED and event.para[0] < self.page_offset:
                self.page_offset += 1
        else:
            raise ValueError("illegal event type")

    def is_document(self):
        """Always False."""
        return False

    def is_binder(self):
        """Always False."""
        return False

    def page(self, pos):
        """page(pos) --> XDWPage"""
        if page in self.observers:
            return self.observers[pos]
        self.observers[pos] = XDWPage(self.binder, self.page_offset + pos)

    def delete_page(self, pos):
        """Delete a page given by pos.

        delete_page(pos)
        """
        page = self.page(pos)
        XDW_DeletePage(self.binder.handle, page.pos)
        self.detach(page, EV_PAGE_REMOVED)
        self.binder.notify(XDWNotification(EV_PAGE_REMOVED, page.pos))
        # TODO: avoid duplicate notification and self-position-shift.
        self.pages -= 1

    def update(self, event):
        if not isinstance(event, XDWNotification):
            raise TypeError("not an instance of XDWNotification class")
        if event.type == EV_PAGE_REMOVED:
            if event.para[0] < self.page_offset:
                self.page_offset -= 1
        if event.type == EV_PAGE_INSERTED:
            if event.para[0] < self.page_offset:
                self.page_offset += 1
        else:
            raise ValueError("illegal event type: %d" % event.type)

    def add_page(self, *args):
        raise NotImplementedError()

    def content_text(self):
        return _join(PSEP, [page.content_text() for page in self])

    def annotation_text(self):
        return _join(PSEP, [page.annotation_text() for page in self])

    def fulltext(self):
        return _join(PSEP, [
                _join(ASEP, [page.content_text(), page.annotation_text()])
                for page in self])


class XDWBinder(XDWDocument):

    """A DocuWorks Binder"""

    def __init__(self, path, readonly=False, authenticate=True):
        XDWDocument.__init__(self,
                path=path, readonly=readonly, authenticate=authenticate)
        assert self.type == XDW_DT_BINDER
        self.document_pages = self.document_pages()

    def __str__(self):
        return "XDWBinder(%s: %d documents, %d pages, %d attachments)" % (
                self.name,
                self.documents,
                self.pages,
                self.original_data,
                )

    def __len__(self):
        return self.documents

    def __iter__(self):
        self.current_pos = 0
        return self

    def next(self):
        if self.documents <= self.current_pos:
            raise StopIteration
        pos = self.current_pos
        self.current_pos += 1
        return self.document(pos)

    def is_document(self):
        """Always False."""
        return False

    def is_binder(self):
        """Always True."""
        return True

    def document(self, pos):
        """document(pos) --> XDWDocumentInBinder"""
        if pos not in self.observers:
            self.observers[pos] = XDWDocumentInBinder(self, pos)
        return self.observers[pos]

    def document_and_page(self, pos):
        """document_and_page(pos) --> (XDWDocumentInBinder, XDWPage)"""
        if self.pages <= pos:
            raise IndexError("page %d exceeds total pages of binder" % pos)
        acc = 0
        for docnum, pages in enumerate(self.document_pages()):
            acc += pages
            if pos < acc:
                doc = self.document(docnum)
                page = doc.page(pos - (acc - pages))
                return (doc, page)

    def page(self, pos):
        """page(pos) --> XDWPage"""
        return self.document_and_page(self, pos)[1]

    def document_pages(self):
        """Get list of page count for each document in binder. """
        pages = []
        for pos in range(self.documents):
            docinfo = XDW_GetDocumentInformationInBinder(
                    self.handle, pos + 1)
            pages.append(docinfo.nPages)
        return pages

    def delete_document(self, pos):
        """Delete a document in binder given by pos.

        delete_document(pos)
        """
        doc = self.document(pos)
        XDW_DeleteDocumentInBinder(self.handle, doc.pos + 1)
        self.detach(doc, EV_DOC_REMOVED)
        self.documents -= 1

    def content_text(self):
        return _join(PSEP, [doc.content_text() for doc in self])

    def annotation_text(self):
        return _join(PSEP, [doc.annotation_text() for doc in self])

    def fulltext(self):
        return _join(PSEP, [
                _join(ASEP, [doc.content_text(), doc.annotation_text()])
                for doc in self])
