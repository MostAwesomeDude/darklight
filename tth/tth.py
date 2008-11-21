# Copyright 2008 Corbin Simpson
# <cds@corbinsimpson.com>
# This code is provided under the terms of the GNU Public License, version 3.

import base64
import math

import tiger

class TTH:
	"""A class describing a Tiger Tree Hash tree."""

	def __init__(self, file=None, thex=True, maxlevels=0, blocksize=1024):
		self.inited = False
		self.thex = thex
		self.maxlevels = maxlevels
		if self.thex:
			self.blocksize = 1024
		else:
			self.blocksize = blocksize
		if file:
			self.buildtree(file)

	def buildtree(self, f):
		"""Build the tree."""

		if self.inited:
			return

		h = open(f, "rb")
		leaves = []
		# Need to read once, to figure out if file's empty.
		# This part is really lame.
		buf = h.read(self.blocksize)
		if not len(buf):
			if self.thex:
				leaves.append(tiger.tiger("\x00").digest())
			else:
				leaves.append(tiger.tiger("").digest())
		else:
			while len(buf):
				if self.thex:
					buf = '\x00' + buf
				leaves.append(tiger.tiger(buf).digest())
				buf = h.read(self.blocksize)

		h.close()

		self.levels = int(math.ceil(math.log(len(leaves),2)))
		self.level = [leaves]

		for i in range(self.levels):
			l = []

			for j in range(len(self.level[i])):

				if j % 2:
					continue
	
				try:
					buf = self.level[i][j] + self.level[i][j+1]
					if self.thex:
						buf = '\x01' + buf
					l.append(tiger.tiger(buf).digest())
				except IndexError:
					l.append(self.level[i][j])

			self.level.append(l)

		self.level.reverse()
		if self.maxlevels:
			del self.level[self.maxlevels:]

		self.inited = True

	def gettree(self):
		if self.inited:
			return self.level

	def getroot(self):
		if self.inited:
			return base64.b32encode(self.level[0][0])

	def dump(self):
		print "Levels:", len(self.level)
		for i in range(len(self.level)):
			print "Level", i, ":", [base64.b32encode(j) for j in self.level[i]]
