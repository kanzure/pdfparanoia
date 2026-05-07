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
        """Korea appears in decompressed streams before scrub; count reaches 0 after.

        The PDF viewer shows "Korea" 3 times.  Two are encoded as TJ-kerning
        arrays -- ``(K)0.1(orea)`` -- which the viewer renders as "Korea" but
        which are NOT contiguous byte sequences.  The third is the literal
        ``(Korea.)`` string object, which IS a contiguous byte sequence and is
        therefore removable by this plugin.  After scrubbing, the byte-level
        count of contiguous "Korea" occurrences drops to 0.
        """
        content = self._raw_content()
        before = _count_in_streams(content, KOREA_LITERAL)
        self.assertGreater(before, 0, "expected at least one contiguous Korea in streams")

        output = pdfparanoia.plugins.CustomStrings.scrub(
            content, scrub_strings=[KOREA_LITERAL]
        )
        after = _count_in_streams(output, KOREA_LITERAL)
        self.assertEqual(after, 0, "all contiguous Korea occurrences should be removed")

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


if __name__ == "__main__":
    unittest.main()

