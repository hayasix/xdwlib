#!/usr/bin/env python
# vim: fileencoding=cp932 fileformat=dos

"""xdwfile.py -- DocuWorks-compatible files

Copyright (C) 2010 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import os
import datetime
import shutil
import atexit

from .xdwapi import *
from .common import *
from .struct import Point
from .timezone import *
from .observer import Subject, Observer


__all__ = (
        "XDWFile", "PageForm", "AttachmentList", "Attachment",
        "StampSignature", "PKISignature",
        "xdwopen", "create_sfx", "extract_sfx", "optimize", "copy",
        "protection_info", "protect", "unprotect", "sign",
        "VALID_DOCUMENT_HANDLES", "close_all",
        )


# The last resort to close documents in interactive session.
try:
    VALID_DOCUMENT_HANDLES
except NameError:
    VALID_DOCUMENT_HANDLES = []


@atexit.register
def atexithandler():
    """Close all files and perform finalization before finishing process."""
    try:
        for handle in VALID_DOCUMENT_HANDLES:
            try:
                XDW_CloseDocumentHandle(handle)
            except:
                continue
            VALID_DOCUMENT_HANDLES.remove(handle)
        XDW_Finalize()
    except Exception as e:
        sys.stderr.write("{0}:xdwlib:error on exit:{1}\n""".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), e))


def xdwopen(path, readonly=False, authenticate=True, autosave=False):
    """General opener.

    Returns Document or Binder object.
    """
    from document import Document
    from binder import Binder
    path = uc(path)
    XDW_TYPES = {".XDW": Document, ".XBD": Binder}
    ext = os.path.splitext(path)[1].upper()
    if ext not in XDW_TYPES:
        raise BadFormatError("extension must be .xdw or .xbd")
    doc = XDW_TYPES[ext](path)
    doc.open(readonly=readonly, authenticate=authenticate, autosave=autosave)
    return doc


def create_sfx(input_path, output_path=None):
    """Create self-extract executable file.

    Returns pathname of generated sfx executable file.
    """
    input_path = adjust_path(uc(input_path))
    root, ext = os.path.splitext(input_path)
    output_path = adjust_path(uc(output_path or root), ext=".exe")
    output_path = derivative_path(output_path)
    XDW_CreateSfxDocument(cp(input_path), cp(output_path))
    return output_path


def extract_sfx(input_path, output_path=None):
    """Extract DocuWorks document/binder from self-extract executable file.

    Returns pathname of generated document/binder file.
    """
    input_path = adjust_path(uc(input_path))
    root, ext = os.path.splitext(input_path)
    output_path = adjust_path(uc(output_path or root), ext=".xdw")
    output_path = derivative_path(output_path)
    XDW_ExtractFromSfxDocument(cp(input_path), cp(output_path))
    # Created file can be either document or binder.  We have to examine
    # which type of file was generated and rename if needed.
    doc = xdwopen(output_path, readonly=True)
    doctype = doc.type
    doc.close()
    if doctype == XDW_DT_DOCUMENT:
        return output_path
    # Binder
    binder_path = derivative_path(os.path.splitext(output_path)[0] + ".xbd")
    os.rename(output_path, binder_path)
    return binder_path


def optimize(input_path, output_path=None):
    """Optimize document/binder file.

    Returns pathname of optimized document/binder file.
    """
    input_path = adjust_path(uc(input_path))
    root, ext = os.path.splitext(input_path)
    output_path = adjust_path(uc(output_path or root), ext=ext)
    output_path = derivative_path(output_path)
    XDW_OptimizeDocument(cp(input_path), cp(output_path))
    return output_path


def copy(input_path, output_path=None):
    """Copy DocuWorks document/binder to another one.

    Returns pathname of copied file.
    """
    input_path = adjust_path(uc(input_path))
    root, ext = os.path.splitext(input_path)
    output_path = adjust_path(uc(output_path or root), ext=ext)
    output_path = derivative_path(output_path)
    shutil.copyfile(input_path, output_path)
    return output_path


def protection_info(path):
    """Get protection information on a document/binder.

    Returns (protect_type, permission) where:
    protect_type    "PASSWORD" | "PASSWORD128" | "PKI" | "STAMP" |
                    "CONTEXT_SERVICE"
    permission      allowed operation(s); comma separated list of
                    "EDIT_DOCUMENT", "EDIT_ANNOTATION", "PRINT" and "COPY"
    """
    path = adjust_path(uc(path))
    info = XDW_GetProtectionInformation(cp(path))
    protect_type = XDW_PROTECT[info.nProtectType]
    permission = flagvalue(XDW_PERM, info.nPermission, store=False)
    return (protect_type, permission)


