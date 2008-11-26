#!/usr/bin/env python

import zope.interface
import twisted.application.internet
import twisted.application.service
import twisted.plugin
import twisted.python.usage

import darklight.DarkFactory

class Options(twisted.python.usage.Options):
	optParameters =  [
		["port", "p", 56789, "The port to listen on."]
	]

class DarkServiceMaker(object):
	zope.interface.implements(twisted.application.service.IServiceMaker,
		twisted.plugin.IPlugin)
	tapname = "darklight"
	description = "Reference implementation of the Darklight protocol."
	options = Options

	def makeService(self, options):
		return twisted.application.internet.TCPServer(
			int(options["port"]), darklight.DarkFactory())

serviceMaker = DarkServiceMaker()
