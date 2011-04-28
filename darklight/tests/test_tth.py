#!/usr/bin/env python

import os
import unittest

from darklight.tth import Branch, Leaf, TTH

class TTHTest(unittest.TestCase):

    def test_devnull(self):
        expected = ']\x9e\xd0\n\x03\x0ec\x8b\xdbu:j$\xfb\x90\x0eZc\xb8\xe7>l%\xb6'
        t = TTH()
        t.build_tree_from_path(os.devnull)
        self.assertEqual(t.top.hash, expected)
        self.assertEqual(t.top.size, 0)

    def test_devnull_no_thex(self):
        expected = '2\x93\xacc\x0c\x13\xf0$_\x92\xbb\xb1vn\x16\x16zNXI-\xdes\xf3'
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
        tth.top = Leaf(1, "asdf")
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
            [tth.top.left, tth.top])

    def test_incomplete_right(self):
        tth = TTH()
        tth.top = Branch.as_incomplete(1, "asdf")
        tth.top.right = Branch.as_incomplete(2, "asdf")
        self.assertEqual(list(tth.iter_incomplete_branches()),
            [tth.top.right, tth.top])

if __name__ == "__main__":
    unittest.main()
