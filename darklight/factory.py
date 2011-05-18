#!/usr/bin/env python

from base64 import b32encode
import os

from twisted.internet.protocol import ServerFactory
import twisted.internet.ssl
from twisted.internet.task import coiterate
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint

from darklight.core.db import DarkDB
from darklight.core.timer import DarkTimer

from darklight.protocol.darkserver import DarkServerProtocol

try:
    from darklight.core.inotify import DarkNotify
    inotify = True
except ImportError:
    inotify = False

class DarkServerFactory(ServerFactory):

    protocol = DarkServerProtocol

    def __init__(self, conf):
        self.dc = conf

        self.db = DarkDB(self.dc.get("database", "url"))

        if inotify:
            self.prepare_notify()

        self.endpoint = TCP4ClientEndpoint(
            reactor, self.dc.get("passthrough", "host"),
            self.dc.getint("passthrough", "port"))

    def startFactory(self):
        g = (self.db.get_or_create_file(f)
            for f in self.library_update_iterator())
        coiterate(g)

    def library_update_iterator(self):
        timer = DarkTimer("library update")
        for folder, none in self.dc.items("folders"):
            for directory, directories, files in os.walk(folder):
                for name in files:
                    yield os.path.join(directory, name)
        timer.stop()

    def buildProtocol(self, addr):
        p = self.protocol(self.endpoint)
        p.factory = self
        return p

    def prepare_notify(self):
        d = DarkNotify()
        for folder, none in self.dc.items("folders"):
            d.add(folder)

    def sendpeze(self, h, size, piece):
        """
        Get a chunk of a file.

        Pieces are always 64KiB big, and are indexed on 64KiB boundaries.

        :param str h: the hash
        :param int size: the size
        :param int piece: the index of the requested piece
        """

        tth = self.db.find_branch(h, size)
        if not tth:
            return None

        top = tth
        while top.file is None:
            top = top.parent

        f = top.file
        handle = open(f.path, "rb")
        handle.seek(tth.offset + piece)
        data = handle.read(65336)
        return data

class DarkSSLFactory(twisted.internet.ssl.DefaultOpenSSLContextFactory):

    def __init__(self, conf):
        twisted.internet.ssl.DefaultOpenSSLContextFactory.__init__(
            self, conf.get("ssl", "key"), conf.get("ssl", "certificate"))
