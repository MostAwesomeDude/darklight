#!/usr/bin/env python

import os

import twisted.internet.protocol
import twisted.internet.ssl
import twisted.internet.task

from darklight.core.db import DarkDB
from darklight.core.cache import DarkCache
from darklight.core.timer import DarkTimer

from serverprotocol import DarkServerProtocol

class DarkServerFactory(twisted.internet.protocol.ServerFactory):
    protocol = DarkServerProtocol

    def configure(self):
        try:
            # XXX stopgap
            raise ImportError
            d = DarkNotify()
            d.start()
            d.add(self.dc.folders)
            print "Started inotify thread..."
        except (ImportError, NameError):
            print "Couldn't start inotify thread,"
            print "\ttry installing pyinotify."

    def __init__(self, conf):
        self.dc = conf
        self.configure()

        self.db = DarkDB()
        self.db.path = self.dc.get("database", "path")
        self.db.connect()

        self.cache = DarkCache(self.dc.getint("cache", "size"))
        self.cache.db = self.db

        for folder, none in self.dc.items("folders"):
            os.path.walk(folder, self.cache.add, None)

        if self.dc.get("cache", "hash-style").startswith("imm"):
            timer = DarkTimer("hashing files offline")
            self.cache.update()
            timer.stop()
        else:
            loop = twisted.internet.task.LoopingCall(self.cache.update_single)
            loop.start(1.0)

class DarkSSLFactory(twisted.internet.ssl.DefaultOpenSSLContextFactory):

    def __init__(self, conf):
        twisted.internet.ssl.DefaultOpenSSLContextFactory.__init__(
            self, conf.get("ssl", "key"), conf.get("ssl", "certificate"))
