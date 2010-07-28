#!/usr/bin/env python

import twisted.protocols.basic

class DarkClientProtocol(twisted.protocols.basic.LineReceiver):

    def __init__(self):
        self.authorized = False
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
                self.helpers[tokens[0]](self, tokens[1:])
        except KeyError:
            self.otwerr("Unknown command '%s'" % tokens[0])
            self.otwerr("Line: %s" % line)
        except ValueError:
            self.otwerr("Received non-numeric in numeric field.")
            self.otwerr("Line: %s" % line)

    def authorize(self):
        print "Shaking..."
        self.sendLine("HAI")

    def otwerr(self, message):
        print "On-the-wire error: %s" % message

    def k(self, tokens):
        self.rawbuflen = int(tokens[0])
        self.setRawMode()
    
    def ohai(self, tokens):
        self.authorized = True

    def rawDataRecieved(self, data):
        self.rawbuf += data
        if len(self.rawbuf) >= self.rawbuflen:
            self.setLineMode(self.rawbuf[self.rawbuflen:])
            self.rawbuf = self.rawbuf[:self.rawbuflen]
            self.rawbuflen = 0
            if callable(self.rawhandler):
                self.rawhandler(self.rawbuf)

    helpers = {"OHAI": ohai}
