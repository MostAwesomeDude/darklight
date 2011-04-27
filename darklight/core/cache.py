#!/usr/bin/env python

import os

from twisted.python import log

from darklight.core.file import DarkFile
from darklight.core.timer import DarkTimer

class DarkCache(object):
    """
    A simple cache and file manager.
    """

    db = None

    def __init__(self, maxsize):
        self.files = []
        self.pcache = {}
        self.phits = {}
        self.size = 0
        self.maxsize = maxsize
        self.dump()

    def __iter__(self):
        return iter(self.files)

    def dump(self):
        log.msg("Cache size: " + str(self.size))
        log.msg("Cache maxsize: " + str(self.maxsize))

    def setsize(self, size):
        self.maxsize = int(size)
        while self.size > self.maxsize:
            for f in self.files:
                if f.size > self.maxsize and self.iscached(f):
                    self.uncache(f)

    def add(self, blah, dir, path):
        '''This is for os.path.walk()'''
        # Skip . files
        for p in path:
            if p.startswith('.'):
                path.remove(p)
        for f in (os.path.join(dir, i) for i in path):
            if os.path.isfile(f):
                f = DarkFile(f)
                self.db.verify(f)
                self.files.append(f)

    def update(self):
        for f in self.files:
            if not f.update():
                self.db.update(f)

    def update_single(self):
        try:
            f = next(i for i in self.files if i.dirty)
            f.update()
            self.db.update(f)
        except StopIteration:
            pass

    def precache(self, piece, data):
        # Already cached?
        if piece in self.pcache:
            return
        # Too big to fit into cache?
        if len(data) + self.size >= self.maxsize:
            return
        self.pcache[piece] = data
        self.size += len(self.pcache[piece])

    def uncache(self, piece):
        if piece in self.pcache:
            self.size -= len(self.pcache[piece])
            del self.pcache[piece]

    def getpiece(self, f, pnum):
        return f.getpiece(pnum)

    def getdata(self, f, pnum):
        assert f in self.files, "Who decided *you* could have a DarkFile?"
        piece = f.getpiece(pnum)
        if not piece:
            # OOB?
            return None
        if piece in self.pcache:
            return self.pcache[piece]
        else:
            data = f.getdata(pnum)
            self.precache(piece, data)
            return data

    def search(self, tth, size):
        timer = DarkTimer("search")
        l = [f for f in self.files if f.match(tth, size)]
        timer.stop()
        return l
