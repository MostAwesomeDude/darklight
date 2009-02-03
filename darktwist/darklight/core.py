import base64
import binascii
import os
import os.path
import pickle
import stat
import sys
import time

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
	import apsw
except ImportError:
	error("Couldn't find APSW module...")

try:
	import tth
except ImportError:
	error("Couldn't find TTH module...")

def checkpath(string):
	path = os.path.normpath(string)
	if not os.path.exists(path):
		error("Path " + path + " does not exist!")

class DarkFile:
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
		DarkDB().verify(self)
		debug("DarkFile: " + self.path)

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
		DarkTimer().start("hashing " + self.path)
		self.tth = tth.TTH(thex=False, blocksize=self.blocksize)
		self.tth.buildtree(self.path)
		self.dump()
		DarkTimer().stop("hashing " + self.path)

	def update(self):
		if not self.dirty:
			return
		self.hash()
		self.dirty = False
		DarkDB().update(self)

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

class DarkConf:
	"""An object that parses configuration."""
	_state = {"folders": [], "remotes": [], "immhash": False}

	folders = None
	remotes = None
	immhash = None

	def __init__(self):
		self.__dict__ = self._state

	def update(self, opts):
		if opts['conf']:
			self.parse(opts['conf'])

	def parse(self, path):
		f = open(os.path.normpath(path))
		for line in f.readlines():
			try:
				if line.startswith("#"):
					continue
				tokens = [i.strip() for i in line.split(' ')]
				if tokens[0] == "FOLDER":
					path = os.path.normpath(tokens[1])
					if os.path.exists(path):
						self.folders.append(path)
					else:
						warning("Path %s does not exist!" % path)
				elif tokens[0] == "CACHE":
					DarkCache().setsize(tokens[1])
				elif tokens[0] == "DB":
					DarkDB().path = tokens[1]
				elif tokens[0] == "REMOTE":
					try:
						self.remotes.append((tokens[1], int(tokens[2])))
					except IndexError:
						self.remotes.append((tokens[1], 56789))
				elif tokens[0] == "HASHSTYLE":
					# "immediate"
					if tokens[1].startswith("imm"):
						self.immhash = True
				else:
					warning("Unknown config line, skipping:")
					warning("\t%s" % line)
			except IndexError:
				warning("Bad config line:")
				warning("\t%s" % line)

class DarkDB:
	_state = {"path": "darklight.db", "handle": None}

	path = None
	handle = None

	def __init__(self):
		self.__dict__ = self._state

	def initdb(self):
		handle = apsw.Connection(self.path)
		cursor = handle.cursor()
		cursor.execute("create table files(serial primary key, path, size, mtime, tth blob)")
		handle.close()

	def connect(self):
		if self.handle:
			return True
		if not self.path:
			return False
		if not os.path.exists(self.path):
			self.initdb()
		self.handle = apsw.Connection(self.path)
		return True

	def update(self, file):
		if not self.connect():
			return
		cursor = self.handle.cursor()
		cursor.execute("select * from files where path=?", (file.path,))
		temp = [i for i in cursor]
		buf = buffer(pickle.dumps(file.tth, 1))
		if len(temp) == 0:
			cursor.execute("insert into files values (null,?,?,?,?)", (file.path, file.size, file.mtime, buf))
		else:
			cursor.execute("update files set size=?, mtime=?, tth=? where path=?", (file.size, file.mtime, buf, file.path))

	def verify(self, file):
		if not self.connect():
			return None
		cursor = self.handle.cursor()
		cursor.execute("select * from files where path=?", (file.path,))
		temp = [i for i in cursor]
		if len(temp) == 0:
			return
		oldfile = temp[0]
		if (oldfile[2] != file.size) or (oldfile[3] != file.mtime):
			cursor.execute("update files set size=?, mtime=? where path=?",
				(file.size, file.mtime, file.path))
			file.dirty = True
		else:
			file.tth = pickle.loads(oldfile[4])
			file.dirty = False

try:
	import pyinotify

	class DarkEvent(pyinotify.ProcessEvent):
	
		def process_IN_CREATE(self, event):
			path = os.path.join(event.path, event.name)
			twisted.internet.reactor.callFromThread(
				darkcache.DarkCache().folders.append, darkcache.DarkFile(path))
	
		def process_IN_DELETE(self, event):
			pass

	class DarkNotify:
		_state = {"n": None, "wm": pyinotify.WatchManager()}
	
		mask = (pyinotify.EventsCodes.IN_CREATE |
			pyinotify.EventsCodes.IN_DELETE)
	
		def __init__(self):
			self.__dict__ = self._state
	
		def start(self):
			self.n = pyinotify.ThreadedNotifier(self.wm, DarkEvent())
			self.n.setDaemon(True)
			self.n.start()
	
		def add(self, folders):
			print self.wm.add_watch(folders, mask, rec=True,
				auto_add=True)
	
		def stop(self):
			self.n.stop()
except ImportError:
	pass

class DarkTimer:
	_state = {"clocks": dict(), "timeouts": dict()}

	clocks = None
	timeouts = None

	def __init__(self):
		self.__dict__ = self._state

	def start(self, string):
		self.clocks[string] = time.time()

	def stop(self, string):
		elapsed = time.time() - self.clocks.get(string)
		print "Timer:", string, "finished in %.6f seconds" % elapsed

	def timeout(self, string, count):
		self.timeouts[string] = time.time() + count

	def checktime(self, string):
		return bool(self.timeouts[string] - self.clocks.get(string))
