#!/usr/bin/env python

import twisted.internet.defer
import twisted.internet.protocol

from darklight.client import DarkClientProtocol

class DarkClientFactory(twisted.internet.protocol.ClientFactory):

    protocol = DarkClientProtocol

    def __init__(self):
        self.connection = None

    def buildProtocol(self, addr):
        if self.connection:
            print "Tried to create two connections, not supported"
        else:
            self.connection = twisted.internet.protocol.ClientFactory.buildProtocol(self, addr)
            return self.connection
