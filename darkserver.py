#!/usr/bin/env python

import base64
import os.path

import twisted.internet.defer
import twisted.internet.protocol
import twisted.internet.reactor

import twisted.protocols.basic

import twisted.python.log

import darkcache
import darkclient
import darkconf
import darklight
import darktimer

class DarkServerProtocol(darklight.DarkProtocol):

	def haz(self, tokens):
		d = twisted.internet.defer.Deferred()
		l = darkcache.Darkcache().search(tokens)
		d.addCallback(lambda f: self.replysearch(l, f))
		self.factory.remotesearch(tokens, d)

	def replysearch(self, files, remotefiles):
		if files != None:
			if len(files) + len(remotefiles):
				l = [i.info() for i in files] + remotefiles
				buf = ["CANHAZ %s" % str(len(l))]
				for data in l:
					buf.append("FILE %s %s" % (str(data[0]), data[1]))
				buf.append("KTHNX")
				self.sendLine(self.delimiter.join(buf))
			else:
				self.sendLine("NOHAZ")
		else:
			self.error()
		return remotefiles

	helpers = {"HAZ": haz}
	helpers.update(darklight.DarkProtocol.helpers)

class DarkServerFactory(twisted.internet.protocol.ServerFactory):
	protocol = DarkServerProtocol

	def fixfactory(self, p):
		print "Fixing factory..."
		p.factory = self
		return p

	def remotesearch(self, request, deferred):
		l = len(darkconf.Darkconf().remotes)
		if l:
			s  = darkclient.DarkSearch(request, l, deferred)
			for (host, port) in darkconf.Darkconf().remotes:
				print "Connecting to %s:%s" % (host, port)
				d = self.clientcreator.connectTCP(host, port)
				d.addCallbacks(lambda p: self.addsearch(p, s),
					lambda f: self.dontsearch(s))
				d.addErrback(twisted.python.log.err)
		else:
			twisted.internet.reactor.callLater(0, deferred.callback, [])

	def addsearch(self, p, s):
		p.purpose = darkclient.PSEARCH
		p.search = s
		p.tasks += 1
		p.handshake()
		return p

	def dontsearch(self, s):
		s.count -= 1
		s.checkcount()

	def conf(self, conffile):
		darktimer.Darktimer().start("parsing configuration")
		darkconf.Darkconf().parse(conffile)
		darktimer.Darktimer().stop("parsing configuration")
		try:
			import darknotify
			d = darknotify.DarkNotify()
			d.start()
			d.add(darkconf.Darkconf().folders)
			print "Started inotify thread..."
		except ImportError:
			print "Couldn't start inotify thread,"
			print "\ttry installing pyinotify."

	def __init__(self):
		self.conf("darklight.conf")
		for folder in darkconf.Darkconf().folders:
			os.path.walk(folder, darkcache.Darkcache().add, None)
		self.clientcreator = twisted.internet.protocol.ClientCreator(
			twisted.internet.reactor, darkclient.DarkClientProtocol)
		if darkconf.Darkconf().immhash:
			twisted.internet.reactor.callInThread(
				darkcache.Darkcache().update)

class DarkService(twisted.application.service.Service):

	def getDarkFactory(self):
		return DarkServerFactory()
