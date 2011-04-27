#!/usr/bin/env python

from base64 import b32encode
import os

from twisted.internet.protocol import ServerFactory
import twisted.internet.ssl
from twisted.internet.task import coiterate
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint

from darklight.core.db import DarkDB
from darklight.core.file import DarkFile
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
        The hash is some form of TTH hash. The size and piece are ASCII
        decimal.
        """

        l = self.factory.cache.search(h, size)
        if len(l) == 1:
            buf = self.factory.cache.getdata(l[0], piece)
            if not buf:
                print "File buffer was bad..."
                self.error()
                return
            i, sent = 0, 0
            tth = b32encode(self.factory.cache.getpiece(l[0], piece))
            return tth, buf
        else:
            self.error()

class DarkSSLFactory(twisted.internet.ssl.DefaultOpenSSLContextFactory):

    def __init__(self, conf):
        twisted.internet.ssl.DefaultOpenSSLContextFactory.__init__(
            self, conf.get("ssl", "key"), conf.get("ssl", "certificate"))
