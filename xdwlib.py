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
import time
import datetime

from xdwapi import *

__all__ = (
    "XDWDocument", "XDWDocumentInBinder", "XDWBinder", "XDWError",
    "environ", "xdwopen", "create", "create_binder",
    "PSEP", "ASEP",
    )

CP = 932
CODEPAGE = "cp%d" % CP
PSEP = "\f"
ASEP = "\v"


# Timezone support

class JST(datetime.tzinfo):

    """JST"""

    def utcoffset(self, dt=None):
        return datetime.timedelta(hours=9)

    def dst(self, dt=None):
        return datetime.timedelta(0)

    def tzname(self, dt=None):
        return "JST"


class UTC(datetime.tzinfo):

    """UTC"""

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "UTC"


TZ_JST = JST()
TZ_UTC = UTC()
DEFAULT_TZ = TZ_JST


def unixtime(dt, utc=False):
    if utc:
        return time.mktime(dt.utctimetuple())
    return time.mktime(dt.timetuple())


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


def annotation_in(annotation, rect):  # Assume rect is half-open.
    return (rect.left <= annotation.horizontal_position \
                     <= rect.right - annotation.width \
            and \
            rect.top <= annotation.vertical_position \
                     <= rect.bottom - annotation.height)


def find_annotations(obj, handles=None, types=None, rect=None,
        half_open=True, recursive=False):
    if not (isinstance(handles, tuple) or isinstance(handles, list)):
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
        if (not rect or annotation_in(annotation, rect)) and \
                (not types or annotation.annotation_type in types) or \
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


def scale_annotation_value(attr_name, value, store=False):
    if attr_name in (XDW_ATN_FontSize, XDW_ATN_TextSpacing):
        return int(value * 10) if store else value / 10.0
    elif attr_name in (XDW_ATN_LineSpace,
            XDW_ATN_TextTopMargin, XDW_ATN_TextLeftMargin,
            XDW_ATN_TextBottomMargin, XDW_ATN_TextRightMargin):
        return int(value * 100) if store else value / 100.0
    return value


class XDWSubject(object):

    def __init__(self):
        self.observers = dict()

    def shift_keys(self, border, delete=False):
        for pos in sorted(filter(lambda p: border < p, self.observers.keys()),
                reverse=(not delete)):
            self.observers[pos + (-1 if delete else 1)] = self.observers[pos]
            del self.observers[pos]

    def attach(self, observer, event):
        self.shift_keys(observer.pos)
        self.observers[observer.pos] = observer
        self.notify(event=XDWNotification(event, observer.pos))

    def detach(self, observer, event=None):
        del self.observers[observer.pos]
        self.shift_keys(observer.pos, delete=True)
        self.notify(event=XDWNotification(event, observer.pos))

    def notify(self, event=None):
        for pos in self.observers:
            self.observers[pos].update(event)


class XDWObserver(object):

    def __init__(self, subject, event):
        subject.attach(self, event)

    def update(self, event):
        raise NotImplementedError  # Override it.


class XDWNotification(object):

    def __init__(self, type, *para):
        self.type = type
        self.para = para


