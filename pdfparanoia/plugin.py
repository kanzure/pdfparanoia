# -*- coding: utf-8 -*-
"""
pdfparanoia.plugin
~~~~~~~~~~~~~~~

Defines how plugins work.

"""

class Plugin:
    @staticmethod
    def scrub(content):
        """
        Removes watermarks from the given pdf.
        """
        raise NotImplementedError("must be implemented by the subclass")

