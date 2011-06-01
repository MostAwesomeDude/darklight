from twisted.internet.defer import gatherResults, maybeDeferred
from twisted.protocols.amp import AMP, Command, Integer, String, Unicode

class BranchLeafError(Exception):
    """
    You thought I was a branch.

    FYI I am a leaf.
    """

class UnknownHashError(Exception):
    """
    The requested hash could not be found.

    This probably isn't fatal.
    """

class Bai(Command):

    arguments = []
    response = []

    requiresAnswer = False

class CheckAPI(Command):

    arguments = []
    response = [("version", Integer())]

class HazTree(Command):

    arguments = [
        ("hash", String()),
        ("size", Integer()),
    ]
    response = [
        ("first_hash", String()),
        ("first_size", Integer()),
        ("second_hash", String()),
        ("second_size", Integer()),
    ]
    errors = {
        BranchLeafError: "BRANCH_LEAF",
        UnknownHashError: "UNKNOWN_HASH",
    }

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

    def haztree(self, hash, size):
        branch = self.factory.db.find_branch(hash, size)
        if not branch:
            raise UnknownHashError()
        if branch.is_leaf:
            raise BranchLeafError()
        return {
            "first_hash": branch.children[0].hash,
            "first_size": branch.children[0].size,
            "second_hash": branch.children[1].hash,
            "second_size": branch.children[1].size,
        }
    HazTree.responder(haztree)

    def kthnxbai(self):
        self.callRemote(Bai)
        self.transport.loseConnection()
    KThnxBai.responder(kthnxbai)

    def sendpeze(self, hash, size, piece):
        d = maybeDeferred(self.factory.sendpeze, hash, size, piece)
        @d.addCallback
        def cb(data):
            if data is None:
                raise UnknownHashError("Couldn't find hash")
            return {"data": data}
        return d
    SendPeze.responder(sendpeze)

    def version(self):
        return {"version": "Darklight pre-alpha"}
    Version.responder(version)

    def get_remote_info(self):
        """
        Get information about this connection.

        Returns a Deferred which will fire with a tuple of API and version.
        """

        d1 = self.callRemote(CheckAPI)
        @d1.addCallback
        def cb1(d):
            self.remote_api = d["version"]
            return self.remote_api

        d2 = self.callRemote(Version)
        @d2.addCallback
        def cb2(d):
            self.remote_version = d["version"]
            return self.remote_version

        return gatherResults([d1, d2])
