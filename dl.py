#!/usr/bin/env python

import sys

import twisted.internet.protocol
import twisted.internet.gtk2reactor
twisted.internet.gtk2reactor.install()

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import twisted.internet.ssl
from twisted.python import log
log.startLogging(sys.stdout)

import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade

from darklight.protocol.darkclient import DarkClientProtocol

gui = gtk.glade.XML("gui.glade")

def error(message):
    dialog = gtk.MessageDialog(main, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR,
        gtk.BUTTONS_OK, message)
    dialog.run()
    dialog.destroy()

server_columns = [
    ("Protocol", str),
    ("Version", str),
    ("API", str),
]

class ClientLogic(object):

    def __init__(self, gui):
        self.gui = gui

        self.connections = set()
        self.cc = twisted.internet.protocol.ClientCreator(reactor,
            DarkClientProtocol)

        statusbar = self.gui.get_widget("statusbar")
        self.status_context = statusbar.get_context_id("")
        self.set_status("Welcome to DarkLight!")

        self.setup_servers()

    def quit(self, window, event):
        for connection in self.connections:
            connection.transport.loseConnection()

        reactor.stop()

    def set_status(self, message):
        self.gui.get_widget("statusbar").pop(self.status_context)
        self.gui.get_widget("statusbar").push(self.status_context, message)

    def setup_servers(self):
        column_names, column_types = zip(*server_columns)
        self.server_list = gtk.ListStore(*column_types)
        server_view = self.gui.get_widget("server-view")
        server_view.set_model(self.server_list)
        server_view.set_reorderable(True)

        for i, name in enumerate(column_names):
            column = gtk.TreeViewColumn(name)
            cell = gtk.CellRendererText()
            column.pack_start(cell, True)
            column.add_attribute(cell, "text", i)
            server_view.append_column(column)

    def setup_signals(self):
        self.gui.signal_connect("on_main_delete_event", self.quit)

        self.gui.signal_connect("on_connect_clicked", self.connect)

    def connect(self, widget):
        host = self.gui.get_widget("host").get_property("text")
        port = self.gui.get_widget("port").get_property("text")

        if not host:
            error("No host specified!")
            return
        elif not port:
            error("No port specified!")
            return

        try:
            port = int(port)
        except ValueError:
            error("Port must be a number!")
            return

        self.set_status("Connecting to %s:%d" % (host, port))

        d = self.cc.connectTCP(host, port, 5)
        d.addCallback(self.connected_callback)

    def connected_callback(self, protocol):
        self.set_status("Connected successfully!")

        protocol.connected_deferred.addCallback(self.get_server_info)

    def get_server_info(self, protocol):
        """
        Get info about a server.
        """

        log.msg("Getting info")

        self.connections.add(protocol)
        self.update_servers()

    def update_servers(self):
        self.server_list.clear()

        for connection in self.connections:
            l = [str(connection)]
            l.append(connection.remote_version)
            l.append(connection.remote_api)
            self.server_list.append(l)

logic = ClientLogic(gui)
logic.setup_signals()

main = gui.get_widget("main")
main.show()

reactor.run()
