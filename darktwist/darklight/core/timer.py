#!/usr/bin/env python

import logging
import time

logging.basicConfig(level=logging.DEBUG)

class DarkTimer:

    def __init__(self, message):
        self.message = message
        self.start()

    def start(self):
        self.clock = time.time()

    def stop(self):
        elapsed = time.time() - self.clock
        logging.info("Timer: %s finished in %.6f seconds" % (self.message,
            elapsed))
