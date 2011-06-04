#!/usr/bin/env python

import curses

from twisted.internet import reactor

from darklight.client import DarkClient

class Curdle(object):
    """
    Curses logic for a Darklight client.
    """

    def __init__(self):
        self.client = DarkClient()
        self.screen = curses.initscr()

    def fileno(self):
        return 0

    def doRead(self):
        reactor.stop()

    def logPrefix(self):
        return "Curdle"

    def connectionLost(self, reason):
        self.stop()

    def start(self):
        self.screen.nodelay(True)
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)
        self.screen.refresh()

    def stop(self):
        self.screen.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

curdle = Curdle()
curdle.start()
reactor.addReader(curdle)
reactor.run()
