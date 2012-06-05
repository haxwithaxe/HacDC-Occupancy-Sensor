import sys
import time
import socket
import threading

maxconnectfail = 10
max_msg_buffer = 1000

def _bool_invert(boolval):
	if boolval:
		return False
	else:
		return True

class comm_sock(threading.Thread):
	def __init__(self, address):
		self.sock = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
		self.address = address
		self.die = False
		self.msg = []
		threading.Thread.__init__(self)

	def _send(self, msg):
		self.conn.send(msg)

	def _receve(self):
		msg = self.conn.recv(1024)
		return msg

	def _connect(self):
		return False

	def run(self):
		if not self._connect():
			print('Failed to _connect to '+str(self.address))
			return False
		while not self.die:
			new_msg = self._receve()
			if new_msg not in (-1,'',None):
				if len(self.msg) > max_msg_buffer:
					self.msg.pop(0)
				self.msg += [new_msg]

	def clear_msg(self):
		self.msg = []

	def die(self):
		self.sock.shutdown()
		self.die = True

class client(comm_sock):
	def _connect(self):
		fail = True # pesimism this is not :P
		failcount = 0
		while fail:
			try:
				self.sock.connect(self.address)
				self.conn = self.sock
				fail = False
			except Exception as se:
				if failcount < maxconnectfail:
					failcount += 1
				else:
					break
				time.sleep(5)
		return _bool_invert(fail)

class server(comm_sock):
	def _connect(self):
		try:
			self.sock.bind(self.address)
			self.sock.listen(1)
			self.conn, self.addr = self.sock.accept()
		except Exception as se:
			print('Exception when attempting to setup server socket',se)
			return False
		return True
