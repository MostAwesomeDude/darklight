#!/usr/bin/env python

import base64
import os
import stat

import tth

from db import DarkDB
from timer import DarkTimer

import logging
logging.basicConfig(level=logging.DEBUG)

class DarkFile:
    """An object representing a file in the system."""

    def __init__(self, path):
        self.path = os.path.normpath(path).decode("utf8")
        s = os.stat(self.path)
        self.size = s[stat.ST_SIZE]
        self.mtime = s[stat.ST_MTIME]
        self.blocksize = 128*1024
        self.dirty = True
        DarkDB().verify(self)
        logging.debug("DarkFile: " + self.path)

    def info(self):
        return (self.size, self.tth.getroot(), self.dirty)

    def match(self, tth, size):
        logging.debug((size, tth))
        logging.debug((self.size, self.tth.getroot()))
        if not size and not tth:
            return False
        if size and (size != self.size):
            return False
        if self.dirty:
            self.update()
        if tth and (base64.b32encode(tth) != self.tth.getroot()):
            return False
        return True

    def hash(self):
        DarkTimer().start("hashing " + self.path)
        self.tth = tth.TTH(thex=False, blocksize=self.blocksize)
        self.tth.buildtree(self.path)
        self.dump()
        DarkTimer().stop("hashing " + self.path)

    def update(self):
        if not self.dirty:
            return
        self.hash()
        self.dirty = False
        DarkDB().update(self)

    def getpiece(self, pnum):
        self.update()
        leaves = self.tth.gettree()
        if pnum < len(leaves[-1]):
            return leaves[-1][pnum]
        else:
            return None

    def getdata(self, pnum):
        self.update()
        offset = self.blocksize * pnum
        if offset < self.size:
            buf = ""
            f = open(self.path, "rb")
            f.seek(offset)
            buf = f.read(self.blocksize)
            f.close()
            return buf
        else:
            return None

    def dump(self):
        logging.debug((self.size, self.tth.getroot()))
        # self.tth.dump()
