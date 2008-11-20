import binascii
import os.path
import stat
import sys

import darkdb
import darktimer

DEBUG = True

def error(string):
	print "Error:", string
	sys.exit()

def warning(string):
	print "Warning:", string

def debug(string):
	if DEBUG:
		print "Debug:", string

def makelong(str):
	try:
		return long(str)
	except ValueError:
		warning("Couldn't cast '%s' to long..." % str)

try:
	import tth
except ImportError:
	error("Couldn't find TTH module...")

def checkpath(string):
	path = os.path.normpath(string)
	if not os.path.exists(path):
		error("Path " + path + " does not exist!")

class File:
	"""An object representing a file in the system."""
	_state = {"serial": 0}

	def __init__(self, path):
		self.serial = self._state.get("serial")
		self._state["serial"] += 1
		self.path = os.path.normpath(path)
		s = os.stat(self.path)
		self.size = s[stat.ST_SIZE]
		self.mtime = s[stat.ST_MTIME]
		self.blocksize = 128*1024
		self.dirty = True
		darkdb.DarkDB().verify(self)
		debug("File: " + self.path)

	def info(self):
		return (self.size, self.tth.getroot(), self.dirty)

	def match(self, size, tth):
		if not size and not tth:
			return False
		if size and (size != self.size):
			return False
		if self.dirty:
			self.update()
		if tth and (tth != self.tth.getroot()):
			return False
		return True

	def hash(self):
		darktimer.Darktimer().start("hashing " + self.path)
		self.tth = tth.TTH(thex=False, blocksize=self.blocksize)
		self.tth.buildtree(self.path)
		self.dump()
		darktimer.Darktimer().stop("hashing " + self.path)

	def update(self):
		if not self.dirty:
			return
		self.hash()
		self.dirty = False
		darkdb.DarkDB().update(self)

	def getpiece(self, pnum):
		self.update()
		leaves = self.tth.gettree()
		if pnum < len(leaves[-1]):
			return leaves[-1][pnum]
		else:
			return None

	def getdata(self, pnum):
		self.update()
		offset = self.blocksize*pnum
		if offset < self.size:
			buf = ""
			f = open(self.path, "rb")
			f.seek(offset)
			buf = f.read(self.blocksize)
			f.close()
			return buf
		else:
			return None

	def dump(self):
		debug((self.size, self.tth.getroot()))
		#self.tth.dump()

class Darkcache:
	"""A Borg that manages the cache."""
	_state = {"n": None, "files": [], "pcache": dict(), "phits": dict(),
	"maxsize": 10*1024*1024, "size": 0}

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

	def add(self, arg, dir, path):
		'''This is for os.path.walk()'''
		# Skip . files
		for p in path:
			if p.startswith('.'):
				path.remove(p)
		for file in [os.path.join(dir, i) for i in path]:
			if os.path.isfile(file):
				self.files.append(File(file))

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
		assert file in self.files, "Who decided *you* could have a File?"
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
		darktimer.Darktimer().start("search")
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
		darktimer.Darktimer().stop("search")
		return l
