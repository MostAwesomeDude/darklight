#!/usr/bin/env python

import curses
from curses.textpad import Textbox

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.python import log
log.startLogging(open("curdl.log", "w"))

from darklight.client import DarkClient

class AsyncTextbox(Textbox):
    """
    A Textbox which doesn't block the reactor.
    """

    def __init__(self, win, insert_mode=False):
        Textbox.__init__(self, win, insert_mode)
        self.completion_deferred = Deferred()

    def increment(self, char, validate=None):
        if validate:
            char = validate(char)
            if not char:
                return
        if not self.do_command(char):
            reactor.callLater(0, self.completion_deferred.callback,
                self.gather())
        self.win.refresh()

class Curdle(object):
    """
    Curses logic for a Darklight client.
    """

    textbox = None

    def __init__(self):
        self.client = DarkClient()
        self.screen = curses.initscr()
        curses.start_color()

        max_y, max_x = self.screen.getmaxyx()

        self.status = self.screen.derwin(1, max_x, max_y - 1, 0)
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)

        self.servers = self.screen.derwin(max_y - 3, max_x, 0, 0)

        self.entry = self.screen.derwin(1, max_x, max_y - 2, 0)

    def fileno(self):
        return 0

    def doRead(self):
        c = self.screen.getch()
        if self.textbox:
            self.textbox.increment(c)
        elif c == ord("q"):
            reactor.stop()
        elif c in (ord("\n"), curses.KEY_ENTER):
            d = self.get_string()
            @d.addCallback
            def cb(s):
                host, port = s.split(":")
                d = self.client.add_server(host, int(port))
                d.addCallback(lambda none: self.update_servers())
            @d.addErrback
            def eb(f):
                self.set_status("Couldn't understand you!")
        else:
            log.msg("Unhandled character %d" % c)

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

    def update_servers(self):
        self.servers.clear()
        for i, server in enumerate(self.client.connections):
            self.servers.addstr(i, 0, str(server))
        self.servers.refresh()

    def get_string(self):
        """
        Start a textbox.

        Returns a Deferred which will fire with the result of the textbox.
        """

        self.entry.clear()
        self.entry.refresh()
        self.textbox = AsyncTextbox(self.entry)
        d = self.textbox.completion_deferred
        @d.addCallback
        def cb(s):
            self.textbox = None
            return s
        return d

curdle = Curdle()
curdle.start()
reactor.addReader(curdle)
reactor.run()
