# -*- coding: utf-8 -*-

import unittest
import pdfparanoia

class JSTORTestCase(unittest.TestCase):
    def test_jstor(self):
        file_handler = open("tests/samples/jstor/231a515256115368c142f528cee7f727.pdf", "rb")
        content = file_handler.read()
        file_handler.close()
        self.assertIn("\n18 0 obj \n", content)

        # this section will later be manipulated
        self.assertIn("\n19 0 obj \n", content)

        output = pdfparanoia.plugins.JSTOR.scrub(content)

        # FlateDecode should be replaced with a decompressed section
        self.assertIn("\n19 0 obj\n<</Length 2862>>stream", output)

