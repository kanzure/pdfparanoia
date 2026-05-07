# -*- coding: utf-8 -*-
"""
CustomStrings plugin
~~~~~~~~~~~~~~~~~~~~

Removes caller-supplied literal substrings from every FlateDecode stream in
the PDF using zlib directly — no pdfminer dependency.

Usage::

    pdfparanoia.scrub(fh, scrub_strings=["Downloaded by user@example.com",
                                          "131.252.130.248"])

Implementation notes:

* Each ``stream … endstream`` block whose compressed payload successfully
  decompresses with :func:`zlib.decompress` is treated as a FlateDecode
  stream.  Non-FlateDecode streams (LZW, ASCII85, etc.) fail decompression
  and are left untouched.
* Matching streams are decompressed, target bytes removed,
  re-compressed with :func:`zlib.compress`, and the ``/Length`` entry in
  the preceding object dictionary is updated to reflect the new size.
* "Korea" (and similar text encoded with TJ kerning arrays) will **not** be
  matched because the characters are split across separate PDF string tokens
  (e.g. ``(K)0.1(orea)``); see test suite for details.
"""

import re
import sys
import zlib

from ..plugin import Plugin

# Match the raw compressed payload of every stream…endstream block.
_STREAM_RE = re.compile(rb"stream\r?\n(.*?)\r?\nendstream", re.DOTALL)

# Match a /Length entry so we can update it after re-compression.
_LENGTH_RE = re.compile(rb"/Length\s+\d+")


class CustomStrings(Plugin):
    """Remove caller-specified literal strings from all FlateDecode streams."""

    @classmethod
    def scrub(cls, content, verbose=False, **kwargs):
        scrub_strings = kwargs.get("scrub_strings") or []
        if not scrub_strings:
            return content

        # Normalise targets to bytes (latin-1 round-trips all 256 byte values).
        targets = [
            s.encode("latin-1") if isinstance(s, str) else s
            for s in scrub_strings
        ]

        pieces = []
        last_end = 0

        for m in _STREAM_RE.finditer(content):
            raw_data = m.group(1)

            # Try to decompress; skip if this is not a zlib/FlateDecode stream.
            try:
                decompressed = zlib.decompress(raw_data)
            except zlib.error:
                pieces.append(content[last_end : m.end()])
                last_end = m.end()
                continue

            modified = decompressed
            hit = False
            for target in targets:
                if target in modified:
                    if verbose:
                        sys.stderr.write(
                            "%s: removing %r from stream at offset %d\n"
                            % (
                                cls.__name__,
                                target.decode("latin-1", errors="replace"),
                                m.start(),
                            )
                        )
                    modified = modified.replace(target, b"")
                    hit = True

            if not hit:
                pieces.append(content[last_end : m.end()])
                last_end = m.end()
                continue

            recompressed = zlib.compress(modified)

            # Collect everything from the last processed position up to the
            # 's' in 'stream', then patch the /Length in the object header.
            before_stream = content[last_end : m.start()]

            obj_marker = before_stream.rfind(b" obj")
            if obj_marker != -1:
                before_obj = before_stream[: obj_marker + 4]
                after_obj = before_stream[obj_marker + 4 :]
                after_obj = _LENGTH_RE.sub(
                    b"/Length " + str(len(recompressed)).encode(),
                    after_obj,
                )
                before_stream = before_obj + after_obj

            pieces.append(before_stream)
            pieces.append(b"stream\n" + recompressed + b"\nendstream")
            last_end = m.end()

        pieces.append(content[last_end:])
        return b"".join(pieces)