def protect(input_path,
        output_path=None,
        protect_type="PASSWORD",
        auth="NONE",
        **options):
    """Generate protected document/binder.

    protect_type    "PASSWORD" | "PASSWORD128" | "PKI"
    auth            "NONE" | "NODIALOGUE" | "CONDITIONAL"

    **options for PASSWORD and PASSWORD128:
    permission      allowed operation(s); comma separated list of
                    "EDIT_DOCUMENT", "EDIT_ANNOTATION", "PRINT" and "COPY"
    password        password to open document/binder, or None
    fullaccess      password to open document/binder with full-access
                    privilege, or None
    comment         notice in password dialogue, or None

    **options for PKI:
    permission      allowed operation(s); comma separated list of
                    "EDIT_DOCUMENT", "EDIT_ANNOTATION", "PRINT" and "COPY"
    certificates    list of certificates in DER (RFC3280) formatted str
    fullaccesscerts list of certificates in DER (RFC3280) formatted str

    Returns pathname of protected file.
    """
    input_path = adjust_path(uc(input_path))
    root, ext = os.path.splitext(input_path)
    output_path = adjust_path(uc(output_path or root), ext=ext)
    output_path = derivative_path(output_path)
    protect_option = XDW_PROTECT_OPTION()
    protect_option.nAuthMode = XDW_AUTH.normalize(auth)
    protect_type = XDW_PROTECT.normalize(protect_type)
    o = lambda s: options.get(s)
    if protect_type in (XDW_PROTECT_PSWD, XDW_PROTECT_PSWD128):
        opt = XDW_SECURITY_OPTION_PSWD()
        opt.nPermission = flagvalue(XDW_PERM, o("permission"), store=True)
        opt.szOpenPswd = o("password") or ""
        opt.szFullAccessPswd = o("fullaccess") or ""
        opt.lpszComment = o("comment") or ""
    elif protect_type == XDW_PROTECT_PKI:
        opt = XDW_SECURITY_OPTION_PKI()
        opt.nPermission = flagvalue(XDW_PERM, o("permission"), store=True)
        certificates = o("certificates")
        if not certificates:
            raise ValueError("a list of certificate(s) is required")
        fullaccesscerts = o("fullacccesscerts")
        opt.nCertsNum = len(certificates) + len(fullaccesscerts)
        opt.nFullAccessCertsNum = len(fullaccesscerts)
        certs = fullaccesscerts + certificates
        ders = XDW_DER_CERTIFICATE() * opt.nCertsNum
        for i in range(opt.nCertsNum):
            ders[i].pCert = pointer(certs[i])
            ders[i].nCertSize = len(certs[i])
        opt.lpxdcCerts = byref(ders)
    elif protect_type in (XDW_PROTECT_STAMP, XDW_PROTECT_CONTEXT_SERVICE):
        raise NotImplementedError(
                "only password- or PKI-based protection is available")
    else:
        raise ValueError("protect_type must be PASSWORD, PASSWORD128 or PKI")
    try:
        XDW_ProtectDocument(cp(input_path), cp(output_path),
                protect_type, opt, protect_option)
    except ProtectModuleError as e:
        msg = XDW_SECURITY_PKI_ERROR[opt.nErrorStatus]
        if 0 <= opt.nFirstErrorCert:
            msg += " in cert[%d]" % opt.nFirstErrorCert
        raise ProtectModuleError(msg)
    return output_path


def unprotect(input_path, output_path=None, auth="NONE"):
    """Release protection on document/binder.

    auth            "NODIALOGUE" | "CONDITIONAL"

    Returns pathname of unprotected file.

    NB. Only PKI-based or DocuWorks-builtin-stamp-based protected files are
        processed.  Password-based protected files are beyond xdwlib.
    """
    input_path = adjust_path(uc(input_path))
    root, ext = os.path.splitext(input_path)
    output_path = adjust_path(uc(output_path or root), ext=ext)
    output_path = derivative_path(output_path)
    if protection_info(input_path)[0] not in ("PKI", "STAMP"):
        raise ValueError("only PKI- or STAMP-protected file is acceptable")
    auth = XDW_AUTH.normalize(auth)
    if auth not in (XDW_AUTH_NODIALOGUE, XDW_AUTH_CONDITIONAL_DIALOGUE):
        raise ValueError("auth must be NODIALOGUE or CONDITIONAL")
    opt = XDW_RELEASE_PROTECTION_OPTION()
    opt.nAuthMode = auth
    XDW_ReleaseProtectionOfDocument(cp(input_path), cp(output_path), opt)
    return output_path


