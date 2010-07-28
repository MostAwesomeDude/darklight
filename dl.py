#!/usr/bin/env python

import twisted.internet.protocol
import twisted.internet.gtk2reactor
twisted.internet.gtk2reactor.install()
import twisted.internet.reactor
import twisted.internet.ssl

import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade

from darklight.client import DarkClientProtocol

gui = gtk.glade.XML("gui.glade")

def error(message):
    dialog = gtk.MessageDialog(main, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR,
        gtk.BUTTONS_OK, message)
    dialog.run()
    dialog.destroy()

server_columns = [
    ("Protocol", str),
    ("Status", str),
]

class ClientLogic(object):

    def __init__(self, gui):
        self.gui = gui

        self.connections = set()
        self.cc = twisted.internet.protocol.ClientCreator(
            twisted.internet.reactor, DarkClientProtocol)

        statusbar = self.gui.get_widget("statusbar")
        self.status_context = statusbar.get_context_id("")
        self.set_status("Welcome to DarkLight!")

        self.setup_servers()

    def quit(self, window, event):
        for connection in self.connections:
            connection.transport.loseConnection()

        twisted.internet.reactor.stop()

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

        self.update_servers()

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

        self.connections.add(protocol)
        d = protocol.hai("test")
        d.addCallback(self.authorized_callback)
        self.update_servers()

    def authorized_callback(self, protocol):
        self.set_status("Authorized successfully!")

        self.update_servers()

    def update_servers(self):
        self.server_list.clear()

        for connection in self.connections:
            l = [str(connection)]
            l.append("Authenticated" if connection.authenticated
                else "Unauthenticated")
            self.server_list.append(l)

logic = ClientLogic(gui)
logic.setup_signals()

main = gui.get_widget("main")
main.show()

twisted.internet.reactor.run()
