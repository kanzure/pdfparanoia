# -*- coding: utf-8 -*-

import unittest
import pdfparanoia

class RoyalSocietyOfChemistryTestCase(unittest.TestCase):
    def test_rsc(self):
        file_handler = open("tests/samples/rsc/3589bf649f8bb019bd97be9880627b7c.pdf", "rb")
        content = file_handler.read()
        file_handler.close()

        # Check the PDF is from the RSC
        self.assertIn("pubs.rsc.org", content)

        output = pdfparanoia.plugins.RoyalSocietyOfChemistry.scrub(content)

        # Check the PDF was output correctly and still 
        # contains the RSC url. 
        self.assertIn("pubs.rsc.org", output)

