# -*- coding: utf-8 -*-
"""
Tests for the CustomStrings plugin and the --scrub-strings CLI argument.

Sample PDF: tests/samples/aip/a7132c0d62d7c00e92e8e0553f480556.pdf

Why the IP address and not "Korea"
-----------------------------------
The AIP watermark text "Downloaded 04 Feb 2013 to 131.252.130.248. ..."
lives inside a FlateDecode (zlib-compressed) stream.  After decompression
the IP ``131.252.130.248`` is a contiguous byte sequence, so the plugin
can find and remove it.

"Korea" appears three times in a PDF viewer but is encoded in a TJ kerning
array as ``(K)0.1(orea)`` — the characters K and orea are separate PDF
string tokens separated by a numeric kerning adjustment.  The IP address does
NOT appear as a literal byte sequence anywhere in the raw (compressed) file;
it is only revealed after decompression.
"""

import os
import re
import subprocess
import sys
import unittest
import zlib
from io import BytesIO

import pikepdf
import pdfparanoia.plugins

SAMPLE = os.path.join(
    os.path.dirname(__file__),
    "samples", "aip", "a7132c0d62d7c00e92e8e0553f480556.pdf",
)

# A string that IS present in a decompressed FlateDecode stream (AIP watermark).
LITERAL_STRING = "131.252.130.248"

# "Korea" appears in two forms inside stream 22:
#   - (K)0.1(orea)  TJ-kerning split -- NOT removable by byte matching
#   - (Korea.)       contiguous literal -- IS removable by byte matching
# So scrub_strings=["Korea"] WILL change the content (removing the
# contiguous occurrence) even though the kerning-split form survives.
KOREA_LITERAL = "Korea"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _string_in_any_stream(pdf_bytes, string):
    """Return True if *string* appears in any decompressed FlateDecode stream."""
    target = string.encode("latin-1") if isinstance(string, str) else string
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", pdf_bytes, re.DOTALL):
        try:
            if target in zlib.decompress(m.group(1)):
                return True
        except zlib.error:
            pass
    return False


def _count_in_streams(pdf_bytes, string):
    """Count total occurrences of *string* across all decompressed FlateDecode streams."""
    target = string.encode("latin-1") if isinstance(string, str) else string
    total = 0
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", pdf_bytes, re.DOTALL):
        try:
            total += zlib.decompress(m.group(1)).count(target)
        except zlib.error:
            pass
    return total


def _count_tj_aware(pdf_bytes, string, case_sensitive=False):
    """Count occurrences of *string* in TJ/Tj operands across all pages (pikepdf).

    Concatenates consecutive string elements within each TJ array so that
    kerning-split text (e.g. ``[(K)0.1(orea)]TJ``) is counted as one match.
    """
    flags = 0 if case_sensitive else re.IGNORECASE
    target = string.encode("latin-1") if isinstance(string, str) else string
    pattern = re.compile(re.escape(target), flags)
    count = 0
    pdf = pikepdf.open(BytesIO(pdf_bytes))
    for page in pdf.pages:
        for operands, operator in pikepdf.parse_content_stream(page):
            op = str(operator)
            if op == "Tj" and operands and isinstance(operands[0], pikepdf.String):
                count += len(pattern.findall(bytes(operands[0])))
            elif op == "TJ" and operands and isinstance(operands[0], pikepdf.Array):
                concat = b"".join(
                    bytes(e)
                    for e in operands[0]
                    if isinstance(e, pikepdf.String)
                )
                count += len(pattern.findall(concat))
    return count


# ---------------------------------------------------------------------------
# Plugin unit tests
# ---------------------------------------------------------------------------