def sign(input_path,
        output_path=None,
        page=0,
        position=None,
        type_="STAMP",
        certificate=None):
    """Sign i.e. place a signature on document/binder page.

    page            page number to paste signature on; starts with 0
    position        (Point) position to paste signature on; default=(0, 0)
    type_           "STAMP" | "PKI"
    certificate     certificate in DER (RFC3280) formatted str; valid for PKI

    Returns pathname of signed file.
    """
    input_path = adjust_path(uc(input_path))
    root, ext = os.path.splitext(input_path)
    output_path = adjust_path(uc(output_path or root), ext=ext)
    output_path = derivative_path(output_path)
    opt = XDW_SIGNATURE_OPTION_V5()
    opt.nPage = page + 1
    opt.nHorPos, opt.nVerPos = ((position or Point(0, 0)) * 100).int()
    opt.nSignatureType = XDW_SIGNATURE.normalize(type_)
    type_ = XDW_SIGNATURE.normalize(type_)
    if type_ == XDW_SIGNATURE_STAMP:
        modopt = None
    else:  # type_ == XDW_SIGNATURE_PKI
        modopt = XDW_SIGNATURE_MODULE_OPTION_PKI()
        modopt.pSignerCert = ptr(cert)
        modopt.nSignerCertSize = len(cert)
    XDW_SignDocument(cp(input_path), cp(output_path), opt, modopt)
    return output_path


class AttachmentList(Subject):

    """Collection of Attachments aka original data."""

    def __init__(self, doc, size=None):
        Subject.__init__(self)
        self.doc = doc
        if size:
            self.size = size
        else:
            docinfo = XDW_GetDocumentInformation(doc.handle)
            self.size = docinfo.nOriginalData

    def __len__(self):
        return self.size

    def __iter__(self):
        for pos in range(self.size):
            yield self.attachment(pos)

    def _pos(self, pos, append=False):
        append = 1 if append else 0
        if not (-self.size <= pos < self.size + append):
            raise IndexError("Attachment #{0} not in [{1}, {2})".format(
                    pos, -self.size, self.size + append))
        if pos < 0:
            pos += self.size
        return pos

    def attachment(self, pos):
        """Get an attachment, aka original data."""
        pos = self._pos(pos)
        if pos not in self.observers:
            self.observers[pos] = Attachment(self.doc, pos)
        return self.observers[pos]

    def __getitem__(self, pos):
        return self.attachment(pos)

    def append(self, path):
        """Append an attachment, aka original data, at the end of XDW/XBD."""
        return self.insert(self.size, path)

    def insert(self, pos, path):
        """Insert an attachment, aka original data.

        pos     position to insert; starts with 0
        path    pathname of a file to insert
        """
        pos = self._pos(pos, append=True)
        XDW_InsertOriginalData(self.doc.handle, pos + 1, path)
        self.size += 1
        att = self.attachment(pos)
        self.attach(att, EV_ATT_INSERTED)

    def delete(self, pos):
        """Remove an attachment, aka original data."""
        pos = self._pos(pos)
        att = self.attachment(pos)
        XDW_DeleteOriginalData(self.doc.handle, pos + 1)
        self.detach(att, EV_ATT_REMOVED)
        self.size -= 1

    def __delitem__(self, pos):
        self.delete(pos)


class Attachment(Observer):

    """Place holder for attachments aka original data."""

    def __init__(self, doc, pos):
        self.doc = doc
        self.pos = pos
        info, text_type = XDW_GetOriginalDataInformationW(
                doc.handle, pos + 1, codepage=CP)
        self.text_type = XDW_TEXT_TYPE[text_type]
        self.size = info.nDataSize
        self.datetime = fromunixtime(info.nDate)
        self.name = info.szName

    def update(self, event):
        """Update self as an observer."""
        if not isinstance(event, Notification):
            raise TypeError("not an instance of Notification class")
        if event.type == EV_ATT_REMOVED:
            if event.para[0] < self.pos:
                self.pos -= 1
        elif event.type == EV_ATT_INSERTED:
            if event.para[0] < self.pos:
                self.pos += 1
        else:
            raise ValueError("Illegal event type: {0}".format(event.type))

    def save(self, path=None):
        """Save attached file.

        Returns pathname actually saved.
        """
        path = derivative_path(path or self.name)
        XDW_GetOriginalData(self.doc.handle, self.pos + 1, path)
        return path


