#!/usr/bin/env python

import twisted.internet.defer
import twisted.internet.protocol

from darklight.client import DarkClientProtocol

class DarkClientFactory(twisted.internet.protocol.ClientFactory):

    protocol = DarkClientProtocol

    new_connection_handler = None

    def __init__(self):
        self.connections = set()