class CustomStringsPluginTestCase(unittest.TestCase):

    def _raw_content(self):
        with open(SAMPLE, "rb") as fh:
            return fh.read()

    # -- fixture sanity checks -----------------------------------------------

    def test_ip_present_in_decompressed_stream(self):
        """The IP address exists in a decompressed FlateDecode stream."""
        self.assertTrue(_string_in_any_stream(self._raw_content(), LITERAL_STRING))

    def test_ip_not_present_as_literal_raw_bytes(self):
        """The IP address is compressed; it is NOT a raw byte sequence in the file."""
        self.assertNotIn(LITERAL_STRING.encode(), self._raw_content())

    def test_korea_not_present_as_literal_bytes(self):
        """Korea is visible in a viewer but TJ-split; not a contiguous byte run."""
        self.assertNotIn(KOREA_LITERAL.encode(), self._raw_content())

    def test_korea_present_in_decompressed_stream(self):
        """Korea appears as a contiguous literal (Korea.) in stream 22."""
        self.assertTrue(_string_in_any_stream(self._raw_content(), KOREA_LITERAL))

    # -- CustomStrings.scrub() direct -----------------------------------------

    def test_scrub_strings_removes_ip_from_streams(self):
        """IP address is removed from all decompressed streams after scrubbing."""
        content = self._raw_content()
        self.assertTrue(_string_in_any_stream(content, LITERAL_STRING))

        output = pdfparanoia.plugins.CustomStrings.scrub(
            content, scrub_strings=[LITERAL_STRING]
        )

        self.assertFalse(_string_in_any_stream(output, LITERAL_STRING))
        self.assertTrue(output.startswith(b"%PDF"))

    def test_scrub_strings_korea_removes_contiguous_occurrence(self):
        """scrub_strings=["Korea"] removes the (Korea.) form; stream changes."""
        content = self._raw_content()
        self.assertTrue(_string_in_any_stream(content, KOREA_LITERAL))
        output = pdfparanoia.plugins.CustomStrings.scrub(
            content, scrub_strings=[KOREA_LITERAL]
        )
        self.assertFalse(_string_in_any_stream(output, KOREA_LITERAL))
        self.assertTrue(output.startswith(b"%PDF"))

    def test_korea_count_before_and_after_scrub(self):
        """Korea contiguous byte count > 0 before scrub; 0 after.

        The PDF viewer shows "Korea" 3 times.  At the raw-byte level (after
        FlateDecode decompression) only one occurrence is a contiguous byte
        sequence (``Korea.`` in a plain Tj string).  The other two are encoded
        as TJ kerning arrays -- ``(K)0.1(orea)`` -- and are therefore not
        contiguous bytes.  After scrubbing, the byte-level count drops to 0
        because the pikepdf-based plugin also empties the TJ-split elements.
        """
        content = self._raw_content()
        before = _count_in_streams(content, KOREA_LITERAL)
        self.assertGreater(before, 0, "expected at least one contiguous Korea in streams")

        output = pdfparanoia.plugins.CustomStrings.scrub(
            content, scrub_strings=[KOREA_LITERAL]
        )
        after = _count_in_streams(output, KOREA_LITERAL)
        self.assertEqual(after, 0, "all contiguous Korea occurrences should be removed")

    def test_korea_tj_aware_count_before_and_after_scrub(self):
        """TJ-aware count finds all 3 viewer-rendered Korea occurrences; 0 after scrub."""
        content = self._raw_content()
        before = _count_tj_aware(content, KOREA_LITERAL)
        self.assertEqual(before, 3, "PDF viewer shows Korea 3 times")

        output = pdfparanoia.plugins.CustomStrings.scrub(
            content, scrub_strings=[KOREA_LITERAL]
        )
        after = _count_tj_aware(output, KOREA_LITERAL)
        self.assertEqual(after, 0, "all TJ-aware Korea occurrences should be removed")

    def test_scrub_strings_empty_list_is_noop(self):
        """An empty scrub_strings list leaves content untouched."""
        content = self._raw_content()
        output = pdfparanoia.plugins.CustomStrings.scrub(content, scrub_strings=[])
        self.assertEqual(content, output)

    def test_scrub_strings_none_is_noop(self):
        """scrub_strings=None leaves content untouched."""
        content = self._raw_content()
        output = pdfparanoia.plugins.CustomStrings.scrub(content, scrub_strings=None)
        self.assertEqual(content, output)

    def test_output_is_still_valid_pdf(self):
        """Output starts with the PDF header after scrubbing."""
        content = self._raw_content()
        output = pdfparanoia.plugins.CustomStrings.scrub(
            content, scrub_strings=[LITERAL_STRING]
        )
        self.assertTrue(output.startswith(b"%PDF"))

    # -- case sensitivity -----------------------------------------------------

    def test_scrub_case_insensitive_default(self):
        """Case-insensitive matching is on by default; lower-case target hits."""
        content = self._raw_content()
        # "korea" (all lower-case) should still find and remove "Korea" / "korea"
        output = pdfparanoia.plugins.CustomStrings.scrub(
            content, scrub_strings=[KOREA_LITERAL.lower()]
        )
        self.assertFalse(_string_in_any_stream(output, KOREA_LITERAL))

    def test_scrub_case_sensitive_no_match_on_wrong_case(self):
        """Case-sensitive matching does NOT remove a differently-cased target."""
        content = self._raw_content()
        output = pdfparanoia.plugins.CustomStrings.scrub(
            content,
            scrub_strings=[KOREA_LITERAL.lower()],  # "korea" won't hit "Korea"
            scrub_strings_case_sensitive=True,
        )
        # The contiguous "Korea" occurrence must still be present.
        self.assertTrue(_string_in_any_stream(output, KOREA_LITERAL))