class XDWFile(object):

    """Docuworks file, XDW or XBD."""

    @staticmethod
    def all_attributes():  # for debugging
        return [outer_attribute_name(k) for k in XDW_DOCUMENT_ATTRIBUTE_W]

    def register(self):
        VALID_DOCUMENT_HANDLES.append(self.handle)

    def free(self):
        VALID_DOCUMENT_HANDLES.remove(self.handle)

    @staticmethod
    def _free(handle):
        VALID_DOCUMENT_HANDLES.remove(handle)

    def __init__(self, path):
        """Initiator.

        Sets the following properties:
            dir         (unicode) directory part of path
            name        (unicode) filename without extension
            type        (str) "DOCUMENT" | "BINDER"
            protection  result of protection_info(path)

        NB. value of `type' may be changed after actual open().
        """
        self.signatures = None  # hack
        self.dir, self.name = os.path.split(uc(path))
        self.name, ext = os.path.splitext(self.name)
        self.type = {".xdw": "DOCUMENT", ".xbd": "BINDER"}.get(
                ext.lower(), "DOCUMENT")
        self.protection = protection_info(path)
        self.handle = None

    def open(self, readonly=False, authenticate=True, autosave=False):
        """Opener."""
        self._autosave = bool(autosave)
        open_mode = XDW_OPEN_MODE_EX()
        if readonly:
            open_mode.nOption = XDW_OPEN_READONLY
        else:
            open_mode.nOption = XDW_OPEN_UPDATE
        if authenticate:
            open_mode.nAuthMode = XDW_AUTH_NODIALOGUE
        else:
            open_mode.nAuthMode = XDW_AUTH_NONE
        self.handle = XDW_OpenDocumentHandle(cp(self.pathname()), open_mode)
        self.register()
        # Set document properties.
        docinfo = XDW_GetDocumentInformation(self.handle)
        self.pages = docinfo.nPages
        self.version = docinfo.nVersion - 3  # DocuWorks version
        self.attachments = AttachmentList(self, size=docinfo.nOriginalData)
        self.type = XDW_DOCUMENT_TYPE[docinfo.nDocType]
        self.editable = bool(docinfo.nPermission & XDW_PERM_DOC_EDIT)
        self.annotatable = bool(docinfo.nPermission & XDW_PERM_ANNO_EDIT)
        self.printable = bool(docinfo.nPermission & XDW_PERM_PRINT)
        self.copyable = bool(docinfo.nPermission & XDW_PERM_COPY)
        self._show_annotations = bool(docinfo.nShowAnnotations)
        # Followings are effective only for binders.
        self.documents = docinfo.nDocuments
        self.binder_color = XDW_BINDER_COLOR[docinfo.nBinderColor]
        self.binder_size = XDW_BINDER_SIZE[docinfo.nBinderSize]
        # Document attributes.
        self._set_property_count()
        # Attached signatures.
        self._set_signature_count()
        # Document verification status.
        self.status = None
        # Remember arguments for future use.
        self.readonly = readonly
        self.authenticate = authenticate
        return self

    def _set_property_count(self):
        self.properties = XDW_GetDocumentAttributeNumber(self.handle)

    def _set_signature_count(self):
        self.signatures = XDW_GetDocumentSignatureNumber(self.handle)

    def filename(self):
        """Get filename with extension."""
        return self.name + {"DOCUMENT": ".xdw", "BINDER": ".xbd"}[self.type]

    def pathname(self):
        """Get full pathname with extension."""
        return os.path.join(self.dir, self.filename())

    def update_pages(self):
        """Update number of pages; used after insert multiple pages in."""
        docinfo = XDW_GetDocumentInformation(self.handle)
        self.pages = docinfo.nPages

    def save(self):
        """Save document regardless of whether it is modified or not."""
        XDW_SaveDocument(self.handle)

    def close(self):
        """Close document."""
        if self._autosave:
            self.save()
        XDW_CloseDocumentHandle(self.handle)
        self.free()
        self.handle = None

    @staticmethod
    def _close(handle):
        XDW_CloseDocumentHandle(handle)
        XDWFile._free(handle)

    @property
    def show_annotations(self):
        return self._show_annotations

    @show_annotations.setter
    def show_annotations(self, value):
        value = bool(value)
        XDW_ShowOrHideAnnotations(self.handle, value)
        self._show_annotations = value
        return

    def __getattribute__(self, name):
        attribute_name = unicode(inner_attribute_name(name))
        if attribute_name not in XDW_DOCUMENT_ATTRIBUTE_W:
            self_signatures = object.__getattribute__(self, "signatures")
            if name == "status" and self_signatures:
                self_signature = object.__getattribute__(self, "signature")
                self_signature(0)  # Update document verification status.
            return object.__getattribute__(self, name)
        self_handle = object.__getattribute__(self, "handle")
        t, value, _ = XDW_GetDocumentAttributeByNameW(
                self_handle, attribute_name, codepage=CP)
        return makevalue(t, value)

    def __setattr__(self, name, value):
        attribute_name = unicode(inner_attribute_name(name))
        if attribute_name in XDW_DOCUMENT_ATTRIBUTE_W:
            t, value = typevalue(value)
            XDW_SetDocumentAttributeW(
                    self.handle, attribute_name, t, value,
                    XDW_TEXT_MULTIBYTE, codepage=CP)
            return
        object.__setattr__(self, name, value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_userattr(self, name, default=None):
        """Get user defined attribute.

        name        (str or unicode) attribute name
        default     value to return if no attribute named name exist
        """
        try:
            return XDW_GetUserAttribute(self.handle, cp(name))
        except InvalidArgError:
            return default

    def set_userattr(self, name, value):
        """Set user defined attribute."""
        XDW_SetUserAttribute(self.handle, cp(name), value)

    def has_property(self, name):
        """Test if user defined property exists.

        name        (str or unicode) name of property

        Returns True if such property exists, or False if not.
        """
        if not isinstance(name, basestring):
            raise TypeError("property name must be str or unicode")
        name = uc(name)
        try:
            t, value, _ = XDW_GetDocumentAttributeByNameW(
                    self.handle, uc(name), codepage=CP)
        except InvalidArgError:
            return False
        return True

    def get_property(self, name, default=None):
        """Get user defined property.

        name        (str or unicode) name of property, or user attribute
                    (int) property order which starts with 0
        default     value to return if no property named name exist

        Returns a unicode, int, bool or datetime.date.

        Note that previous set_property(str_value) gives unicode.
        """
        if isinstance(name, int):
            name, t, value, _ = XDW_GetDocumentAttributeByOrderW(
                    self.handle, name + 1)
            return (name, makevalue(t, value))
        try:
            t, value, _ = XDW_GetDocumentAttributeByNameW(
                    self.handle, uc(name), codepage=CP)
        except InvalidArgError:
            return default
        return makevalue(t, value)

    def set_property(self, name, value, update=True):
        """Set user defined property.

        name        (str or unicode) name of property, or user attribute
        value       (str, unicode, int, bool or datetime.date) stored value
                    (None) delete property if update==False
        update      (bool) False=don't update value if exists already

        Note that str value is actually stored in unicode and get_property()
        will returen unicode.
        """
        name = uc(name)  # Force to specify in unicode.
        if not update and self.get_property(name) is not None:
            return
        if value is None:
            self.del_property(name)
            return
        if isinstance(value, str):
            value = uc(value)  # Force to store in unicode.
        t, value = typevalue(value)
        if t != XDW_ATYPE_STRING:
            value = byref(value)
        XDW_SetDocumentAttributeW(
                self.handle, name, t, value, XDW_TEXT_MULTIBYTE, codepage=CP)
        self._set_property_count()

    def del_property(self, name):
        """Delete user defined property.

        name        (unicode) name of property, or user attribute
        """
        name = uc(name)  # Force to specify in unicode.
        XDW_SetDocumentAttributeW(
                self.handle, name, XDW_ATYPE_INT, NULL,
                XDW_TEXT_MULTIBYTE, codepage=CP)
        self._set_property_count()

    hasprop = has_property
    getprop = get_property
    setprop = set_property
    delprop = del_property

    def pageform(self, form):
        return PageForm(self, form)

    def pageform_text(self):
        """Get all text in page form."""
        return ASEP.join(self.pageform(form).text
                for form in ("header", "footer"))

    def update_pageform(self, sync=False):
        """Update page form.

        sync        (bool) also update pageforms for documents in binder
        """
        sync = XDW_PAGEFORM_REMOVE if sync else XDW_PAGEFORM_STAY
        XDW_UpdatePageForm(self.handle, sync)

    def delete_pageform(self, sync=False):
        """Delete page form.

        sync        (bool) also delete pageforms for documents in binder
        """
        sync = XDW_PAGEFORM_REMOVE if sync else XDW_PAGEFORM_STAY
        XDW_RemovePageForm(self.handle, sync)

    updform = update_pageform
    delform = delete_pageform

    def signature(self, pos):
        """Get signature information.

        Returns StampSignature or PKISignature object.
        """
        siginfo, modinfo = XDW_GetSignatureInformation(self.handle, pos + 1)
        if siginfo.nSignatureType == XDW_SIGNATURE_STAMP:
            sts = XDW_SIGNATURE_STAMP_STAMP[modinfo.nStampVerificationStatus]
            docsts = XDW_SIGNATURE_STAMP_DOC[modinfo.nDocVerificationStatus]
            sig = StampSignature(
                    self,
                    pos,
                    siginfo.nPage - 1,
                    Point(siginfo.nHorPos, siginfo.nVerPos) / 100.0,
                    Point(siginfo.nWidth, siginfo.nHeight) / 100.0,
                    fromunixtime(siginfo.nSignedTime),
                    stamp_name=modinfo.lpszStampName,
                    owner_name=modinfo.lpszOwnerName,
                    valid_until=fromunixtime(modinfo.nValidDate),
                    memo=modinfo.lpszRemarks,
                    status=sts,
                    )
            self.status = docsts
        else:  # siginfo.nSignatureType == XDW_SIGNATURE_PKI

            def parsedt(s):
                return datetime.datetime.strptime(s, "%Y/%m/%d %H:%M:%S")

            ver = XDW_SIGNATURE_PKI_TYPE[modinfo.nCertVerificationType]
            sts = XDW_SIGNATURE_PKI_CERT[modinfo.nCertVerificationStatus]
            docsts = XDW_SIGNATURE_PKI_DOC[modinfo.nDocVerificationStatus]
            sig = PKISignature(
                    self,
                    pos,
                    siginfo.nPage - 1,
                    Point(siginfo.nHorPos, siginfo.nVerPos) / 100.0,
                    Point(siginfo.nWidth, siginfo.nHeight) / 100.0,
                    fromunixtime(siginfo.nSignedTime),
                    stamp_name=modinfo.lpszStampName,
                    module=modinfo.lpszModule,
                    subject_dn=modinfo.lpszSubjectDN,
                    subject=modinfo.lpszSubject,
                    issuer_dn=modinfo.lpszIssuerDN,
                    issuer=modinfo.lpszIssuer,
                    not_before=parsedt(modinfo.lpszNotBefore),
                    not_after=parsedt(modinfo.lpszNotAfter),
                    serial=modinfo.lpszSerial,
                    certificate=modinfo.signer_cert,
                    memo=modinfo.lpszRemarks,
                    signing_time=parsedt(modinfo.lpszSigningTime),
                    verification_type=ver,
                    status=sts,
                    )
            self.status = docsts
        return sig

    def _process(self, meth, *args, **kw):
        selfpath = self.pathname()
        oldhandle = self.handle
        if oldhandle:
            self.save()
            self.close()
        newpath = meth(selfpath, *args, **kw)
        if kw.get("output_path"):
            if oldhandle:
                self.open(readonly=self.readonly,
                        authenticate=self.authenticate,
                        autosave=self._autosave)
            return newpath
        # Swap the old for the new, and remove the old.
        os.remove(selfpath)
        os.rename(newpath, selfpath)
        if oldhandle:
            self.open(readonly=self.readonly,
                    authenticate=self.authenticate,
                    autosave=self._autosave)
            # Renew related attributes.
            self.signatures = XDW_GetDocumentSignatureNumber(self.handle)
            self.status = None

    def sign(self,
            output_path=None,
            page=0,
            position=None,
            type_="STAMP",
            certificate=None):
        """Sign i.e. attach signature.

        See xdwfile.sign() for arguments.

        Returns actual pathname of signed file if output_path is specified;
        otherwise, nothing is returned.

        NB. self.save() is performed internally.
        """
        return self._process(sign, output_path=output_path, page=page,
                lposition=position, type_=type_, certificate=certificate)

    def protect(self,
            output_path=None,
            protect_type="PASSWORD",
            auth="NONE",
            **options):
        """Protect document/binder.

        See xdwfile.protect() for arguments.

        Returns pathname of protected file if output_path is specified;
        otherwise, nothing is returned.

        NB. Only password- or PKI-based protection is available.
        NB. self.save() is performed internally.
        """
        return self._process(protect, output_path=output_path,
                protect_type=protect_type, auth=auth, **options)

    def unprotect(self, output_path=None, auth="NONE"):
        """Release protection on document/binder.

        See xdwfile.unprotect() for arguments.

        Returns pathname of unprotected file if output_path is specified;
        otherwise, nothing is returned.

        NB. Only PKI- or STAMP-protected file is acceptable.
        NB. self.save() is performed internally.
        """
        return self._process(unprotect, output_path=output_path, auth=auth)

    def optimize(self, output_path=None):
        """Optimize document/binder file.

        See xdwfile.optimize() for arguments.

        Returns pathname of optimized file if output_path is specified;
        otherwise, nothing is returned.

        NB. self.save() is performed internally.
        """
        return self._process(optimize, output_path=output_path)


class BaseSignature(object):

    """Base class for StampSignature and PKISignature."""

    def __init__(self, doc, pos, pagepos, position, size, dt):
        """Initiator.

        doc             Document/Binder
        pos             position in signature list of doc; starts with 0
        pagepos         page number to paste signature on; starts with 0
        position        (Point) position in mm to paste signature on
        size            (Point) size in mm to show signature
        dt              (datetime.datetime) signed datetime
        """
        self.doc = doc
        self.pos = pos
        self.pagepos = pagepos
        self.position = position
        self.size = size
        self.dt = dt

    def __repr__(self):
        return  u"{cls}({doc}[{pos}])".format(
                cls=self.__class__.__name__,
                doc=self.doc.name,
                pos=self.pos,
                )

    def __str__(self):
        return  u"{cls}({doc}[{pos}]; page {pgpos}, position {loc}mm)".format(
                cls=self.__class__.__name__,
                doc=self.doc.name,
                pos=self.pos,
                pgpos=self.pagepos,
                loc="({0:.2f}, {1:.2f})".format(*self.position),
                )

    def update(self):
        """Update signature status.

        Note that the result of XDW_GetSignatureInformation() and therefore
        self.doc.status may be altered.
        """
        XDW_UpdateSignatureStatus(self.doc.handle, self.pos + 1)


class StampSignature(BaseSignature):

    """DocuWorks' built-in stamp signature."""

    def __init__(self, doc, pos, pagepos, position, size, dt,
            stamp_name="",
            owner_name="",
            valid_until=None,
            memo="",
            status=None,
            ):
        """Initiator.

        doc             Document/Binder
        pos             position in signature list of doc; starts with 0
        pagepos         page number to paste signature on; starts with 0
        position        (Point) position to paste signature on
        size            (Point) size to show signature
        dt              (datetime.datetime) signed datetime
        stamp_name      stamp's name
        owner_name      owner's name
        valid_until     (datetime.datetime) ending time of validity
        memo            (str)
        status          "NONE" | "TRUSTED" | "NOTRUST"
        """
        BaseSignature.__init__(self, doc, pos, pagepos, position, size, dt)
        self.stamp_name = stamp_name
        self.owner_name = owner_name
        self.valid_until = valid_until
        self.memo = memo
        self.status = status


class PKISignature(BaseSignature):

    """PKI-based signature."""

    def __init__(self, doc, pos, pagepos, position, size, dt,
            module="",
            subjectdn="",
            subject="",
            issuerdn="",
            issuer="",
            not_before=None,
            not_after=None,
            serial=None,
            certificate=None,
            memo="",
            signing_time=None,
            verification_type=None,
            status=None,
            ):
        """Initiator.

        doc             Document/Binder
        pos             position in signature list of doc; starts with 0
        pagepos         page number to paste signature on; starts with 0
        position        (Point) position to paste signature on
        size            (Point) size to show signature
        dt              (datetime.datetime) signed datetime
        module          security module name
        subjectdn       content of SUBJECT DN (distinguished name);
                        max. 511 bytes
        subject         content of SUBJECT; CN, OU, O or E
        issuerdn        content of ISSUER DN (distinguished name);
                        max. 511 bytes
        issuer          content of ISSUER; CN, OU, O or E
        not_before      (datetime.datetime)
        not_after       (datetime.datetime)
        serial          (str)
        certificate     (str) content of singer certificate in DER (RFC3280)
                        format
        memo            (str)
        signing_time    (datetime.datetime)
        verification_type   "LOW" | "MID_LOCAL" | "MID_NETWORK" |
                            "HIGH_LOCAL" | "HIGH_NETWORK"
        status          "UNKNOWN" | "OK" | "NO_ROOT_CERTIFICATE" |
                        "NO_REVOCATION_CHECK" | OUT_OF_VALIDITY" |
                        "OUT_OF_VALIDITY_AT_SIGNED_TIME |
                        "REVOKE_CERTIFICATE" |
                        "REVOKE_INTERMEDIATE_CERTIFICATE" |
                        "INVLIAD_SIGNATURE" | "INVALID_USAGE" |
                        "UNDEFINED_ERROR"
        """
        BaseSignature.__init__(self, doc, pos, pagepos, position, size, dt)
        self.module = module
        self.subjectdn = subjectdn[:511]  # max. 511 bytes
        self.subject = subject  # CN, OU, O or E
        self.issuerdn = issuerdn[:511]  # max. 511 bytes
        self.issuer = issuer  # CN, OU, O or E
        self.not_before = not_before
        self.not_after = not_after
        self.serial = serial
        self.certificate = certificate
        self.memo = memo
        self.signing_time = signing_time
        self.verification_type = verification_type
        self.status = status


class PageForm(object):

    """Header/footer of document."""

    @staticmethod
    def all_types():
        """Return all pageform types for convenience."""
        return tuple(sorted(XDW_PAGEFORM.values()))

    @staticmethod
    def all_attributes():
        """Return all pageform attributes for convenience."""
        return tuple(sorted(
                "alignment back_color beginning_page digit doc ending_page "
                "font_char_set font_name font_pitch_and_family font_size "
                "font_style fore_color form image_file left_right_margin "
                "page_range starting_number text top_bottom_margin "
                "ver_position zoom".split()))

    @staticmethod
    def all_colors():
        """Returns all colors available."""
        return tuple(sorted(XDW_COLOR.values()))

    def __init__(self, doc, form):
        self.__dict__["doc"] = doc
        self.__dict__["form"] = XDW_PAGEFORM.normalize(form)

    def __repr__(self):
        return u"{cls}({doc}.{attr})".format(
                cls=self.__class__.__name__,
                doc=self.doc,
                attr=outer_attribute_name(XDW_PAGEFORM[self.form]))

    @property
    def form(self):
        return self.__dict__["form"]

    @form.setter
    def form(self, value):
        object.__setattr__(self, "form", XDW_PAGEFORM.normalize(value))

    def __setattr__(self, name, value):
        attrname = inner_attribute_name(name)
        if attrname not in XDW_ANNOTATION_ATTRIBUTE:
            object.__setattr__(self, name, value)
            return
        special = isinstance(XDW_ANNOTATION_ATTRIBUTE[attrname][1], XDWConst)
        if special or isinstance(value, (int, float)):
            value = int(scale(attrname, value, store=True))
            if attrname.endswith("Page"):
                value += 1  # 1-based
            value = byref(c_int(value))
            attribute_type = XDW_ATYPE_INT  # TODO: Scaling may be required.
        elif isinstance(value, basestring):
            attribute_type = XDW_ATYPE_STRING
            """TODO: unicode handling.
            Currently Author has no idea to take unicode with ord < 256.
            Python's unicode may have inner representation with 0x00,
            e.g.  0x41 0x00 0x42 0x00 0x43 0x00 for "ABC".  This results in
            unexpected string termination e.g. "ABC" -> "A".  So, if the next
            if-block is not placed, you will get much more but inexact
            elements in result for abbreviated search string.
            """
            if isinstance(value, unicode):
                value = value.encode(CODEPAGE)  # TODO: unicode handling
            if 255 < len(value):
                raise ValueError("text length must be <= 255")
        # TODO: XDW_ATYPE_OTHER should also be valid.
        else:
            raise TypeError("illegal value " + repr(value))
        XDW_SetPageFormAttribute(self.doc.handle, self.form,
                attrname, attribute_type, value)

    def __getattribute__(self, name):
        attrname = inner_attribute_name(name)
        if attrname not in XDW_ANNOTATION_ATTRIBUTE:
            return object.__getattribute__(self, name)
        self_doc = object.__getattribute__(self, "doc")
        self_form = object.__getattribute__(self, "form")
        value = XDW_GetPageFormAttribute(self_doc.handle, self_form, attrname)
        attribute_type = XDW_ANNOTATION_ATTRIBUTE[attrname][0]
        if attribute_type == 1:  # string
            return unicode(value, CODEPAGE)
        value = unpack(value)
        if attrname.endswith("Page"):
            value -= 1  # 0-based
        return scale(attrname, value, store=False)

    def update(self, sync=False):
        """Update page form.

        sync        (bool) also update pageforms for documents in binder
        """
        sync = XDW_PAGEFORM_REMOVE if sync else XDW_PAGEFORM_STAY
        XDW_UpdatePageForm(self.doc.handle, sync)

    def delete(self, sync=False):
        """Delete page form.

        sync        (bool) also delete pageforms for documents in binder
        """
        sync = XDW_PAGEFORM_REMOVE if sync else XDW_PAGEFORM_STAY
        XDW_RemovePageForm(self.doc.handle, sync)
