#!/usr/bin/env python

import base64
import binascii
import os

from file import DarkFile
from timer import DarkTimer

def debug(string):
	if True:
		print "Debug:", string

def makelong(str):
	try:
		return long(str)
	except ValueError:
		debug("Couldn't cast '%s' to long..." % str)

class DarkCache:
	"""A Borg that manages the cache."""
	_state = {"n": None, "files": [], "pcache": dict(), "phits": dict(),
	"maxsize": 10*1024*1024, "size": 0}

	n = None
	files = None
	pcache = None
	phits = None
	maxsize = None
	size = None

	def __init__(self):
		self.__dict__ = self._state

	def __iter__(self):
		return iter(self.files)

	def dump(self):
		debug("Cache size: " + str(self.size))
		debug("Cache maxsize: " + str(self.maxsize))

	def setsize(self, size):
		self.maxsize = int(size)
		while self.size > self.maxsize:
			for f in self.files:
				if f.size > self.maxsize and self.iscached(f):
					self.uncache(f)

	def add(self, blah, dir, path):
		'''This is for os.path.walk()'''
# Skip . files
		for p in path:
			if p.startswith('.'):
				path.remove(p)
		for f in [os.path.join(dir, i) for i in path]:
			if os.path.isfile(f):
				self.files.append(DarkFile(f))

	def update(self):
		[f.update() for f in self.files]

	def iscached(self, piece):
		return self.pcache.has_key(piece)

	def precache(self, piece, data):
# Already cached?
		if self.iscached(file):
			return
# Too big to fit into cache?
		if len(data) + self.size >= self.maxsize:
			return
		self.pcache[piece] = data
		self.size += len(self.pcache[piece])

	def uncache(self, piece):
		if not self.iscached(file):
			return
		self.size -= len(self.pcache[piece])
		del self.pcache[piece]

	def getpiece(self, file, pnum):

		return file.getpiece(pnum)

	def getdata(self, file, pnum):
		assert file in self.files, "Who decided *you* could have a DarkFile?"
		piece = file.getpiece(pnum)
		if not piece:
# OOB?
			return None
		if self.iscached(piece):
			return self.pcache[piece]
		else:
			data = file.getdata(pnum)
			self.precache(piece, data)
			return data

	def search(self, tokens):
		DarkTimer().start("search")
		l = []
		tth = size = None
		for token in tokens:
			if len(token) == 48:
				tth = binascii.unhexlify(token)
			elif len(token) == 40:
				tth = base64.b32decode(token)
			elif len(token) == 24:
				tth = token
			elif not len(token):
				continue
			else:
				size = makelong(token)
				if not size:
					return None
		for f in self.files:
			if f.match(size, tth):
				l.append(f)
		DarkTimer().stop("search")
		return l