# -*- coding: utf-8 -*-
"""
pdfparanoia.plugin
~~~~~~~~~~~~~~~

Defines how plugins work.

"""

class Plugin:
    @classmethod
    def scrub(cls, content, verbose=False, **kwargs):
        """
        Removes watermarks from the given pdf.

        Extra keyword arguments (e.g. scrub_strings) are forwarded from
        pdfparanoia.core.scrub() so plugins can opt-in to runtime parameters.
        """
        raise NotImplementedError("must be implemented by the subclass")

