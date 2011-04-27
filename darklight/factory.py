#!/usr/bin/env python

from base64 import b32encode
import os

import twisted.internet.protocol
import twisted.internet.ssl
import twisted.internet.task
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

class DarkServerFactory(twisted.internet.protocol.ServerFactory):

    protocol = DarkServerProtocol

    def __init__(self, conf):
        self.dc = conf

        self.db = DarkDB(self.dc.get("database", "url"))

        timer = DarkTimer("hashing files offline")
        self.update_library_now()
        timer.stop()

        if inotify:
            self.prepare_notify()

        else:
            loop = twisted.internet.task.LoopingCall(self.cache.update_single)
            loop.start(1.0)

        self.endpoint = TCP4ClientEndpoint(
            reactor, self.dc.get("passthrough", "host"),
            self.dc.getint("passthrough", "port"))

    def update_library_now(self):
        for folder, none in self.dc.items("folders"):
            os.path.walk(folder, self.update_library_path, None)

    def update_library_path(self, chaff, directory, names):
        for name in names:
            self.db.update(DarkFile(os.path.join(directory, name)))

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
