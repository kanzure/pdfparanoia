# -*- coding: utf-8 -*-

from copy import copy
import sys

from ..parser import parse_content
from ..plugin import Plugin

class SPIE(Plugin):
    """
    Society of Photo-Optical Instrumentation Engineers
    ~~~~~~~~~~~~~~~

    These watermarks are shown on each page, but are only defined in one place.
    Also, there seems to be some interference from some of the other
    pdfparanoia plugins causing the deletion of images in the document.
    Side-effects need to be better accounted for.

    """

    @classmethod
    def scrub(cls, content, verbose=False):
        evil_ids = []

        # parse the pdf into a pdfminer document
        pdf = parse_content(content)

        # get a list of all object ids
        xrefs = pdf._parser.read_xref()
        xref = xrefs[0]
        objids = xref.get_objids()

        # check each object in the pdf
        for objid in objids:
            # get an object by id
            obj = pdf.getobj(objid)

            if hasattr(obj, "attrs"):
                # watermarks tend to be in FlateDecode elements
                if obj.attrs.has_key("Filter") and str(obj.attrs["Filter"]) == "/FlateDecode":
                    data = copy(obj.get_data())

                    phrase="Downloaded From:"
                    if phrase in data:
                        if verbose:
                            sys.stderr.write("%s: found object %s with %r; omitting..." % (cls.__name__, objid, phrase))
                        evil_ids.append(objid)

        for objid in evil_ids:
            # for some reason SPIE pdfs are broken by this, images are randomly removed
            #content = remove_object_by_id(content, objid)
            continue

        return content