# ---------------------------------------------------------------------------
# Metadata tests
# ---------------------------------------------------------------------------

def _make_pdf_with_metadata(base_pdf_bytes, xmp_fields=None, docinfo_fields=None):
    """Return bytes of a PDF derived from *base_pdf_bytes* with extra metadata.

    *xmp_fields*    -- dict of XMP key -> str or list-of-str
    *docinfo_fields* -- dict of '/Key' -> str  (classic /Info dictionary)
    """
    pdf = pikepdf.open(BytesIO(base_pdf_bytes))
    if xmp_fields:
        with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
            for k, v in xmp_fields.items():
                meta[k] = v
    if docinfo_fields:
        for k, v in docinfo_fields.items():
            pdf.docinfo[k] = v
    out = BytesIO()
    pdf.save(out)
    return out.getvalue()


def _get_xmp_value(pdf_bytes, key):
    """Return the XMP metadata value for *key*, or None if absent."""
    with pikepdf.open(BytesIO(pdf_bytes)).open_metadata(
        set_pikepdf_as_editor=False
    ) as meta:
        return meta.get(key)


def _get_docinfo_value(pdf_bytes, key):
    """Return the DocInfo string value for *key*, or None if absent."""
    pdf = pikepdf.open(BytesIO(pdf_bytes))
    val = pdf.docinfo.get(key)
    return str(val) if val is not None else None


class MetadataScrubbingTestCase(unittest.TestCase):
    """Tests that scrub_strings also removes matches from XMP and DocInfo."""

    def _raw_content(self):
        with open(SAMPLE, "rb") as fh:
            return fh.read()

    # -- XMP -----------------------------------------------------------------

    def test_xmp_string_value_is_scrubbed(self):
        """A scrub target present in an XMP string field is removed."""
        content = _make_pdf_with_metadata(
            self._raw_content(),
            xmp_fields={"dc:description": "Downloaded by 131.252.130.248 from AIP"},
        )
        self.assertIn("131.252.130.248", _get_xmp_value(content, "dc:description"))

        output = pdfparanoia.plugins.CustomStrings.scrub(
            content, scrub_strings=[LITERAL_STRING]
        )
        self.assertNotIn("131.252.130.248", _get_xmp_value(output, "dc:description") or "")

    def test_xmp_list_value_is_scrubbed(self):
        """A scrub target in an XMP list-of-strings field is removed from each item."""
        content = _make_pdf_with_metadata(
            self._raw_content(),
            xmp_fields={"dc:creator": ["Korea Institute", "Another Author"]},
        )
        self.assertIn("Korea", _get_xmp_value(content, "dc:creator")[0])

        output = pdfparanoia.plugins.CustomStrings.scrub(
            content, scrub_strings=[KOREA_LITERAL]
        )
        for item in (_get_xmp_value(output, "dc:creator") or []):
            self.assertNotIn("Korea", item)

    def test_xmp_case_insensitive_scrub(self):
        """XMP scrubbing respects case-insensitive default."""
        content = _make_pdf_with_metadata(
            self._raw_content(),
            xmp_fields={"dc:subject": ["KOREA university"]},
        )
        output = pdfparanoia.plugins.CustomStrings.scrub(
            content, scrub_strings=[KOREA_LITERAL.lower()]  # "korea"
        )
        for item in (_get_xmp_value(output, "dc:subject") or []):
            self.assertNotIn("KOREA", item)

    def test_xmp_case_sensitive_no_match(self):
        """XMP scrubbing with case_sensitive=True does not remove wrong-case text."""
        content = _make_pdf_with_metadata(
            self._raw_content(),
            xmp_fields={"dc:subject": ["KOREA university"]},
        )
        output = pdfparanoia.plugins.CustomStrings.scrub(
            content,
            scrub_strings=[KOREA_LITERAL.lower()],  # "korea" != "KOREA"
            scrub_strings_case_sensitive=True,
        )
        items = _get_xmp_value(output, "dc:subject") or []
        self.assertTrue(any("KOREA" in item for item in items))

    # -- DocInfo -------------------------------------------------------------

    def test_docinfo_value_is_scrubbed(self):
        """A scrub target present in a DocInfo field is removed."""
        content = _make_pdf_with_metadata(
            self._raw_content(),
            docinfo_fields={"/Author": "Downloaded by 131.252.130.248"},
        )
        self.assertIn("131.252.130.248", _get_docinfo_value(content, "/Author"))

        output = pdfparanoia.plugins.CustomStrings.scrub(
            content, scrub_strings=[LITERAL_STRING]
        )
        self.assertNotIn("131.252.130.248", _get_docinfo_value(output, "/Author") or "")

    def test_docinfo_case_insensitive_scrub(self):
        """DocInfo scrubbing respects case-insensitive default."""
        content = _make_pdf_with_metadata(
            self._raw_content(),
            docinfo_fields={"/Subject": "Korea Institute of Technology"},
        )
        output = pdfparanoia.plugins.CustomStrings.scrub(
            content, scrub_strings=["korea"]
        )
        self.assertNotIn("Korea", _get_docinfo_value(output, "/Subject") or "")

    # -- metadata_only -------------------------------------------------------

    def test_metadata_only_skips_content_streams(self):
        """scrub_strings_metadata_only=True leaves page content streams untouched."""
        content = _make_pdf_with_metadata(
            self._raw_content(),
            docinfo_fields={"/Author": "131.252.130.248"},
        )
        # IP is also present in content streams; metadata_only must NOT remove it there.
        self.assertTrue(_string_in_any_stream(content, LITERAL_STRING))

        output = pdfparanoia.plugins.CustomStrings.scrub(
            content,
            scrub_strings=[LITERAL_STRING],
            scrub_strings_metadata_only=True,
        )
        # Content streams unchanged.
        self.assertTrue(_string_in_any_stream(output, LITERAL_STRING))
        # Metadata scrubbed.
        self.assertNotIn("131.252.130.248", _get_docinfo_value(output, "/Author") or "")

    def test_metadata_only_scrubs_xmp(self):
        """scrub_strings_metadata_only=True still scrubs XMP."""
        content = _make_pdf_with_metadata(
            self._raw_content(),
            xmp_fields={"dc:description": "Korea Institute watermark"},
        )
        output = pdfparanoia.plugins.CustomStrings.scrub(
            content,
            scrub_strings=[KOREA_LITERAL],
            scrub_strings_metadata_only=True,
        )
        self.assertNotIn("Korea", _get_xmp_value(output, "dc:description") or "")
        # TJ-split Korea in content streams must be untouched.
        self.assertEqual(_count_tj_aware(output, KOREA_LITERAL), 3)


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

