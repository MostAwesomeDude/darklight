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
        curses.start_color()

        max_y, max_x = self.screen.getmaxyx()

        self.status = self.screen.derwin(1, max_x, max_y - 1, 0)
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)

    def fileno(self):
        return 0

    def doRead(self):
        c = self.screen.getch()
        if c == ord("q"):
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

        self.set_status("Welcome to Darklight!")

    def stop(self):
        self.screen.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def set_status(self, message):
        y, x = self.status.getmaxyx()
        if x > len(message):
            message = message.center(x - 1, " ")
        self.status.clear()
        self.status.addnstr(0, 0, message, x,
            curses.A_BOLD | curses.color_pair(1))
        self.status.refresh()

curdle = Curdle()
curdle.start()
reactor.addReader(curdle)
reactor.run()