class XDWAnnotation(XDWSubject, XDWObserver):

    """Annotation on DocuWorks document page"""

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

    def __init__(self, page, index, parent=None, handle=None):
        self.pos = index
        XDWSubject.__init__(self)
        XDWObserver.__init__(self, page, EV_ANN_INSERTED)
        self.page = page
        self.parent = parent
        pah = parent and parent.handle or NULL
        info = XDW_GetAnnotationInformation(
                page.xdw.handle, page.pos + 1, pah, index + 1)
        self.handle = info.handle
        self.horizontal_position = info.nHorPos / 100.0  # mm
        self.vertical_position = info.nVerPos / 100.0  # mm
        self.width = info.nWidth / 100.0  # mm
        self.height = info.nHeight / 100.0  # mm
        self.annotation_type = info.nAnnotationType
        self.annotations = info.nChildAnnotations
        self.is_unicode = False

    def __str__(self):
        return "XDWAnnotation(%s P%d: type=%s)" % (
                self.page.xdw.name,
                self.page.pos,
                XDW_ANNOTATION_TYPE[self.annotation_type],
                )

    def __getattr__(self, name):
        attr_name = inner_attribute_name(name)
        t, v, tt = XDW_GetAnnotationAttributeW(
                self.handle, attr_name, codepage=CP)
        v = scale_annotation_value(attr_name, v)
        if t == XDW_ATYPE_STRING:
            self.is_unicode = (tt == XDW_TEXT_UNICODE)
        return v

    def __setattr__(self, name, value):
        attr_name = inner_attribute_name(name)
        if attr_name in XDW_ANNOTATION_ATTRIBUTE:
            if isinstance(value, basestring):
                texttype = XDW_TEXT_UNICODE if self.is_unicode \
                            else XDW_TEXT_MULTIBYTE
                if isinstance(value, str):
                    value = unicode(value, CODEPAGE)
                XDW_SetAnnotationAttributeW(
                        self.page.xdw.handle, self.handle,
                        attr_name, XDW_ATYPE_STRING, value,
                        texttype, codepage=CP)
            else:
                value = c_int(
                        scale_attribute_value(attr_name, value, store=True))
                XDW_SetAnnotationAttributeW(
                        self.page.xdw.handle, self.handle,
                        attr_name, XDW_ATYPE_INT, byref(value), 0, 0)
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

    def annotation(self, index):
        """annotation(index) --> XDWAnnotation"""
        if index not in self.observers:
            self.observers[index] = XDWAnnotation(self.page, index, parent=self)
        return self.observers[index]

    def find_annotations(self, *args, **kw):
        """Find annotations on page, which meets criteria given.

        find_annotations(object, handles=None, types=None, rect=None, half_open=True, recursive=False)
            handles     return annotations that has given annotation handles.
            types       return annotations of types given.  None means all.
            rect        return annotations in given rectangular area,
                        (rect.left, rect.top) - (rect.right, rect.bottom).
                        Note that right/bottom value are innermost of outside
                        unless half_open==False.  None means all.
            recursive   also return descendant (child) annotations.
        """
        return find_annotations(self, *args, **kw)

    def add_annotation(self, ann_type, hpos, vpos, **kw):
        """Add an annotation.

        add_annotation(ann_type, hpos, vpos, **kw)
            hpos    horizontal position (float, in mm)
            vpos    vertical position (float, in mm)
        """
        ann_type = XDW_ANNOTATION_TYPE.normalize(ann_type)
        init_dat = XDWAnnotation.initial_data(ann_type, **kw)
        ann_handle = XDW_AddAnnotationOnParentAnnotation(
                self.page.xdw.handle, self.handle, ann_type,
                int(hpos * 100), int(vpos * 100), init_dat)
        self.annotations += 1
        ann = find_annotations(self, handles=[ann_handle], parent=self)[0]
        # self.attach(ann, EV_ANN_INSERTED) is done automatically.
        return ann

    def delete_annotation(self, index):
        """Delete a child annotation given by index."""
        ann = self.annotation(index)
        XDW_RemoveAnnotation(self.page.xdw.handle, ann.handle)
        self.detach(ann, EV_ANN_REMOVED)
        self.annotations -= 1

    def content_text(self, recursive=True):
        if self.annotation_type == XDW_AID_TEXT:
            s = getattr(self, XDW_ATN_Text)
        elif self.annotation_type == XDW_AID_LINK:
            s = getattr(self, XDW_ATN_Caption)
        elif self.annotation_type == XDW_AID_STAMP:
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
    def normalize_resolution(n):
        if n <= 6:
            return (100, 200, 400, 200, 300, 400, 200)[n]
        return n

    def reset_attr(self):
        page_info = XDW_GetPageInformation(
                self.xdw.handle, self.pos + 1, extend=True)
        self.width = page_info.nWidth / 100.0  # float, in mm
        self.height = page_info.nHeight / 100.0  # float, in mm
        # XDW_PGT_FROMIMAGE/FROMAPPL/NULL
        self.page_type = page_info.nPageType
        self.horizontal_resolution = XDWPage.normalize_resolution(
                page_info.nHorRes)  # dpi
        self.vertical_resolution = XDWPage.normalize_resolution(
                page_info.nVerRes)  # dpi
        self.compress_type = page_info.nCompressType
        self.annotations = page_info.nAnnotations
        self.degree = page_info.nDegree
        self.original_width = page_info.nOrgWidth / 100.0  # float, in mm
        self.original_height = page_info.nOrgHeight / 100.0  # float, in mm
        self.original_horizontal_resolution = XDWPage.normalize_resolution(
                page_info.nOrgHorRes)  # dpi
        self.original_vertical_resolution = XDWPage.normalize_resolution(
                page_info.nOrgVerRes)  # dpi
        self.image_width = page_info.nImageWidth  # px
        self.image_height = page_info.nImageHeight  # px

    def __init__(self, xdw, page):
        self.pos = page
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

    def annotation(self, index):
        """annotation(n) --> XDWAnnotation"""
        if index not in self.observers:
            self.observers[index] = XDWAnnotation(self, index)
        return self.observers[index]

    def find_annotations(self, *args, **kw):
        return find_annotations(self, *args, **kw)

    def add_annotation(self, ann_type, hpos, vpos, **kw):
        """Add an annotation.

        add_annotation(ann_type, hpos, vpos, **kw)
            hpos    horizontal position (float, in mm)
            vpos    vertical position (float, in mm)
        """
        ann_type = XDW_ANNOTATION_TYPE.normalize(ann_type)
        init_dat = XDWAnnotation.initial_data(ann_type, **kw)
        ann_handle = XDW_AddAnnotation(self.xdw.handle,
                    ann_type, self.pos + 1,
                    int(hpos * 100), int(vpos * 100), init_dat)
        self.annotations += 1
        ann = find_annotations(self, handles=[ann_handle])[0]
        # self.attach(ann, EV_ANN_INSERTED) is done automatically.
        return ann

    def delete_annotation(self, index):
        """Delete an annotation given by index.

        delete_annotation(index)
        """
        ann = self.annotation(index)
        XDW_RemoveAnnotation(self.handle, ann.handle)
        self.detach(ann, EV_ANN_REMOVED)
        self.annotations -= 1

    def content_text(self):
        return XDW_GetPageTextToMemoryW(self.xdw.handle, self.pos + 1)

    def annotation_text(self, recursive=True):
        return _join(ASEP, [
                a.content_text(recursive=recursive) for a in self.find_annotations()])

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
                r.left = rect[0][0]
                r.top = rect[0][1]
                r.right = rect[1][0]
                r.bottom = rect[1][1]
            opt.pAreaRects = byref(rectlist)
        else:
            opt.pAreaRects = NULL
        XDW_ApplyOcr(self.xdw.handle, self.pos + 1, engine, byref(opt))
        self.finalize = True


