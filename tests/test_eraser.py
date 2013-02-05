# -*- coding: utf-8 -*-

import unittest
from pdfparanoia.eraser import remove_object_by_id

class EraserTestCase(unittest.TestCase):
    def test_remove_object_by_id(self):
        content = ""
        output = remove_object_by_id(content, 1)
        self.assertEqual(content, output)

        content = ""
        output = remove_object_by_id(content, 2)
        self.assertEqual(content, output)

        content = ""
        output = remove_object_by_id(content, 100)
        self.assertEqual(content, output)

        content = "1 0 obj\nthings\nendobj\nleftovers"
        output = remove_object_by_id(content, 2)
        self.assertEqual(content, output)

        content = "1 0 obj\nthings\nendobj\nleftovers"
        output = remove_object_by_id(content, 1)
        self.assertEqual("leftovers", output)

