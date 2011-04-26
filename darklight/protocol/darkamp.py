from twisted.internet.defer import gatherResults, maybeDeferred
from twisted.protocols.amp import AMP, Command, Integer, String, Unicode

class Bai(Command):

    arguments = []
    response = []

    requiresAnswer = False

class CheckAPI(Command):

    arguments = []
    response = [("version", Integer())]

class KThnxBai(Command):

    arguments = []
    response = []

    requiresAnswer = False

class SendPeze(Command):

    arguments = [
        ("hash", String()),
        ("size", Integer()),
        ("piece", Integer()),
    ]
    response = [
        ("hash", String()),
        ("data", String()),
    ]

class Version(Command):

    arguments = []
    response = [("version", Unicode())]

class DarkAMP(AMP):

    remote_version = "Unknown"
    remote_api = "Unknown"

    def bai(self):
        self.transport.loseConnection()
    Bai.responder(bai)

    def checkapi(self):
        return {"version": 2}
    CheckAPI.responder(checkapi)

    def kthnxbai(self):
        self.callRemote(Bai)
        self.transport.loseConnection()
    KThnxBai.responder(kthnxbai)

    def sendpeze(self, hash, size, piece):
        return maybeDeferred(self.factory.getpeze(hash, size, piece))
    SendPeze.responder(sendpeze)

    def version(self):
        return {"version": "Darklight pre-alpha"}
    Version.responder(version)

    def get_remote_info(self):
        d1 = self.callRemote(CheckAPI)
        def cb1(d):
            self.remote_api = d["version"]
        d1.addCallback(cb1)

        d2 = self.callRemote(Version)
        def cb2(d):
            self.remote_version = d["version"]
        d2.addCallback(cb2)

        return gatherResults([d1, d2])
