#!/usr/bin/env python

import base64
import os
import stat

import tth

import sqlalchemy.ext.declarative

from twisted.python import log

from darklight.core.timer import DarkTimer

class DarkFile(sqlalchemy.ext.declarative.declarative_base()):
    """
    A file in the library.
    """

    __tablename__ = "files"

    serial = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    path = sqlalchemy.Column(sqlalchemy.String)
    size = sqlalchemy.Column(sqlalchemy.Integer)
    mtime = sqlalchemy.Column(sqlalchemy.Integer)
    tth = sqlalchemy.Column(sqlalchemy.PickleType)

    def __init__(self, path):
        self.path = os.path.normpath(path).decode("utf8")
        s = os.stat(self.path)
        self.size = s[stat.ST_SIZE]
        self.mtime = s[stat.ST_MTIME]
        self.blocksize = 128*1024
        self.dirty = True
        log.msg("DarkFile: " + self.path)

    def info(self):
        return (self.size, self.tth.getroot(), self.dirty)

    def match(self, tth, size):
        log.msg((size, tth))
        log.msg((self.size, self.tth.getroot()))
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
        timer = DarkTimer("hashing " + self.path)
        self.tth = tth.TTH(thex=False, blocksize=self.blocksize)
        self.tth.buildtree(self.path)
        self.dump()
        timer.stop()

    def update(self):
        if self.dirty:
            self.hash()
            self.dirty = False

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
        log.msg((self.size, self.tth.getroot()))
        # self.tth.dump()
