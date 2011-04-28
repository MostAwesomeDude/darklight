# Copyright 2008 Corbin Simpson
# <cds@corbinsimpson.com>
# This code is provided under the terms of the GNU Public License, version 3.

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

    def __init__(self, left=None, right=None, thex=True):
        self.left = left
        self.right = right

        if self.left and self.right:
            buf = self.left.hash + self.right.hash
            if thex:
                buf = "\x01" + buf
            self.hash = tiger.tiger(buf).digest()
            self.size = self.left.size + self.right.size
        elif self.left:
            self.size = self.left.size
            self.hash = self.left.hash

    def __eq__(self, other):
        return self.size == other.size and self.hash == other.hash

    @classmethod
    def as_incomplete(cls, size, hash, **kwargs):
        """
        Make an incomplete branch node.
        """

        self = cls(**kwargs)
        self.size = size
        self.hash = hash

        return self

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

    def __init__(self, thex=False, maxlevels=0, blocksize=128 * 1024):
        self.thex = thex

        if self.thex:
            self.blocksize = 1024
        else:
            self.blocksize = blocksize

    @classmethod
    def from_size_and_hash(cls, size, hash, **kwargs):
        """
        Create an incomplete tree from a size and a hash.

        The tree may end up being complete if it only has one node.
        """

        self = cls(**kwargs)
        if size > self.blocksize:
            self.top = Branch.as_incomplete(size, hash, thex=self.thex)
            self.complete = False
        else:
            self.top = Leaf(size, hash)
            self.complete = True

        return self

    def iter_incomplete_branches(self):
        """
        Get a list of branches which have incomplete children.

        This method goes through the entire tree regardless of whether it is
        marked as complete.
        """

        stack = [self.top]

        while stack:
            current = stack[-1]
            if isinstance(current, Leaf):
                stack.pop()
            elif current.left:
                stack.append(current.left)
            elif current.right:
                stack.append(current.right)
            else:
                while not (current.left and current.right):
                    yield stack.pop()
                    if stack:
                        current = stack[-1]
                    else:
                        break

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
            level = [Branch(left, right, thex=self.thex)
                for left, right in grouper(2, level)]

        self.top = level[0]
        self.complete = True
