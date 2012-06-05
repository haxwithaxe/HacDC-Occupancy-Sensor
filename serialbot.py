
import time
import threading
import pytty
import json
import comms
from util import *
from botutil import *
from config import config as configmod

config = configmod()
socketdict = config.socketsdict
config = config.config

class serial(threading.Thread):
	def __init__(self):
		cachestr = file2str(config['status_cache'],'r')
		if len(cachestr) > 1:
			cache = json.loads(cachestr)
		else:
			cache = {'changed':'','status':False,'default':'','full':'','raw':''}
			stash(json.dumps(cache))
		self.config = config
		self.con_sock = comms.server(config['serial.console'])
		self.con_sock.start()
		self.socketlist = []
		self.state = None
		self.changed = cache['changed'] or time.strftime(config['change_time_fmt'])
		self.boolstate = cache['status']
		self.laststate = None
		self.notify = False
		self.die = False
		self.tty = pytty.TTY(self.config['serial.device'])
		self.loadsockets()
		threading.Thread.__init__( self )

	def run(self):
		while not self.die:
			time.sleep(1)
			rawmsg = self.tty.readline()
			try:
				rawmsgdict = json.loads(rawmsg.split('\r\n',1)[0].decode())
			except:
				rawmsgdict = None

			if rawmsgdict:
				debug('DEVICE SAYS: %s' % rawmsg)
				self.state = rawmsgdict
				current_boolstate = (0 < (self.state['hall_light'] + self.state['main_light'] + self.state['work_light'])) #+ self.state['main_pir'] + self.state['work_pir']

				if (self.boolstate != current_boolstate and self.laststate != current_boolstate):
					debug('OCCSENSOR STATE SET: %s' % current_boolstate)
					self.boolstate = current_boolstate
					self.changed = time.strftime(config['change_time_fmt'])
					self.notify = True

					stash(self._get_status_str())

				if self.notify:
					self.notify = False
					self.pushupdate()
				self.laststate = current_boolstate
			for sock in self.socketlist:
				if len(sock.msg) > 0:
					for m in sock.msg:
						self._handle_msgs(m)
		# end while
		return

	def _handle_msgs(self,msg):
		if len(str(msg)) < 1: return
		if msg == config['update_flag']:
			self.pushupdate()
		elif msg == config['refresh_flag']:
			self.update_cache()
		return

	def _get_status_str(self):
		if self.state == None: return ''
		statdict = {'changed':self.changed,'status':self.boolstate,'default':config['default_msg_fmt'],'full':config['full_msg_fmt'],'raw':config['raw_msg_fmt']}
		statdict['default'] = statdict['default'] % ({True:'open',False:'closed'}[self.boolstate],time.strptime(self.changed,config['change_time_fmt']).strftime(config['default_time_fmt']))
		statdict['full'] = statdict['full'] % ({True:'open',False:'closed'}[self.state['hall_light']],{True:'open',False:'closed'}[self.state['main_light']],{True:'open',False:'closed'}[self.state['work_light']])
		statusdict['raw'] = statusdict['raw'] % str(self.state)
		return json.dumps(statusdict)

	def update_cache(self):
		str2file(self.config['status_cache'],self._get_status_str())

	def pushupdate(self):
		update_cache()
		for sock in self.socketlist:
				sock.send(self.config['update_flag'])

	def loadsockets(self):
		for sock in socketdict.values():
			self.socketlist += [comms.server(sock)]
			self.socketlist[-1].start()

	def die(self):
		self.die = True
		self._Thread__stop()

if __name__ == '__main__':
	bot = serial()
	bot.start()
