#!/usr/bin/env python

import os.path

import zope.interface
import twisted.application.internet
import twisted.application.service
import twisted.plugin
import twisted.python.usage

from darklight.server import DarkServerFactory

class Options(twisted.python.usage.Options):
    optParameters =  [
        ["conf", "c", None,  "Configuration file."   ],
        ["port", "p", 56789, "The port to listen on."]
    ]

    def postOptions(self):
        if self['conf'] and not os.path.isfile(self['conf']):
            raise twisted.python.usage.UsageError, "Bad conf file."

class DarkServiceMaker(object):
    zope.interface.implements(twisted.application.service.IServiceMaker,
        twisted.plugin.IPlugin)
    tapname = "darklight"
    description = "Reference implementation of the Darklight protocol."
    options = Options

    def makeService(self, options):
        return twisted.application.internet.TCPServer(
            int(options["port"]), DarkServerFactory(options))

serviceMaker = DarkServiceMaker()
