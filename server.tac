#!/usr/bin/env python

import twisted.application.internet
import twisted.application.service

import darkserver

application = twisted.application.service.Application("darklight")
service = darkserver.DarkService()
twisted.application.internet.TCPServer(56789,
	service.getDarkFactory()).setServiceParent(
	twisted.application.service.IServiceCollection(application))