class XDWDocument(XDWSubject):

    """DocuWorks document"""

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
        self.document_type = document_info.nDocType
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
        attribute_name = inner_attribute_name(name)
        try:
            return XDW_GetDocumentAttributeByNameW(
                    self.handle, attribute_name, codepage=CP)[1]
        except XDWError as e:
            if e.error_code == XDW_E_INVALIDARG:
                raise AttributeError("'%s' object has no attribute '%s'" % (
                        self.__class__.__name__, name))
            else:
                raise

    def __setattr__(self, name, value):
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
        if attribute_name in XDW_DOCUMENT_ATTRIBUTE:
            XDW_SetDocumentAttributeW(
                    self.handle, attribute_name, attribute_type, byref(value),
                    XDW_TEXT_MULTIBYTE, codepage=CP)
            return
        self.__dict__[name] = value

    def __len__(self):
        return self.pages

    def __iter__(self):
        self.current_page = 0
        return self

    def next(self):
        if self.pages <= self.current_page:
            raise StopIteration
        page = self.current_page
        self.current_page += 1
        return self.page(page)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

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

    def page(self, page):
        """page(page) --> XDWPage"""
        if page not in self.observers:
            self.observers[page] = XDWPage(self, page)
        return self.observers[page]

    def add_page(self, *args):
        raise NotImplementedError()

    def delete_page(self, page):
        """Delete a page given by page number.

        delete_page(page)
        """
        page = self.page(page)
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

    def __init__(self, binder, position):
        self.pos = position
        XDWSubject.__init__(self)
        XDWObserver.__init__(self, binder, EV_DOC_INSERTED)
        self.binder = binder
        self.page_offset = sum(binder.document_pages[:position])
        self.name = XDW_GetDocumentNameInBinderW(
                self.binder.handle, position + 1, codepage=CP)[0]
        document_info = XDW_GetDocumentInformationInBinder(
                self.binder.handle, position + 1)
        self.pages = document_info.nPages
        self.original_data = document_info.nOriginalData

    def __str__(self):
        return "XDWDocumentInBinder(" \
                "%s = %s[%d]: %d pages, %d attachments)" % (
                self.name,
                self.binder.name, self.position,
                self.position + 1,
                self.pages,
                self.original_data,
                )

    def __len__(self):
        return self.pages

    def __iter__(self):
        self.current_page = 0
        return self

    def next(self):
        if self.pages <= self.current_page:
            raise StopIteration
        page = self.page_offset + self.current_page
        self.current_page += 1
        return self.binder.page(page)

    def update(self, page):
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

    def page(self, page):
        """page(n) --> XDWPage"""
        if page in self.observers:
            return self.observers[page]
        self.observers[page] = XDWPage(self.binder, self.page_offset + page)

    def delete_page(self, page):
        """Delete a page given by page number.

        delete_page(page)
        """
        page = self.page(page)
        XDW_DeletePage(self.binder.handle, page.pos)
        self.detach(page, EV_PAGE_REMOVED)
        self.binder.notify(XDWNotification(EV_PAGE_REMOVED, page.pos))
        # TODO: avoid duplicate notification and self-position-shift.
        self.pages -= 1

    def update(self, page):
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
        assert self.document_type == XDW_DT_BINDER
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
        self.current_position = 0
        return self

    def next(self):
        if self.documents <= self.current_position:
            raise StopIteration
        position = self.current_position
        self.current_position += 1
        return self.document(position)

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

    def document_and_page(self, page):
        """document_and_page(page) --> (XDWDocumentInBinder, XDWPage)"""
        if self.pages <= page:
            raise IndexError("page %d exceeds total pages of binder" % page)
        acc = 0
        for pos, pages in enumerate(self.document_pages()):
            acc += pages
            if page < acc:
                doc = self.document(pos)
                page = doc.page(page - (acc - pages))
                return (doc, page)

    def page(self, page):
        """page(page) --> XDWPage"""
        return self.document_and_page(self, page)[1]

    def document_pages(self):
        """Get list of page count for each document in binder. """
        pages = []
        for position in range(self.documents):
            docinfo = XDW_GetDocumentInformationInBinder(
                    self.handle, position + 1)
            pages.append(docinfo.nPages)
        return pages

    def delete_document(self, pos):
        """Delete a document in binder given by position.

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
