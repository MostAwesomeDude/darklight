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

def connect(widget):
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

    factory = DarkClientFactory()

    twisted.internet.reactor.connectSSL(host, port, factory,
        twisted.internet.ssl.ClientContextFactory())

main = gui.get_widget("main")

gui.signal_connect("on_connect_clicked", connect)

main.show()

twisted.internet.reactor.run()
