# -*- coding: utf-8 -*-
"""
pdfparanoia.core
~~~~~~~~~~~~~~~

This module provides most of the heavy lifting of pdfparanoia.

"""

import sys
import inspect

from .parser import (
    parse_pdf,
    parse_content,
)

from .plugin import Plugin

from pdfparanoia.plugins import *

def find_plugins():
    """
    Returns a list of all compatible plugins.
    """
    def inspection(thing):
        iswanted = inspect.isclass(thing)
        iswanted = iswanted and issubclass(thing, Plugin)
        iswanted = iswanted and thing is not Plugin
        return iswanted
    plugins = inspect.getmembers(sys.modules[__name__], inspection)
    plugins = [each[1] for each in plugins]
    return plugins

def scrub(obj, verbose=False, **kwargs):
    """
    Removes watermarks from a pdf and returns the resulting pdf as a string.

    Extra keyword arguments are forwarded to every plugin's scrub() method.
    For example, pass scrub_strings=["Downloaded by", "user@example.com"] to
    remove arbitrary substrings from all FlateDecode streams.
    """
    # reset the file handler
    if hasattr(obj, "seek"):
        obj.seek(0)
    else:
        obj = open(obj, "rb")

    # load up the raw bytes
    content = obj.read()

    # get a list of plugins that will manipulate this paper
    plugins = find_plugins()

    # clean this pdf as much as possible
    for plugin in plugins:
        content = plugin.scrub(content, verbose=verbose, **kwargs)

    return content

