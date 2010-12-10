#!/usr/bin/env python
#vim:fileencoding=cp932:fileformat=dos

"""page.py -- DocuWorks library for Python.

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

from common import *
from annotation import Annotation


__all__ = ("Page",)


class Page(Subject, Observer):

    """Page of DocuWorks document"""

    @staticmethod
    def norm_res(n):
        if n <= 6:
            return (100, 200, 400, 200, 300, 400, 200)[n]
        return n

    def reset_attr(self):
        page_info = XDW_GetPageInformation(self.xdw.handle, self.pos + 1,
                                           extend=True)
        self.size = Point(page_info.nWidth / 100.0,
                          page_info.nHeight / 100.0)  # float, in mm
        # XDW_PGT_FROMIMAGE/FROMAPPL/NULL
        self.page_type = page_info.nPageType
        self.resolution = (Page.norm_res(page_info.nHorRes),
                           Page.norm_res(page_info.nVerRes))  # dpi
        self.compress_type = page_info.nCompressType
        self.annotations = page_info.nAnnotations
        self.degree = page_info.nDegree
        self.original_size = (page_info.nOrgWidth / 100.0,
                              page_info.nOrgHeight / 100.0)  # mm
        self.original_resolution = (
                Page.norm_res(page_info.nOrgHorRes),
                Page.norm_res(page_info.nOrgVerRes))  # dpi
        self.image_size = (page_info.nImageWidth,
                           page_info.nImageHeight)  # px

    def __init__(self, xdw, pos):
        self.pos = pos
        Subject.__init__(self)
        Observer.__init__(self, xdw, EV_PAGE_INSERTED)
        self.xdw = xdw
        self.reset_attr()

    def __str__(self):
        return "Page(page %d: %.2f*%.2fmm, %s, %d annotations)" % (
                self.pos,
                self.width, self.height,
                XDW_PAGE_TYPE[self.page_type],
                self.annotations)

    def update(self, event):
        if not isinstance(event, Notification):
            raise TypeError("not an instance of Notification class")
        if event.type == EV_PAGE_REMOVED:
            if event.para[0] < self.pos:
                self.pos -= 1
        elif event.type == EV_PAGE_INSERTED:
            if event.para[0] < self.pos:
                self.pos += 1
        else:
            raise ValueError("illegal event type: %d" % event.type)

    def annotation(self, pos):
        """annotation(pos) --> Annotation"""
        if pos not in self.observers:
            self.observers[pos] = Annotation(self, pos)
        return self.observers[pos]

    def find_annotations(self, *args, **kw):
        return find_annotations(self, *args, **kw)

    def add_annotation(self, ann_type, position, **kw):
        """Add an annotation.

        add_annotation(ann_type, position, **kw)
            ann_type    annotation type
            position    Point; float, unit:mm
        """
        ann_type = XDW_ANNOTATION_TYPE.normalize(ann_type)
        if isinstance(position, (tuple, list)):
            position = Point(*position)
        init_dat = Annotation.initial_data(ann_type, **kw)
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
        ann = Annotation(self, pos, parent=None, info=info)
        self.annotations += 1
        self.notify(event=Notification(EV_ANN_INSERTED, pos))
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
        return joinf(ASEP, [
                a.content_text(recursive=recursive) for a
                        in self.find_annotations()])

    def fulltext(self):
        return  joinf(ASEP, [self.content_text(), self.annotation_text()])

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
        self.xdw.finalize = True
