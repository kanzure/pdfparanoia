# -*- coding: utf-8 -*-

from copy import copy
import sys
from ..parser import parse_content
from ..plugin import Plugin
import base64

class RoyalSocietyOfChemistry(Plugin):
    """
    RoyalSocietyOfChemistry
    ~~~~~~~~~~~~~~~

    RSC watermarks each PDF with a "Downloaded" date and the name
    of the institution from which the PDF was downloaded.
    
    Watermarks removed:
        * "Downloaded by" watermark and timestamp on the each page
        * "Published on" watermark on the side of each page

    This was primary written for RSC PDF's from http://pubs.rsc.org
    """
        
    @classmethod
    def scrub(cls, content, verbose=0):
        replacements = []
        
        # List of watermark strings to remove
        watermarks = [
            "Downloaded by ",
            "Downloaded on ",
            "Published on ",
            #"View Article Online",
            #"Journal Homepage",
            #"Table of Contents for this issue",
        ]

        # Confirm the PDF is from the RSC
        if "pubs.rsc.org" in content:
            
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
                        rawdata = copy(obj.rawdata)
                        data = copy(obj.get_data())

                        # Check if any of the watermarks are in the current object
                        for phrase in watermarks:
                            if phrase in data:
                                if verbose >= 2:
                                    sys.stderr.write("%s: Found object %s with %r: %r; omitting...\n" % (cls.__name__, objid, phrase, data[data.index(phrase):data.index(phrase)+1000]))
                                elif verbose >= 1:
                                    sys.stderr.write("%s: Found object %s with %r; omitting...\n" % (cls.__name__, objid, phrase)) 
                                
                                # We had a match so replace the watermark data with an empty string                 
                                replacements.append([rawdata, ""])
            
        for deets in replacements:
            # Directly replace the stream data in binary encoded object
            content = content.replace( deets[0], deets[1])

        return content


