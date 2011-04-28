#!/usr/bin/env python

import os
import unittest

from darklight.tth import TTH

class TTHTest(unittest.TestCase):

    def test_devnull(self):
        expected = ']\x9e\xd0\n\x03\x0ec\x8b\xdbu:j$\xfb\x90\x0eZc\xb8\xe7>l%\xb6'
        t = TTH()
        t.buildtree(os.devnull)
        self.assertEqual(t.top.hash, expected)
        self.assertEqual(t.top.size, 0)

    def test_devnull_no_thex(self):
        expected = '2\x93\xacc\x0c\x13\xf0$_\x92\xbb\xb1vn\x16\x16zNXI-\xdes\xf3'
        t = TTH(thex=False)
        t.buildtree(os.devnull)
        self.assertEqual(t.top.hash, expected)
        self.assertEqual(t.top.size, 0)

if __name__ == "__main__":
    unittest.main()
