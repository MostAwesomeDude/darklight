# Copyright 2008 Corbin Simpson
# <cds@corbinsimpson.com>
# This code is provided under the terms of the GNU Public License, version 3.

import base64
import itertools
import math
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
            buf = self.left.value + self.right.value
            if thex:
                buf = "\x01" + buf
            self.value = tiger.tiger(buf).digest()
        else:
            self.value = self.left.value

class Leaf(object):
    """
    Special-case branch.
    """

    def __init__(self, value):
        self.value = value

class TTH(object):
    """A class describing a Tiger Tree Hash tree."""

    def __init__(self, filename=None, thex=True, maxlevels=0, blocksize=1024):
        self.inited = False
        self.thex = thex
        self.maxlevels = maxlevels
        if self.thex:
            self.blocksize = 1024
        else:
            self.blocksize = blocksize
        if filename:
            self.buildtree(filename)

    def buildtree(self, f):
        """Build the tree."""

        if self.inited:
            return

        if os.stat(f).st_size:
            h = open(f, "rb")
            leaves = []
            buf = h.read(self.blocksize)
            while len(buf):
                if self.thex:
                    buf = '\x00' + buf
                leaves.append(tiger.tiger(buf).digest())
                buf = h.read(self.blocksize)
            h.close()
        else:
            # File is empty, special-case hash
            if self.thex:
                leaves = [tiger.tiger("\x00").digest()]
            else:
                leaves = [tiger.tiger("").digest()]

        level = [Leaf(leaf) for leaf in leaves]
        self.levels = 0

        while len(level) > 1:
            self.levels += 1
            level = [Branch(left, right) for left, right in grouper(2, level)]
            print len(level)

        self.top = level[0]
        self.inited = True

    def gettree(self):
        if self.inited:
            return self.top

    def getroot(self):
        if self.inited:
            return base64.b32encode(self.top.value)

    def dump(self):
        print "Levels: %d" % self.levels
