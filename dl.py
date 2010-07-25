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

from darklight.client import DarkClientFactory

gui = gtk.glade.XML("gui.glade")

def error(message):
    dialog = gtk.MessageDialog(main, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR,
        gtk.BUTTONS_OK, message)
    dialog.run()
    dialog.destroy()

class ClientLogic(object):

    def __init__(self):
        self.connections = set()
        self.factory = DarkClientFactory()

        self.factory.new_connection_handler = self.connected_callback

    def setup_signals(self, gui):
        gui.signal_connect("on_connect_clicked", self.connect)

    def connect(self, widget):
        host = gui.get_widget("host").get_property("text")
        port = gui.get_widget("port").get_property("text")

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

        print "Connecting to %s:%d" % (host, port)

        twisted.internet.reactor.connectTCP(host, port, self.factory, 5)

    def connected_callback(self, protocol):
        print "Connected successfully!"

        self.connections.add(protocol)

logic = ClientLogic()
logic.setup_signals(gui)

main = gui.get_widget("main")
main.show()

twisted.internet.reactor.run()
