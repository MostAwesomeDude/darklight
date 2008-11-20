import os.path

import darkdb
import darkcache

def warning(string):
	print "Warning:", string

class Darkconf:
	"""An object that parses configuration."""
	_state = {"folders": [], "remotes": [], "immhash": False}

	def __init__(self):
		self.__dict__ = self._state

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
					darkcache.Darkcache().setsize(tokens[1])
				elif tokens[0] == "DB":
					darkdb.DarkDB().path = tokens[1]
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
			except (IndexError, ParseError):
				warning("Bad config line:")
				warning("\t%s" % line)