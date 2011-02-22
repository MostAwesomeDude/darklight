#!/usr/bin/env python

import base64
import functools
import os.path

import twisted.internet.protocol
import twisted.internet.reactor
import twisted.protocols.basic

from darklight.aux import DarkHMAC, util
from darklight.core import DarkCache, DarkConf, DarkTimer

PASSTHROUGH_PENDING, PASSTHROUGH, AUTHENTICATED = range(3)

class DarkServerProtocol(twisted.protocols.basic.LineReceiver):

    state = PASSTHROUGH_PENDING
    passthrough = None

    def __init__(self):
        print "Protocol created..."
        self.passthrough_pending_lines = []

    def checkapi(self, tokens):
        self.sendLine("API 1")

    def bai(self, tokens):
        self.transport.loseConnection()

    def fail(self, tokens):
        self.transport.loseConnection()

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
            h = util.deserialize(h, 24)
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

    def sendtth(self, tokens):
        """
        SENDTTH <hash>

        The hash is just a TTH hash.
        """

        pass

    def version(self, tokens):
        self.sendLine("Darklight pre-alpha")

    helpers = {
        "BAI": bai,
        "CHECKAPI": checkapi,
        "FAIL": fail,
        "KTHNXBAI": kthnxbai,
        "SENDPEZE": sendpeze,
        "SENDTTH": sendtth,
        "VERSION": version
    }

    def error(self):
        self.sendLine("FAIL")
        self.transport.loseConnection()

    def unknown(self):
        self.sendLine("LOLWUT")
        self.transport.loseConnection()

    def challenge(self, challenge):
        try:
            hai, passphrase = challenge.strip().split(" ", 1)
        except ValueError:
            return False

        if hai != "HAI":
            return False

        hmac = DarkHMAC("test")
        try:
            passphrase = util.deserialize(passphrase, len(hmac))
        except ValueError:
            return False

        if passphrase != hmac:
            return False

        self.state = AUTHENTICATED

        if self.passthrough:
            self.passthrough.master = None
            self.passthrough.transport.loseConnection()

        self.sendLine("OHAI")

        return True

    def dispatch(self, line):
        if self.state != AUTHENTICATED:
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
        if self.state != PASSTHROUGH_PENDING:
            protocol.transport.loseConnection()
            return

        self.passthrough = protocol
        self.passthrough.master = self
        for line in self.passthrough_pending_lines:
            self.passthrough.sendLine(line)

        self.state = PASSTHROUGH
        print "Switched to passthrough mode"

    def connectionMade(self):
        creator = twisted.internet.protocol.ClientCreator(
            twisted.internet.reactor, PassthroughProtocol)
        creator.connectTCP("localhost", 80).addCallback(self.setup_passthrough)

    def connectionLost(self, reason):
        self.passthrough = None

    def lineReceived(self, line):
        print "Received line: %s" % line
        if self.state == PASSTHROUGH_PENDING:
            self.passthrough_pending_lines.append(line)
        elif self.state == PASSTHROUGH:
            # Check HAI first.
            if not self.challenge(line):
                self.passthrough.sendLine(line)
        elif self.state == AUTHENTICATED:
            self.dispatch(line)
        else:
            print "Dead code warning: Impossible self.state value!"

    def sendLine(self, line):
        print "Sending '%s'" % line
        twisted.protocols.basic.LineReceiver.sendLine(self, line)

class PassthroughProtocol(twisted.protocols.basic.LineReceiver):

    master = None

    def lineReceived(self, line):
        self.master.sendLine(line)

    def connectionLost(self, reason):
        if self.master:
            self.master.transport.loseConnection()
