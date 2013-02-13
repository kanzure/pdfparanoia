# -*- coding: utf-8 -*-
"""
pdfparanoia.plugin
~~~~~~~~~~~~~~~

Defines how plugins work.

"""

class Plugin:
    @classmethod
    def scrub(cls, content, verbose=False):
        """
        Removes watermarks from the given pdf.
        """
        raise NotImplementedError("must be implemented by the subclass")

