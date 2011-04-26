import base64

from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString
from twisted.internet.protocol import Protocol
from twisted.protocols.portforward import ProxyClientFactory
from twisted.python import log

from darklight.aux import util
from darklight.aux.hash import DarkHMAC
from darklight.protocol.darkamp import DarkAMP

PASSTHROUGH_PENDING, PASSTHROUGH, AUTHENTICATED = range(3)

class DarkServerProtocol(Protocol):
    """
    Shim protocol for servers.
    """

    peer = None
    buf = ""

    def __init__(self, endpoint):
        self.endpoint = endpoint
        print "Protocol created..."

    def challenge(self, challenge):
        log.msg("Challenged: %s" % challenge)

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

        self.transport.write("OHAI")

        return True

    def connectionMade(self):
        pcf = ProxyClientFactory()
        pcf.setServer(self)
        d = self.endpoint.connect(pcf)
        d.addErrback(lambda failure: self.transport.loseConnection())

        self.transport.pauseProducing()

    def setPeer(self, peer):
        # Our proxy passthrough has succeeded, so we will be seeing data
        # coming through shortly.
        log.msg("Established passthrough")
        self.peer = peer

    def dataReceived(self, data):
        self.buf += data

        # Examine whether we have received a HAI.
        if (("HAI".startswith(self.buf) or self.buf.startswith("HAI")) and
            self.challenge(self.buf)):
            # Excellent; change protocol.
            p = DarkAMP()
            self.transport.protocol = p
            p.makeConnection(self.transport)
        elif self.peer:
            # Well, go ahead and send it through.
            self.peer.transport.write(data)
