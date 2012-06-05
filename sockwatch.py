import threading
import time

class Watch(threading.Thread):
	def __init__(self,clientobj,socketobj):
		self.sock = socketobj
		self.client = clientobj
		self.die = False
		threading.Thread.__init__(self)

	def run(self):
		while not self.die:
			msgs = self.sock.msg[:]
			self.sock.msg = []
			if len(msgs) > 0:
				self.client.handle_sock_msgs(msgs)
			time.sleep(0.01)

	def die(self):
		self.die = True
		self._Thread__stop()
