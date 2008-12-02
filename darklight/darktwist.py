#!/usr/bin/env python

import base64
import os.path
import Queue

import twisted.application.service

import twisted.internet.defer
import twisted.internet.protocol
import twisted.internet.reactor

import twisted.protocols.basic

import twisted.python.log

from darklight.core import DarkCache, DarkConf, DarkTimer

class DarkProtocol(twisted.protocols.basic.LineReceiver):

	def __init__(self):
		self.authorized = False

	def checkapi(self, tokens):
		self.sendLine("API 1")

	def bai(self, tokens):
		self.transport.loseConnection()

	def fail(self, tokens):
		self.transport.loseConnection()

	def hai(self, tokens):
		self.authorized = True
		self.sendLine("OHAI")

	def kthnxbai(self, tokens):
		self.sendLine("BAI")
		self.bai(tokens)

	def sendpeze(self, tokens):
		if not int(tokens[0]) >= 0:
			self.error()
			return
		l = DarkCache().search(tokens[0:-1])
		if l and len(l) == 1:
			pnum = long(tokens[-1])
			buf = DarkCache().getdata(l[0], pnum)
			if not buf:
				print "File buffer was bad..."
				self.error()
				return
			i, sent = 0, 0
			tth = base64.b32encode(DarkCache().getpiece(l[0], pnum))
			self.sendLine("K %s %s" % (tth, str(len(buf))))
			self.sendLine(buf)
		else:
			self.error()

	def version(self, tokens):
		self.sendLine("Darklight pre-alpha")

	helpers = {"BAI": bai, "CHECKAPI": checkapi, "FAIL": fail, "HAI": hai,
		"KTHNXBAI": kthnxbai, "SENDPEZE": sendpeze, "VERSION": version}

	def error(self):
		self.sendLine("FAIL")
		self.transport.loseConnection()

	def unknown(self):
		self.sendLine("LOLWUT")
		self.transport.loseConnection()

	def authorize(self, challenge):
		if challenge.strip() == "HAI":
			self.authorized = True
		return self.authorized

	def dispatch(self, line):
		if not self.authorized:
			if not self.authorize(line):
				return

		tokens = [i.strip() for i in line.split(' ')]

		try:
			print "Dispatching '%s'" % line
			self.helpers[tokens[0]](self, tokens[1:])
		except KeyError:
			print "Unknown command '%s'" % tokens[0]
			self.unknown()
		#except:
			#print "Error dispatching '%s'" % line
			#self.error()

	def lineReceived(self, line):
		self.dispatch(line)

	def sendLine(self, line):
		print "Sending '%s'" % line
		twisted.protocols.basic.LineReceiver.sendLine(self, line)
class DarkServerProtocol(DarkProtocol):

	def haz(self, tokens):
		d = twisted.internet.defer.Deferred()
		l = DarkCache().search(tokens)
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
	helpers.update(DarkProtocol.helpers)

class DarkServerFactory(twisted.internet.protocol.ServerFactory):
	protocol = DarkServerProtocol

	def fixfactory(self, p):
		print "Fixing factory..."
		p.factory = self
		return p

	def remotesearch(self, request, deferred):
		l = len(DarkConf().remotes)
		if l:
			s  = darkclient.DarkSearch(request, l, deferred)
			for (host, port) in DarkConf().remotes:
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
		DarkConf().parse(conffile)
		try:
			import darknotify
			d = darknotify.DarkNotify()
			d.start()
			d.add(DarkConf().folders)
			print "Started inotify thread..."
		except ImportError:
			print "Couldn't start inotify thread,"
			print "\ttry installing pyinotify."

	def __init__(self):
		for folder in DarkConf().folders:
			os.path.walk(folder, DarkCache().add, None)
		self.clientcreator = twisted.internet.protocol.ClientCreator(
			twisted.internet.reactor, DarkClientProtocol)
		if DarkConf().immhash:
			twisted.internet.reactor.callInThread(
				DarkCache().update)

class DarkService(twisted.application.service.Service):

	def getDarkFactory(self):
		return DarkServerFactory()

(PSEARCH, PPIECE) = range(2)

class Darktask:

	def __init__(self):
		pass

class DarkSearch(Darktask):

	def __init__(self, request, count, deferred):
		self.files = []
		self.request = request
		self.count = count
		self.deferred = deferred

	def checkcount(self):
		if self.count <= 0:
			print "Finished with %d files!" % len(self.files)
			twisted.internet.reactor.callLater(0, self.deferred.callback,
				self.files)

class DarkClientProtocol(DarkProtocol):

	def __init__(self):
		self.authorized = True
		self.rawbuf = ""
		self.rawbuflen = 0
		self.tasks = 0
		self.rawhandler = None
		self.linehandler = None

	def connectionMade(self):
		self.filespending = 0

	def connectionLost(self, reason):
		self.finishsearch()

	def dispatch(self, line):
		try:
			if callable(self.linehandler):
				self.linehandler(line)
			else:
				darklight.DarkProtocol.dispatch(self, line)
		except ValueError:
			otwerr("Received non-numeric in numeric field.")
			otwerr("Line: %s" % line)

	def checktasks(self):
		self.tasks -= 1
		if self.tasks < 1:
			self.sendLine("KTHNXBAI")

	def finishsearch(self):
		try:
			self.search.count -= 1
			self.search.checkcount()
			self.search = None
		except:
			pass
		self.checktasks()

	def handshake(self):
		print "Shaking..."
		self.sendLine("HAI")

	def otwerr(self, message):
		print "On-the-wire error: %s" % message

	def canhaz(self, tokens):
		self.filespending = int(tokens[0])

	def file(self, tokens):
		size = int(tokens[0])
		self.search.files.append((size, tokens[1]))
		self.filespending -= 1

	def k(self, tokens):
		self.rawbuflen = int(tokens[0])
		self.setRawMode()

	def kthnx(self, tokens):
		if self.filespending < 0:
			otwerr("Overrun: Received %d extra files"
				% abs(self.filespending))
		elif self.filespending > 0:
			otwerr("Underrun: Missing %d files" % self.filespending)
		self.finishsearch()

	def nohaz(self, tokens):
		self.finishsearch()

	def ohai(self, tokens):
		request = " ".join(self.search.request)
		self.sendLine("HAZ %s" % request)

	def rawDataRecieved(self, data):
		self.rawbuf += data
		if len(self.rawbuf) >= self.rawbuflen:
			self.setLineMode(self.rawbuf[self.rawbuflen:])
			self.rawbuf = self.rawbuf[:self.rawbuflen]
			self.rawbuflen = 0
			if callable(self.rawhandler):
				self.rawhandler(self.rawbuf)

	helpers = {"FILE": file, "CANHAZ": canhaz, "KTHNX": kthnx,
		"NOHAZ": nohaz, "OHAI": ohai}
	helpers.update(DarkProtocol.helpers)
