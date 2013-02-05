# -*- coding: utf-8 -*-
"""
pdfparanoia.parser
~~~~~~~~~~~~~~~

Deals with the existential nature of parsing pdfs.

"""

from StringIO import StringIO

# Maybe one day pdfquery will be able to save pdf.
# from pdfquery import PDFQuery

from pdfminer.pdfparser import (
    PDFParser,
    PDFDocument,
)

def parse_pdf(handler):
    """
    Parses a PDF via pdfminer.
    """
    # reset to the beginning of the data
    handler.seek(0)

    # setup for parsing
    parser = PDFParser(handler)
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)

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

