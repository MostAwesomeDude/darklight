#!/usr/bin/env python

import base64
import functools
import os.path

import twisted.internet.protocol
import twisted.internet.reactor
import twisted.protocols.basic

from darklight.core import DarkCache, DarkConf, DarkTimer

# XXX should live somewhere better
def canonicalize_tth(tth):
    if len(tth) == 48:
        return binascii.unhexlify(tth)
    elif len(tth) == 40:
        return base64.b32decode(tth)
    elif len(tth) == 24:
        return tth
    else:
        raise ValueError, "Couldn't guess the TTH format"

class DarkServerProtocol(twisted.protocols.basic.LineReceiver):

    authorized = False
    passthrough = None
    passthrough_pending = True

    def __init__(self):
        print "Protocol created..."
        self.passthrough_pending_lines = []

    def checkapi(self, tokens):
        self.sendLine("API 1")

    def bai(self, tokens):
        self.transport.loseConnection()

    def fail(self, tokens):
        self.transport.loseConnection()

    def hai(self, tokens):
        self.authorized = True
        if self.passthrough:
            self.passthrough.master = None
            self.passthrough.transport.loseConnection()
        self.sendLine("OHAI")

    def kthnxbai(self, tokens):
        self.sendLine("BAI")
        self.bai(tokens)

    def sendpeze(self, tokens):
        """
        SENDPEZE <hash> <size> <piece>

        The hash is some form of TTH hash. The size and piece are ASCII
        decimal.
        """

        try:
            h, size, piece = tokens
            h = canonicalize_tth(h)
            size = int(size)
            piece = int(piece)
        except ValueError:
            self.error()
            return

        l = self.factory.cache.search(h, size)
        if len(l) == 1:
            buf = self.factory.cache.getdata(l[0], piece)
            if not buf:
                print "File buffer was bad..."
                self.error()
                return
            i, sent = 0, 0
            tth = base64.b32encode(self.factory.cache.getpiece(l[0], piece))
            self.sendLine("K %s %s" % (tth, str(len(buf))))
            self.sendLine(buf)
        else:
            self.error()

    def version(self, tokens):
        self.sendLine("Darklight pre-alpha")

    helpers = {"BAI": bai, "CHECKAPI": checkapi, "FAIL": fail, "HAI": hai,
        "KTHNXBAI": kthnxbai, "SENDPEZE": sendpeze, "VERSION": version}

    def error(self):
        self.sendLine("FAIL")
        self.transport.loseConnection()

    def unknown(self):
        self.sendLine("LOLWUT")
        self.transport.loseConnection()

    def authorize(self, challenge):
        if challenge.strip() == "HAI":
            self.authorized = True
        return self.authorized

    def dispatch(self, line):
        if not self.authorized:
            if not self.authorize(line):
                return

        tokens = [i.strip() for i in line.split(' ')]

        try:
            print "Dispatching '%s'" % line
            self.helpers[tokens[0]](self, tokens[1:])
        except KeyError:
            print "Unknown command '%s'" % tokens[0]
            self.unknown()
        #except:
            #print "Error dispatching '%s'" % line
            #self.error()

    def setup_passthrough(self, protocol):
        self.passthrough = protocol
        self.passthrough.master = self
        for line in self.passthrough_pending_lines:
            self.passthrough.sendLine(line)
        self.passthrough_pending = False

    def connectionMade(self):
        creator = twisted.internet.protocol.ClientCreator(
            twisted.internet.reactor, PassthroughProtocol)
        creator.connectTCP("www.google.com", 80).addCallback(self.setup_passthrough)

    def connectionLost(self, reason):
        self.passthrough = None

    def lineReceived(self, line):
        print "Received line: %s" % line
        if self.passthrough_pending:
            self.passthrough_pending_lines.append(line)
        elif self.passthrough:
            self.passthrough.sendLine(line)
        else:
            self.dispatch(line)

    def sendLine(self, line):
        print "Sending '%s'" % line
        twisted.protocols.basic.LineReceiver.sendLine(self, line)

class PassthroughProtocol(twisted.protocols.basic.LineReceiver):

    def lineReceived(self, line):
        self.master.sendLine(line)

    def connectionLost(self, reason):
        if self.master:
            self.master.transport.loseConnection()
