#!/usr/bin/env python

import os
import unittest
import tempfile

from darklight.tth import Branch, TTH

class TTHTestVectors(unittest.TestCase):
    """
    Test the THEX vectors.

    While THEX might not be Darklight's perferred mode of operation, it is
    essential that it be supported.
    """

    def test_devnull(self):
        expected = "]\x9e\xd0\n\x03\x0ec\x8b\xdbu:j$\xfb\x90\x0eZc\xb8\xe7>l%\xb6"
        t = TTH(thex=True)
        t.build_tree_from_path(os.devnull)
        self.assertEqual(t.top.hash, expected)
        self.assertEqual(t.top.size, 0)

    def test_zero(self):
        f = tempfile.NamedTemporaryFile()
        f.write("\x00")
        f.flush()
        f.seek(0)

        expected = ("\xaa\xbb\xcc\xa0\x84\xac\xec\xd0Q"
             "\x1d\x1fb2\xa1{\xfa\xef\xa4A\xb2\x98.UH")
        t = TTH(thex=True)
        t.build_tree_from_path(f.name)
        self.assertEqual(t.top.hash, expected)
        self.assertEqual(t.top.size, 1)

    def test_1024_a(self):
        f = tempfile.NamedTemporaryFile()
        f.write("A" * 1024)
        f.flush()
        f.seek(0)

        expected = ("_\xbd\x0eb\xad\x01mYkw\xd1\xd2"
            "\x88\x83\xb9O\xedx\xec\xba\xf4d\t\x14")
        t = TTH(thex=True)
        t.build_tree_from_path(f.name)
        self.assertEqual(t.top.hash, expected)
        self.assertEqual(t.top.size, 1024)

    def test_1025_a(self):
        f = tempfile.NamedTemporaryFile()
        f.write("A" * 1025)
        f.flush()
        f.seek(0)

        expected = ("~Y\x1c\x1c\xd8\xf2\xe6\x12\x1f\xdb"
            "\xcd\x80q\xba'\x96&\xb7qd-\x10\xa3\xdb")
        t = TTH(thex=True)
        t.build_tree_from_path(f.name)
        self.assertEqual(t.top.hash, expected)
        self.assertEqual(t.top.size, 1025)

    def test_devnull_no_thex(self):
        expected = "2\x93\xacc\x0c\x13\xf0$_\x92\xbb\xb1vn\x16\x16zNXI-\xdes\xf3"
        t = TTH(thex=False)
        t.build_tree_from_path(os.devnull)
        self.assertEqual(t.top.hash, expected)
        self.assertEqual(t.top.size, 0)

class IterIncompleteBranches(unittest.TestCase):

    def test_single_leaf(self):
        """
        A single leaf shouldn't be incomplete.
        """

        tth = TTH()
        tth.top = Branch.as_incomplete(1, "asdf", is_leaf=True)
        self.assertEqual(list(tth.iter_incomplete_branches()), [])

    def test_single_branch(self):
        """
        Single branches are incomplete.
        """

        tth = TTH()
        tth.top = Branch.as_incomplete(1, "asdf")
        self.assertEqual(list(tth.iter_incomplete_branches()),
            [tth.top])

    def test_incomplete_left(self):
        tth = TTH()
        tth.top = Branch.as_incomplete(1, "asdf")
        tth.top.left = Branch.as_incomplete(2, "asdf")
        self.assertEqual(list(tth.iter_incomplete_branches()),
            [tth.top, tth.top.left])

    def test_incomplete_right(self):
        tth = TTH()
        tth.top = Branch.as_incomplete(1, "asdf")
        tth.top.right = Branch.as_incomplete(2, "asdf")
        self.assertEqual(list(tth.iter_incomplete_branches()),
            [tth.top, tth.top.right])

class TTHTestAPI(unittest.TestCase):

    def test_from_size_and_hash_leaf(self):
        tth = TTH.from_size_and_hash(1, "asdf")
        self.assertTrue(tth.complete)
        self.assertEqual(tth.top.size, 1)
        self.assertEqual(tth.top.hash, "asdf")

    def test_from_size_and_hash_branch(self):
        tth = TTH.from_size_and_hash(1000000, "asdf")
        self.assertFalse(tth.complete)
        self.assertEqual(tth.top.size, 1000000)
        self.assertEqual(tth.top.hash, "asdf")

if __name__ == "__main__":
    unittest.main()
