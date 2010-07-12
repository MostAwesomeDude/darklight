#!/usr/bin/env python

import logging
import os.path

import zope.interface
import twisted.application.internet
import twisted.application.service
import twisted.plugin
import twisted.python.log
import twisted.python.usage

from darklight.server import DarkServerFactory

logging.basicConfig(loglevel=logging.DEBUG)

class Options(twisted.python.usage.Options):
    optParameters =  [
        ["conf", "c", None,  "Configuration file."   ],
        ["port", "p", 56789, "The port to listen on."]
    ]

    def postOptions(self):
        if not self['conf']:
            raise twisted.python.usage.UsageError(
                "No configuration file specified.")
        if not os.path.isfile(self['conf']):
            raise twisted.python.usage.UsageError(
                "Could not find configuration file.")

class DarkServiceMaker(object):
    zope.interface.implements(twisted.application.service.IServiceMaker,
        twisted.plugin.IPlugin)
    tapname = "darklight"
    description = "Reference implementation of the Darklight protocol."
    options = Options

    def makeService(self, options):
        twisted.python.log.PythonLoggingObserver().start()

        return twisted.application.internet.TCPServer(
            int(options["port"]), DarkServerFactory(options))

serviceMaker = DarkServiceMaker()
