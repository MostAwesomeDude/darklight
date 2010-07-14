#!/usr/bin/env python

import base64
import binascii
import os

from file import DarkFile
from timer import DarkTimer

import logging
logging.basicConfig(level=logging.DEBUG)

def makelong(s):
    try:
        return long(s)
    except ValueError:
        logging.debug("Couldn't cast '%s' to long..." % s)

class DarkCache(object):
    """
    A simple cache and file manager.
    """

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
        logging.debug("Cache size: " + str(self.size))
        logging.debug("Cache maxsize: " + str(self.maxsize))

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
                self.files.append(DarkFile(f))

    def update(self):
        [f.update() for f in self.files]

    def update_single(self):
        try:
            next(i for i in self.files if i.dirty).update()
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

    def search(self, tokens):
        DarkTimer().start("search")
        tth = None
        size = None
        for token in tokens:
            if len(token) == 48:
                tth = binascii.unhexlify(token)
            elif len(token) == 40:
                tth = base64.b32decode(token)
            elif len(token) == 24:
                tth = token
            elif not len(token):
                continue
            else:
                size = makelong(token)
                if not size:
                    return None
        l = [f for f in self.files if f.match(size, tth)]
        DarkTimer().stop("search")
        return l
