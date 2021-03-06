#!/usr/bin/env python

import os.path

import zope.interface
import twisted.application.internet
import twisted.application.service
import twisted.plugin
import twisted.python.usage

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
        from darklight.core.conf import DarkConf
        from darklight.core.timer import DarkTimer
        from darklight.factory import DarkServerFactory, DarkSSLFactory

        # from twisted.python import log
        # log.PythonLoggingObserver().start()

        timer = DarkTimer("parsing configuration")
        conf = DarkConf()
        conf.read(options["conf"])
        timer.stop()

        if conf.getboolean("ssl", "enabled"):
            return twisted.application.internet.SSLServer(
                int(options["port"]), DarkServerFactory(conf),
                DarkSSLFactory(conf))
        else:
            return twisted.application.internet.TCPServer(
                int(options["port"]), DarkServerFactory(conf))

serviceMaker = DarkServiceMaker()
