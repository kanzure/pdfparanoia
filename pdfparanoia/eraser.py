# -*- coding: utf-8 -*-
"""
pdfparanoia.eraser
~~~~~~~~~~~~~~~

Tools to erase things from pdfs by direct manipulation of the pdf format.

"""

def manipulate_pdf(content, objid, callback, *args):
    """
    Iterates through a pdf looking for the object with the objid id. When the
    object is found, callback is called with a reference to the current list of
    output lines.
    """
    outlines = []
    content = content.replace("\r\n", "\n")
    lines = content.split("\n")
    last_line = None
    skip_mode = False
    for line in lines:
        if line == "":
            outlines.append("")
            continue
        if not skip_mode:
            if last_line in ["endobj", "endobj ", None]:
                if line[-3:] == "obj" or line[-4:] == "obj " or " obj <<" in line[0:50] or " obj<<" in line[0:50]:
                    if line.startswith(str(objid) + " "):
                        skip_mode = True
                        last_line = line
                        callback(outlines, *args)
                        continue
            outlines.append(line)
        elif skip_mode:
            if line == "endobj" or line == "endobj ":
                skip_mode = False
        last_line = line
    output = "\n".join(outlines)
    return output

def remove_object_by_id(content, objid):
    """
    Deletes an object from a pdf. Mostly streams and FlateDecode stuff.
    """
    def _remove_object(outlines): pass
    output = manipulate_pdf(content, objid, _remove_object)
    return output

def replace_object_with(content, objid, replacement):
    """
    Replaces an object from a pdf. Mostly streams. This is useful for replacing
    an encoded object with a plaintext object.
    """
    def _replace_object_with(outlines, details):
        objid = details["objid"]
        replacement = details["replacement"]

        output = str(objid) + " 0 obj\n"
        output += "<</Length " + str(len(replacement)+2) + ">>stream\n"
        output += replacement
        output += "\nendstream\nendobj\n"

        for line in output.split("\n"):
            outlines.append(line)

    output = manipulate_pdf(content, objid, _replace_object_with, {"objid": objid, "replacement": replacement})
    return output

