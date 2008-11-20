import Queue

import twisted.internet.defer
import twisted.internet.protocol
import twisted.internet.reactor

import twisted.protocols.basic

import darkconf
import darklight

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

class DarkClientProtocol(darklight.DarkProtocol):

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
	helpers.update(darklight.DarkProtocol.helpers)