class CustomStringsCLITestCase(unittest.TestCase):
    """Exercises the -s / --scrub-strings flag on bin/pdfparanoia."""

    CLI = os.path.join(os.path.dirname(__file__), "..", "bin", "pdfparanoia")

    def _run_cli(self, *extra_args):
        cmd = [sys.executable, self.CLI] + list(extra_args) + [SAMPLE]
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_cli_scrub_strings_ip_removed_from_streams(self):
        """-s removes the IP from decompressed streams via the CLI."""
        result = self._run_cli("-s", LITERAL_STRING)
        self.assertEqual(result.returncode, 0, msg=result.stderr.decode(errors="replace"))
        self.assertIn(b"%PDF", result.stdout)
        self.assertFalse(_string_in_any_stream(result.stdout, LITERAL_STRING))

    def test_cli_scrub_strings_korea_no_error(self):
        """-s Korea runs without error (removes the contiguous (Korea.) form)."""
        result = self._run_cli("-s", KOREA_LITERAL)
        self.assertEqual(result.returncode, 0, msg=result.stderr.decode(errors="replace"))
        self.assertIn(b"%PDF", result.stdout)

    def test_cli_scrub_strings_multiple(self):
        """Multiple -s flags are each applied."""
        result = self._run_cli("-s", LITERAL_STRING, "-s", "Redistribution")
        self.assertEqual(result.returncode, 0, msg=result.stderr.decode(errors="replace"))
        self.assertIn(b"%PDF", result.stdout)
        self.assertFalse(_string_in_any_stream(result.stdout, LITERAL_STRING))

    def test_cli_no_scrub_strings_still_works(self):
        """CLI works normally without --scrub-strings."""
        result = self._run_cli()
        self.assertEqual(result.returncode, 0, msg=result.stderr.decode(errors="replace"))
        self.assertIn(b"%PDF", result.stdout)

    def test_cli_only_scrub_metadata_leaves_streams(self):
        """--only-scrub-metadata does not remove the IP from content streams."""
        result = self._run_cli("-s", LITERAL_STRING, "--only-scrub-metadata")
        self.assertEqual(result.returncode, 0, msg=result.stderr.decode(errors="replace"))
        self.assertIn(b"%PDF", result.stdout)
        # Content stream still contains the IP (metadata_only skips streams).
        self.assertTrue(_string_in_any_stream(result.stdout, LITERAL_STRING))


if __name__ == "__main__":
    unittest.main()

