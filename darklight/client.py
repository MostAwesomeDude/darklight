from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientCreator

from darklight.protocol.darkclient import DarkClientProtocol

class DarkClient(object):
    """
    I am a client.

    Use me to handle the high-level logic for retrieving things from Darklight
    servers.
    """

    timeout = 10

    def __init__(self):
        self.cc = ClientCreator(reactor, DarkClientProtocol)
        self.connections = set()

    def add_server(self, host, port):
        """
        Connect to a server.

        Returns a Deferred which will fire with the DarkAMP connection on
        success.
        """

        # This one will get us the intermediate client protocol.
        d = self.cc.connectTCP(host, port, self.timeout)

        # This one will eventually fire with the AMP connection.
        rv = Deferred()

        @d.addCallback
        def cb(intermediate):
            d = intermediate.connected_deferred
            # Callback: Success! Add the connection to our pool, and return
            # the AMP connection to the next in line.
            @d.addCallback
            def cb(amp):
                self.connections.add(amp)
                return amp
            # And now chain to our return value, so that it can also fire.
            d.chainDeferred(rv)

        # If the intermediate protocol fails, also fire the errback for our
        # caller.
        d.addErrback(rv.errback)

        return rv
