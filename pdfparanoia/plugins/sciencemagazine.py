# -*- coding: utf-8 -*-

from copy import copy
import sys

from ..parser import parse_content
from ..eraser import remove_object_by_id
from ..plugin import Plugin

class ScienceMagazine(Plugin):
    """
    Science Magazine
    ~~~~~~~~~~~~~~~

    Remove ads from academic papers. :(
    """

    # TODO: better confirmation that the paper is from sciencemag. Look for
    # "oascentral" in one of the URIs, since the ads are all hyperlinked to
    # that server.

    @classmethod
    def scrub(cls, content, verbose=0):
        evil_ids = []

        # parse the pdf into a pdfminer document
        pdf = parse_content(content)

        # get a list of all object ids
        xref = pdf.xrefs[0]
        objids = xref.get_objids()

        # check each object in the pdf
        for objid in objids:
            # get an object by id
            obj = pdf.getobj(objid)

            if hasattr(obj, "attrs"):
                if ("Width" in obj.attrs) and str(obj.attrs["Width"]) == "432":
                    if "Height" in obj.attrs and str(obj.attrs["Height"]) == "230":
                        evil_ids.append(objid)

        if len(evil_ids) > 1:
            raise Exception("too many ads detected on the page, please double check?")

        for objid in evil_ids:
            content = remove_object_by_id(content, objid)

        return content
