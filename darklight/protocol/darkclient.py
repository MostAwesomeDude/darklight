from base64 import b32encode

from twisted.internet.defer import Deferred
from twisted.protocols.stateful import StatefulProtocol
from twisted.python import log

from darklight.aux.hash import DarkHMAC
from darklight.protocol.darkamp import DarkAMP

class DarkClientProtocol(StatefulProtocol):
    """
    Shim protocol which starts up a DL connection for a client.
    """

    def __init__(self, passphrase="test"):
        self.passphrase = passphrase
        self.connected_deferred = Deferred()

    def getInitialState(self):
        return self.ohai, 4

    def ohai(self, data):
        """
        Confirm initial handshake.

        If we succeeded, then this will be exactly four bytes: "OHAI". If
        anything else, then assume the server doesn't like us, and close the
        connection.
        """

        log.msg("data %r" % data)

        if data == "OHAI":
            # Success!
            p = DarkAMP()
            self.transport.protocol = p
            p.makeConnection(self.transport)
            self.connected_deferred.callback(p)
        else:
            # Failure...
            self.transport.loseConnection()

    def connectionMade(self):
        if self.passphrase:
            hmac = b32encode(DarkHMAC(self.passphrase))
            self.transport.write("HAI %s" % hmac)
        else:
            self.transport.write("HAI")
