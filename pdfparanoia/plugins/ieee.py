# -*- coding: utf-8 -*-

from copy import copy
import sys

from ..parser import parse_content
from ..eraser import remove_object_by_id
from ..plugin import Plugin

class IEEEXplore(Plugin):
    """
    IEEE Xplore
    ~~~~~~~~~~~~~~~

    """

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
                # watermarks tend to be in FlateDecode elements
                if "Filter" in obj.attrs and str(obj.attrs["Filter"]) == "/FlateDecode":
                    #length = obj.attrs["Length"]
                    #rawdata = copy(obj.rawdata)
                    data = copy(obj.get_data())

                    phrase= "Authorized licensed use limited to: "
                    if phrase in str(data):
                        if verbose >= 2:
                            sys.stderr.write("%s: Found object %s with %r: %r; omitting..." % (cls.__name__, objid, phrase, data[data.index(phrase):data.index(phrase)+1000]))
                        elif verbose >= 1:
                            sys.stderr.write("%s: Found object %s with %r; omitting..." % (cls.__name__, objid, phrase,))

                        evil_ids.append(objid)

        for objid in evil_ids:
            content = remove_object_by_id(content, objid)

        return content

