#!/usr/bin/env python

import base64
import os
import stat

from darklight.tth import TTH

from sqlalchemy import (Column, ForeignKey, Boolean, Integer, LargeBinary,
    String)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from twisted.python import log

from darklight.core.timer import DarkTimer

Base = declarative_base()

class DarkTTH(Base):
    """
    A TTH node in the database.

    Any node can be a complete or partial tree.
    """

    __tablename__ = "hashes"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("hashes.id"))
    size = Column(Integer)
    hash = Column(LargeBinary)
    is_leaf = Column(Boolean, default=False)
    offset = Column(Integer)

    children = relationship("DarkTTH",
        backref=backref("parent", remote_side=id))

    def __init__(self, size, hash):
        self.size = size
        self.hash = hash

    def __repr__(self):
        return "<DarkTTH(%d, %s)>" % (self.size, self.hash.encode("hex"))

    @classmethod
    def from_tree(cls, tth):
        """
        Save a TTH tree into the database, returning the top of the tree.
        """

        node = cls(tth.size, tth.hash)

        if tth.is_leaf:
            node.is_leaf = True
            node.offset = tth.offset
        else:
            node.children = [cls.from_tree(tth.left)]
            if tth.right:
                node.children.append(cls.from_tree(tth.right))

        return node

class DarkFile(Base):
    """
    A file in the library.
    """

    __tablename__ = "files"

    path = Column(String, primary_key=True)
    size = Column(Integer)
    mtime = Column(Integer, default=-1)
    tth_id = Column(Integer, ForeignKey("hashes.id"))

    tth = relationship("DarkTTH", backref=backref("file", uselist=False))

    blocksize = 128 * 1024
    dirty = False

    def __init__(self, path):
        self.path = os.path.normpath(path).decode("utf8")
        self.update_from_fs()
        log.msg("DarkFile: " + self.path)

    def __repr__(self):
        return "<DarkFile(%s, %d)>" % (self.path.encode("utf8"), self.size)

    def update_from_fs(self):
        """
        Gather data from the filesystem.

        This method will dirty the file if appropriate.
        """

        s = os.stat(self.path)
        size = s[stat.ST_SIZE]
        mtime = s[stat.ST_MTIME]

        if size != self.size or mtime != self.mtime:
            self.size = size
            self.mtime = mtime
            self.dirty = True

    def clean(self):
        if self.dirty:
            self.hash()

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
        tth = TTH(thex=False, blocksize=self.blocksize)
        tth.build_tree_from_path(self.path)
        self.tth = DarkTTH.from_tree(tth.top)
        timer.stop()

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
