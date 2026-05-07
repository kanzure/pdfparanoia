# -*- coding: utf-8 -*-
"""
CustomStrings plugin
~~~~~~~~~~~~~~~~~~~~

Removes caller-supplied substrings from PDF page content streams using
pikepdf, which understands the full content-stream token structure.

Usage::

    pdfparanoia.scrub(fh, scrub_strings=["Downloaded by user@example.com",
                                          "131.252.130.248"])
    # Case-sensitive (default is case-insensitive):
    pdfparanoia.scrub(fh, scrub_strings=["Korea"],
                      scrub_strings_case_sensitive=True)

Implementation notes:

* pikepdf's ``parse_content_stream`` is used to walk every ``Tj`` / ``TJ``
  instruction on every page.

* **Tj** (single string): the target bytes are replaced directly.

* **TJ** (kerning array): the string elements are *concatenated* to form a
  logical text run, the target is located within that run, and only the
  matched byte positions are removed from their respective string elements.
  This handles text split across multiple tokens by kerning adjustments
  (e.g. ``[(K)0.1(orea)]TJ`` renders as "Korea" in a viewer).

* Matching is case-insensitive by default; pass
  ``scrub_strings_case_sensitive=True`` to opt out.

* **Metadata scrubbing**: after processing content streams, the plugin also
  scrubs XMP metadata (all string and list-of-string values) and the classic
  DocInfo dictionary (``/Info`` entry).  Both are searched with the same
  case-sensitivity setting.

* Pass ``scrub_strings_metadata_only=True`` to skip content-stream scrubbing
  entirely and only scrub XMP / DocInfo.  Useful for removing a short
  substring (e.g. an institution name) from metadata without altering the
  rendered page text.
"""

import re
import sys
from io import BytesIO

import pikepdf

from ..plugin import Plugin


class CustomStrings(Plugin):
    """Remove caller-specified strings from all page content streams."""

    @classmethod
    def scrub(cls, content, verbose=False, **kwargs):
        scrub_strings = kwargs.get("scrub_strings") or []
        if not scrub_strings:
            return content

        case_sensitive = kwargs.get("scrub_strings_case_sensitive", False)
        metadata_only = kwargs.get("scrub_strings_metadata_only", False)
        re_flags = 0 if case_sensitive else re.IGNORECASE

        # Normalise targets to bytes (latin-1 round-trips all 256 byte values).
        targets = [
            s.encode("latin-1") if isinstance(s, str) else s
            for s in scrub_strings
        ]
        patterns = [re.compile(re.escape(t), re_flags) for t in targets]

        pdf = pikepdf.open(BytesIO(content))

        # XMP / DocInfo use Python str, not bytes -- build matching str patterns.
        str_targets = [t.decode("latin-1") for t in targets]
        str_patterns = [re.compile(re.escape(t), re_flags) for t in str_targets]

        for page in pdf.pages:
            if metadata_only:
                break
            instructions = list(pikepdf.parse_content_stream(page))
            changed = False
            new_instructions = []

            for operands, operator in instructions:
                op_str = str(operator)

                # ---- Tj: single string operand ---------------------------------
                if op_str == "Tj" and operands and isinstance(
                    operands[0], pikepdf.String
                ):
                    data = bytes(operands[0])
                    modified = data
                    for target, pattern in zip(targets, patterns):
                        if pattern.search(modified):
                            if verbose:
                                sys.stderr.write(
                                    "%s: Tj removing %r (case_%s)\n"
                                    % (
                                        cls.__name__,
                                        target.decode("latin-1", errors="replace"),
                                        "sensitive" if case_sensitive else "insensitive",
                                    )
                                )
                            modified = pattern.sub(b"", modified)
                    if modified != data:
                        operands = [pikepdf.String(modified)]
                        changed = True

                # ---- TJ: kerning array -----------------------------------------
                elif (
                    op_str == "TJ"
                    and operands
                    and isinstance(operands[0], pikepdf.Array)
                ):
                    arr = list(operands[0])

                    # Build a flat concatenation of string elements and a map
                    # from byte position in the concat back to (arr_idx, byte_idx).
                    concat = b""
                    idx_map = []  # list of (arr_idx, byte_idx_within_element)
                    for ai, elem in enumerate(arr):
                        if isinstance(elem, pikepdf.String):
                            b = bytes(elem)
                            for bi in range(len(b)):
                                idx_map.append((ai, bi))
                            concat += b

                    # Collect (arr_idx, byte_idx) pairs that are part of any match.
                    to_remove = set()
                    for target, pattern in zip(targets, patterns):
                        for m in pattern.finditer(concat):
                            if verbose:
                                sys.stderr.write(
                                    "%s: TJ removing %r (case_%s) "
                                    "spanning %d element(s)\n"
                                    % (
                                        cls.__name__,
                                        target.decode("latin-1", errors="replace"),
                                        "sensitive" if case_sensitive else "insensitive",
                                        len(
                                            {idx_map[p][0] for p in range(m.start(), m.end())}
                                        ),
                                    )
                                )
                            for pos in range(m.start(), m.end()):
                                to_remove.add(idx_map[pos])

                    if to_remove:
                        new_arr = []
                        for ai, elem in enumerate(arr):
                            if isinstance(elem, pikepdf.String):
                                b = bytes(elem)
                                new_b = bytes(
                                    byte
                                    for bi, byte in enumerate(b)
                                    if (ai, bi) not in to_remove
                                )
                                new_arr.append(pikepdf.String(new_b))
                            else:
                                new_arr.append(elem)
                        operands = [pikepdf.Array(new_arr)]
                        changed = True

                new_instructions.append((operands, operator))

            if changed:
                page["/Contents"] = pdf.make_stream(
                    pikepdf.unparse_content_stream(new_instructions)
                )

        # --- Scrub XMP metadata ------------------------------------------------
        with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
            for key in list(meta.keys()):
                val = meta[key]
                if isinstance(val, list):
                    new_list = []
                    for item in val:
                        new_item = item
                        for sp in str_patterns:
                            if sp.search(new_item):
                                if verbose:
                                    sys.stderr.write(
                                        "%s: XMP %s removing %r (case_%s)\n"
                                        % (
                                            cls.__name__,
                                            key,
                                            sp.pattern,
                                            "sensitive" if case_sensitive else "insensitive",
                                        )
                                    )
                                new_item = sp.sub("", new_item)
                        new_list.append(new_item)
                    if new_list != val:
                        meta[key] = new_list
                elif isinstance(val, str):
                    new_val = val
                    for sp in str_patterns:
                        if sp.search(new_val):
                            if verbose:
                                sys.stderr.write(
                                    "%s: XMP %s removing %r (case_%s)\n"
                                    % (
                                        cls.__name__,
                                        key,
                                        sp.pattern,
                                        "sensitive" if case_sensitive else "insensitive",
                                    )
                                )
                            new_val = sp.sub("", new_val)
                    if new_val != val:
                        meta[key] = new_val

        # --- Scrub DocInfo dictionary ------------------------------------------
        for key in list(pdf.docinfo.keys()):
            val = str(pdf.docinfo[key])
            new_val = val
            for sp in str_patterns:
                new_val = sp.sub("", new_val)
            if new_val != val:
                if verbose:
                    sys.stderr.write(
                        "%s: DocInfo %s value changed (case_%s)\n"
                        % (
                            cls.__name__,
                            key,
                            "sensitive" if case_sensitive else "insensitive",
                        )
                    )
                pdf.docinfo[key] = new_val

        out = BytesIO()
        pdf.save(out)
        return out.getvalue()

