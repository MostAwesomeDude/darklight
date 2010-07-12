#!/usr/bin/env python

import logging
import time

logging.basicConfig(level=logging.DEBUG)

class DarkTimer:
    _state = {"clocks": dict(), "timeouts": dict()}

    clocks = None
    timeouts = None

    def __init__(self):
        self.__dict__ = self._state

    def start(self, string):
        self.clocks[string] = time.time()

    def stop(self, string):
        elapsed = time.time() - self.clocks.get(string)
        logging.info("Timer: %s finished in %.6f seconds" % (string, elapsed))

    def timeout(self, string, count):
        self.timeouts[string] = time.time() + count

    def checktime(self, string):
        return bool(self.timeouts[string] - self.clocks.get(string))
