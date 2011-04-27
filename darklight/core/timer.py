#!/usr/bin/env python

from twisted.python import log
import time

class DarkTimer:

    def __init__(self, message):
        self.message = message
        self.start()

    def start(self):
        self.clock = time.time()
        log.msg("Timer: %s starting" % (self.message))

    def stop(self):
        elapsed = time.time() - self.clock
        log.msg("Timer: %s finished in %.6f seconds" % (self.message,
            elapsed))
