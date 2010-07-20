#!/usr/bin/env python

import os

import twisted.internet.protocol
import twisted.internet.ssl
import twisted.internet.task

from darklight.core import DarkDB, DarkCache, DarkConf, DarkTimer

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
        if self.dc.path:
            self.db.path = self.dc.path
        self.db.connect()

        self.cache = DarkCache(self.dc.cache_size)
        self.cache.db = self.db

        for folder in self.dc.folders:
            os.path.walk(folder, self.cache.add, None)

        if self.dc.immhash:
            timer = DarkTimer("hashing files offline")
            self.cache.update()
            timer.stop()
        else:
            loop = twisted.internet.task.LoopingCall(self.cache.update_single)
            loop.start(1.0)

class DarkSSLFactory(twisted.internet.ssl.DefaultOpenSSLContextFactory):
    pass
