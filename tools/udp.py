#!/usr/bin/env python2
import socket
import struct
import sys

class McastSocket(socket.socket):
	def __init__(self, local_port):
		socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM)
		self._mcast_send_grp = ('224.0.0.42', local_port)
		self._mcast_recv_grp = '224.0.0.42'
		self._mcast_recv_addr = ('', local_port)
		self._ttl = struct.pack('b',1)
		self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		if hasattr(socket, "SO_REUSEPORT"):
			self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		self.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self._ttl)
	def mcast_send(self, msg='hello'):
		self.sendto(str(msg), self._mcast_send_grp)
	def mcast_recv(self):
		self.bind(self._mcast_recv_addr)
		grp = socket.inet_aton(self._mcast_recv_grp)
		mreq = struct.pack('=4sl', grp, socket.INADDR_ANY)
		self.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		self._mcast_recv_loop()
	def _mcast_recv_loop(self):
		while True:
			data, src_addr = self.recvfrom(1024)
			print(str(src_addr)+str(data))
			self.sendto('ack',src_addr)

class UDPSocket(socket.socket):
	def __init__(self, local_addr=None, local_port=5606):
		socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM)
		self._local_port = local_port
		self._dest_port = 5606
		self._local_addr = local_addr or ''
		self._local_grp = (self._local_addr, self._local_port)
		self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		if hasattr(socket, "SO_REUSEPORT"):
			self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
	def mysend(self, msg='hello', addr='127.0.0.1'):
		print(str(msg), str(addr), str(self._dest_port))
		self.sendto(str(msg), (addr, self._dest_port))
	def myrecv(self):
		self.bind(self._local_grp)
		self._myrecv_loop()
	def _myrecv_loop(self):
		while True:
			data, src_addr = self.recvfrom(1024)
			print(str(src_addr)+str(data))
			self.sendto('ack',src_addr)

def usage():
	usage_str = '''
	udp.py [-m] [-d] -r|-s <msg>
	-m multicast
	-d desination IPv4 IP
	-r receive
	-s <msg> send message <msg>
	'''


if __name__ == '__main__':
	udp = None
	udp_mcast = None
	if '-h' in sys.argv or '--help' in sys.argv or len(sys.argv) < 1:
		usage()
		sys.exit(1)

	if '-m' in sys.argv:
		udp_mcast = McastSocket(local_port=5606)
	else:
		udp = UDPSocket(local_port=5606)

	if '-r' in sys.argv:
		print('receiving ...')
		if udp_mcast: udp_mcast.mcast_recv()
		if udp: udp.myrecv()
	if '-s' in sys.argv:
		sa = sys.argv.index('-s')
		msg = ' '.join(sys.argv[(sa+1):])
		if udp_mcast: udp_mcast.mcast_send(msg=msg)
		if udp:
			if '-d' in sys.argv:
				ai = sys.argv.index('-d')
				addr = sys.argv[ai+1]
				udp.mysend(msg=msg,addr=addr)
			else:
				udp.mysend(msg=msg)
