#!/usr/bin/env python

import os

import twisted.internet.protocol
import twisted.internet.task

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
            DarkTimer().start("hashing files offline")
            DarkCache().update()
            DarkTimer().stop("hashing files offline")
        else:
            loop = twisted.internet.task.LoopingCall(DarkCache().update_single)
            loop.start(1.0)
