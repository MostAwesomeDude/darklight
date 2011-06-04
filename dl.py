#!/usr/bin/env python

import sys

from twisted.internet import gtk2reactor
gtk2reactor.install()

from twisted.internet import reactor
from twisted.python import log
log.startLogging(sys.stdout)

import pygtk
pygtk.require("2.0")
import gtk

from darklight.client import DarkClient

gui = gtk.Builder()
gui.add_from_file("gui.glade")

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

        self.server_popup = self.gui.get_object("server_popup")

        self.client = DarkClient()

        statusbar = self.gui.get_object("statusbar")
        self.status_context = statusbar.get_context_id("")
        self.set_status("Welcome to DarkLight!")

        self.setup_servers()

    def set_status(self, message):
        self.gui.get_object("statusbar").pop(self.status_context)
        self.gui.get_object("statusbar").push(self.status_context, message)

    def setup_servers(self):
        column_names, column_types = zip(*server_columns)
        self.server_list = self.gui.get_object("server_list")
        server_view = self.gui.get_object("server_view")
        server_view.set_model(self.server_list)
        server_view.set_reorderable(True)

        for i, name in enumerate(column_names):
            column = gtk.TreeViewColumn(name)
            cell = gtk.CellRendererText()
            column.pack_start(cell, True)
            column.add_attribute(cell, "text", i)
            server_view.append_column(column)

    def on_main_delete_event(self, window, event):
        for connection in self.client.connections:
            connection.transport.loseConnection()

        reactor.stop()

    def on_connect_clicked(self, widget):
        host = self.gui.get_object("host").get_property("text")
        port = self.gui.get_object("port").get_property("text")

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

        d = self.client.add_server(host, port)
        d.addCallback(self.get_server_info)

    def on_server_mouse_clicked(self, widget, event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            try:
                path, column, cellx, celly = widget.get_path_at_pos(x, y)
                widget.grab_focus()
                widget.set_cursor(path, column, False)
                self.server_popup.popup(None, None, None, event.button,
                    event.time)
            except TypeError:
                pass
            return True

    def on_disconnect_server(self, widget):
        for connection in self.client.connections:
            connection.transport.loseConnection()

        self.update_servers()

    def get_server_info(self, protocol):
        """
        Get info about a server.
        """

        self.update_servers()
        d = protocol.get_remote_info()
        d.addCallback(lambda l: self.update_servers())

    def update_servers(self):
        self.server_list.clear()

        for connection in self.client.connections:
            l = [str(connection)]
            l.append(connection.remote_version)
            l.append(connection.remote_api)
            self.server_list.append(l)

logic = ClientLogic(gui)
logic.gui.connect_signals(logic)

main = gui.get_object("main")
main.show()

reactor.run()
