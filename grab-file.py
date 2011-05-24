#!/usr/bin/env python

import sys

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.python import log
log.startLogging(sys.stdout)

from darklight.client import DarkClient
from darklight.magnet import parse_magnet
from darklight.protocol.darkamp import HazTree, SendPeze
from darklight.tth import TTH

from optparse import OptionParser

parser = OptionParser(usage="Usage: %prog [options] <magnet> <destination>")
parser.add_option("-s", "--server", dest="host", default="localhost")
parser.add_option("-p", "--port", dest="port", type="int", default=56789)

options, args = parser.parse_args()

if not args:
    parser.print_help()
    sys.exit()

magnet, output = args

magnet_dict = parse_magnet(magnet)

client = DarkClient()

@inlineCallbacks
def get_stuff_from_server(p):
    print "Connected, getting server info..."
    yield p.get_remote_info()
    print "Remote server is %s, API version %d" % (p.remote_version,
                                                   p.remote_api)
    tth = TTH.from_size_and_hash(magnet_dict["size"], magnet_dict["hash"])
    while not tth.complete:
        for branch in tth.iter_incomplete_branches():
            d = yield p.callRemote(HazTree, size=branch.size,
                hash=branch.hash)
            tth.extend_branch(branch, d)
            print "Extended %r" % branch
    # Grab each section sequentially.
    tth.update_offsets()
    f = open(output, "wb")
    for branch in tth.iter_branches():
        if branch.is_leaf:
            # Grab the offsets for this leaf.
            print "Grabbing %r" % branch
            offset = 0
            while branch.size > offset:
                d = yield p.callRemote(SendPeze, size=branch.size,
                                       hash=branch.hash, piece=offset)
                f.seek(branch.offset + offset)
                f.write(d["data"])
                offset += 65336
    f.close()
    reactor.stop()

client.add_server(options.host, options.port).addCallbacks(
    get_stuff_from_server, lambda none: reactor.stop())

reactor.run()
