# -*- coding: utf-8 -*-
"""
pdfparanoia.eraser
~~~~~~~~~~~~~~~

Tools to erase things from pdfs by direct manipulation of the pdf format.

"""

def remove_object_by_id(content, objid):
    """
    Deletes an object from a pdf. Mostly streams and FlateDecode stuff.
    """
    outlines = []
    lines = content.split("\n")
    last_line = None
    skip_mode = False
    for line in lines:
        if not skip_mode:
            if last_line in ["endobj", None]:
                if line[-3:] == "obj":
                    if line.startswith(str(objid) + " "):
                        skip_mode = True
                        last_line = line
                        continue
            outlines.append(line)
        elif skip_mode:
            if line == "endobj":
                skip_mode = False
        last_line = line
    output = "\n".join(outlines)
    return output

