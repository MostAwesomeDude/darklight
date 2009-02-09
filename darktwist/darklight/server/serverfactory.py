#!/usr/bin/env python

import os

import twisted.internet.protocol

from darklight.core import DarkCache, DarkConf, DarkTimer

from serverprotocol import DarkServerProtocol

class DarkServerFactory(twisted.internet.protocol.ServerFactory):
	protocol = DarkServerProtocol

	def conf(self, conf):
		DarkTimer().start("parsing configuration")
		# DarkConf().parse(conf)
		DarkConf().update(conf)
		DarkTimer().stop("parsing configuration")
		try:
			# XXX stopgap
			raise ImportError
			d = DarkNotify()
			d.start()
			d.add(DarkConf().folders)
			print "Started inotify thread..."
		except (ImportError, NameError):
			print "Couldn't start inotify thread,"
			print "\ttry installing pyinotify."

	def __init__(self, opts):
		self.conf(opts)
		for folder in DarkConf().folders:
			os.path.walk(folder, DarkCache().add, None)
		if DarkConf().immhash:
			twisted.internet.reactor.callInThread(
				DarkCache().update)
