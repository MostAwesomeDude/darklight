#!/usr/bin/env python

import base64

import twisted.internet.defer
import twisted.protocols.basic

from darklight.aux import DarkHMAC

class DarkClientProtocol(twisted.protocols.basic.LineReceiver):

    def __init__(self):
        self.authenticated = False
        self.linehandler = None
        self.rawhandler = None

    def connectionMade(self):
        print "Made connection!"

    def connectionLost(self, reason):
        print "Lost connection!"

    def dispatch(self, line):
        try:
            if callable(self.linehandler):
                self.linehandler(line)
            else:
                print "Dispatching '%s'" % line
                tokens = [i.strip() for i in line.split(' ')]
                if tokens[0] in self.helpers:
                    self.helpers[tokens[0]](self, tokens[1:])
                else:
                    self.otwerr("Unknown command '%s'" % tokens[0])
                    self.otwerr("Line: %s" % line)
        except ValueError:
            self.otwerr("Received non-numeric in numeric field.")
            self.otwerr("Line: %s" % line)

    def hai(self, passphrase=None):
        print "Shaking..."
        if passphrase:
            hmac = base64.b32encode(DarkHMAC(passphrase))
            self.sendLine("HAI %s" % hmac)
        else:
            self.sendLine("HAI")

        self.authentication_deferred = twisted.internet.defer.Deferred()
        return self.authentication_deferred

    def otwerr(self, message):
        print "On-the-wire error: %s" % message

    def k(self, tokens):
        self.rawbuflen = int(tokens[0])
        self.setRawMode()
    
    def ohai(self, tokens):
        self.authenticated = True

        twisted.internet.reactor.callLater(0,
            self.authentication_deferred.callback, self)

    def lineReceived(self, line):
        self.dispatch(line)

    def rawDataRecieved(self, data):
        self.rawbuf += data
        if len(self.rawbuf) >= self.rawbuflen:
            self.setLineMode(self.rawbuf[self.rawbuflen:])
            self.rawbuf = self.rawbuf[:self.rawbuflen]
            self.rawbuflen = 0
            if callable(self.rawhandler):
                self.rawhandler(self.rawbuf)

    helpers = {"OHAI": ohai}
