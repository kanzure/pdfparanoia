# -*- coding: utf-8 -*-
"""
pdfparanoia.parser
~~~~~~~~~~~~~~~

Deals with the existential nature of parsing pdfs.

"""

try:
    from StringIO import StringIO
except ImportError: # py3k
    from io import StringIO, BytesIO

# Maybe one day pdfquery will be able to save pdf.
# from pdfquery import PDFQuery

import pdfminer.pdfparser
import pdfminer.pdfdocument

from .eraser import replace_object_with

def parse_pdf(handler):
    """
    Parses a PDF via pdfminer.
    """
    # reset to the beginning of the data
    handler.seek(0)

    # setup for parsing
    parser = pdfminer.pdfparser.PDFParser(handler)
    doc = pdfminer.pdfdocument.PDFDocument(parser)

    # actual parsing
    doc.initialize()

    return doc

def parse_content(content):
    """
    Parses a PDF via pdfminer from a string. There are some problems with
    pdfminer accepting StringIO objects, so this is a temporary hack.
    """
    stream = StringIO(content)
    return parse_pdf(stream)

def deflate(content):
    """
    Converts all FlateDecode streams into plaintext streams. This significantly
    increases the size of a pdf, but it's useful for debugging and searching
    for how watermarks are implemented.

    Not all elements are preserved in the resulting document. This is for
    debugging only.
    """
    # parse the pdf
    pdf = parse_content(content)

    # get a list of all object ids
    xref = pdf.xrefs[0]
    objids = xref.get_objids()

    # store new replacements
    replacements = []

    # scan through each object looking for things to deflate
    for objid in objids:
        obj = pdf.getobj(objid)
        if hasattr(obj, "attrs"):
            if obj.attrs.has_key("Filter") and str(obj.attrs["Filter"]) == "/FlateDecode":
                obj.decode()
                data = obj.data
                if len(data) < 1000:
                    replacements.append([objid, data])

    # apply the replacements to the document
    for (objid, replacement) in replacements:
        content = replace_object_with(content, objid, replacement)

    return content

