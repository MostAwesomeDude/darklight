#!/usr/bin/env python

import os

import twisted.internet.protocol

from darklight.core import DarkCache, DarkConf, DarkTimer

from serverprotocol import DarkServerProtocol

class DarkServerFactory(twisted.internet.protocol.ServerFactory):
    protocol = DarkServerProtocol

    def configure(self, opts):
        DarkTimer().start("parsing configuration")
        self.dc.parse(opts["conf"])
        DarkTimer().stop("parsing configuration")
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

    def __init__(self, opts):
        self.dc = DarkConf()
        self.configure(opts)
        for folder in self.dc.folders:
            os.path.walk(folder, DarkCache().add, None)
        if self.dc.immhash:
            twisted.internet.reactor.callInThread(
                DarkCache().update)
