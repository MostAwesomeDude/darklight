#!/usr/bin/env python

from twisted.internet.inotify import INotify
from twisted.python import log
from twisted.python.filepath import FilePath

def notified(self, filepath, mask):
    log.msg("Was notified: %s %s %s" % (self, filepath, mask))

class DarkNotify(object):

    def __init__(self):
        self.notifier = INotify()
        self.notifier.startReading()

    def add(self, folders):
        self.notifier.watch(FilePath(folders), callbacks=[notified])
