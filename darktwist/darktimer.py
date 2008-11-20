import time

class Darktimer:
	_state = {"clocks": dict(), "timeouts": dict()}

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
