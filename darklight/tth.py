# Copyright 2008 Corbin Simpson
# <cds@corbinsimpson.com>
# This code is provided under the terms of the GNU Public License, version 3.

import base64
import itertools
import os

import tiger

def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.izip_longest(fillvalue=fillvalue, *args)

class Branch(object):
    """
    Helper class for describing binary trees.

    Nodes can be cut off at any point to form a complete tree.
    """

    def __init__(self, left, right=None, thex=True):
        self.left = left
        self.right = right

        if self.right:
            buf = self.left.hash + self.right.hash
            if thex:
                buf = "\x01" + buf
            self.hash = tiger.tiger(buf).digest()
            self.size = self.left.size + self.right.size
        else:
            self.size = self.left.size
            self.hash = self.left.hash

class Leaf(object):
    """
    Special-case branch.
    """

    def __init__(self, size, hash):
        self.size = size
        self.hash = hash

class TTH(object):
    """A class describing a Tiger Tree Hash tree."""

    top = None
    """
    The top of the tree.

    May be None if the tree has not been initialized.
    """

    complete = False
    """
    Whether this tree is complete.

    Completed trees have leaves for every single block in the object they have
    hashed.
    """

    def __init__(self, thex=True, maxlevels=0, blocksize=1024):
        self.thex = thex
        self.maxlevels = maxlevels

        if self.thex:
            self.blocksize = 1024
        else:
            self.blocksize = blocksize

    def build_tree_from_path(self, f):
        """
        Build a complete tree by hashing a file.
        """

        if os.stat(f).st_size:
            h = open(f, "rb")
            leaves = []
            buf = h.read(self.blocksize)
            while len(buf):
                if self.thex:
                    buf = '\x00' + buf
                leaves.append((len(buf), tiger.tiger(buf).digest()))
                buf = h.read(self.blocksize)
            h.close()
        else:
            # File is empty, special-case hash
            if self.thex:
                leaves = [(0, tiger.tiger("\x00").digest())]
            else:
                leaves = [(0, tiger.tiger("").digest())]

        level = [Leaf(size, hash) for size, hash in leaves]
        self.levels = 0

        while len(level) > 1:
            self.levels += 1
            level = [Branch(left, right) for left, right in grouper(2, level)]

        self.top = level[0]
        self.complete = True
