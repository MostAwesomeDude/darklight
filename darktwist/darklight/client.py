#!/usr/bin/env python

class DarkClientProtocol(twisted.protocols.basic.LineReceiver):

	def __init__(self):
		self.authorized = False
		self.linehandler = None

	def connectionMade(self):
		pass

	def connectionLost(self, reason):
		pass

	def dispatch(self, line):
		try:
			if callable(self.linehandler):
				self.linehandler(line)
			else:
				print "Dispatching '%s'" % line
				tokens = [i.strip() for i in line.split(' ')]
				self.helpers[tokens[0]](self, tokens[1:])
		except KeyError:
			otwerr("Unknown command '%s'" % tokens[0])
			otwerr("Line: %s" % line)
		except ValueError:
			otwerr("Received non-numeric in numeric field.")
			otwerr("Line: %s" % line)

	def authorize(self):
		print "Shaking..."
		self.sendLine("HAI")

	def otwerr(self, message):
		print "On-the-wire error: %s" % message
	def k(self, tokens):
		self.rawbuflen = int(tokens[0])
		self.setRawMode()
	
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
