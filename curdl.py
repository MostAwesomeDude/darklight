#!/usr/bin/env python

import urwid

from twisted.internet import reactor

from darklight.client import DarkClient

class ServerInfo(urwid.Text):

    def __init__(self, server, **kwargs):
        urwid.Text.__init__(self, "", **kwargs)

        self.server = server
        self._update_server_info()

    def _update_server_info(self):
        self.set_text("%s %s %s" %
            (self.server, self.server.remote_version, self.server.remote_api))

palette = [
    ("header", "light green", "default"),
]

server_list = urwid.SimpleListWalker([])
servers = urwid.ListBox(server_list)

client = DarkClient()

statusbar = urwid.Text("Welcome to DarkLight!", align="center")
view = urwid.Frame(servers, footer=urwid.AttrMap(statusbar, "header"))

def connect_to_server(host, port):
    d = client.add_server(host, port)
    d.addCallback(lambda p: server_list.append(ServerInfo(p)))

reactor.callLater(5, connect_to_server, "localhost", 56789)

def exit_on_q(i):
    if i in ("q", "Q"):
        for widget in server_list:
            widget.server.transport.loseConnection()
        raise urwid.ExitMainLoop()

loop = urwid.MainLoop(view, palette, unhandled_input=exit_on_q,
    event_loop=urwid.TwistedEventLoop())
loop.run()
