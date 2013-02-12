# -*- coding: utf-8 -*-

import unittest
import pdfparanoia

class SPIETestCase(unittest.TestCase):
    def test_spie(self):
        file_handler = open("tests/samples/spie/266c86e6f47e39415584450f5a3af4d0.pdf", "rb")
        content = file_handler.read()
        self.assertIn("\n46 0 obj", content)

        output = pdfparanoia.plugins.SPIE.scrub(content)
        self.assertNotIn("\n55 0 obj", output)

