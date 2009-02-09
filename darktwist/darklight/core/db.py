#!/usr/bin/env python

import os
import pickle
import sys

try:
	import apsw
except ImportError:
	print "Fatal error: Couldn't find APSW module..."
	sys.exit()

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
