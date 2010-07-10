#!/usr/bin/env python

import os
import stat

from db import DarkDB
from timer import DarkTimer

import logging

class DarkFile:
    """An object representing a file in the system."""
    _state = {"serial": 0}

    def __init__(self, path):
        self.serial = self._state.get("serial")
        self._state["serial"] += 1
        self.path = os.path.normpath(path)
        s = os.stat(self.path)
        self.size = s[stat.ST_SIZE]
        self.mtime = s[stat.ST_MTIME]
        self.blocksize = 128*1024
        self.dirty = True
        DarkDB().verify(self)
        logging.debug("DarkFile: " + self.path)

    def info(self):
        return (self.size, self.tth.getroot(), self.dirty)

    def match(self, size, tth):
        if not size and not tth:
            return False
        if size and (size != self.size):
            return False
        if self.dirty:
            self.update()
        if tth and (tth != self.tth.getroot()):
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
        offset = self.blocksize*pnum
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
#self.tth.dump()
