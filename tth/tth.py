# Copyright 2008 Corbin Simpson
# <cds@corbinsimpson.com>
# This code is provided under the terms of the GNU Public License, version 3.

import base64
import math
import os

import tiger

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

        self.levels = int(math.ceil(math.log(len(leaves),2)))
        self.level = [leaves]

        for i in range(self.levels):
            l = []

            for j in range(0, len(self.level[i]), 2):
                try:
                    buf = self.level[i][j] + self.level[i][j+1]
                    if self.thex:
                        buf = '\x01' + buf
                    l.append(tiger.tiger(buf).digest())
                except IndexError:
                    l.append(self.level[i][j])

            self.level.append(l)

        self.level.reverse()
        if self.maxlevels:
            del self.level[self.maxlevels:]

        self.inited = True

    def gettree(self):
        if self.inited:
            return self.level

    def getroot(self):
        if self.inited:
            return base64.b32encode(self.level[0][0])

    def dump(self):
        print "Levels:", len(self.level)
        for i, level in enumerate(self.level):
            print "Level", i, ":", [base64.b32encode(j) for j in level]
