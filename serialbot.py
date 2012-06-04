
import time
import threading
import pytty
import json
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
			cache = {'since':'Wed, Jan 01 at 12:00 AM','status':False,'default':'','full':'','raw':''}
			stash(json.dumps(cache))
		self.config = config
		self.socketlist = []
		self.state = None
		self.since = cache['since']
		self.boolstate = cache['status']
		self.laststate = None
		self.notify = False
		self.stopnow = False
		self.tty = pytty.TTY(self.config['serial.device'])
		threading.Thread.__init__( self )

	def run(self):
		while not self.stopnow:
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
					self.since = time.strptime('%s').strftime('%a, %b %d at %I:%M %p')
					self.notify = True

					stash(self._get_status_str())

				if self.notify and self.bot:
					self.notify = False
					self.pushupdate()
				self.laststate = current_boolstate
		# end while
		return

	def _get_status_str(self):
		statdict = {'since':self.since,'status':self.boolstate,'default':self.config['default_msg_fmt'],'full':self.config['full_msg_fmt'],'raw':self.config['raw_msg_fmt']}
		statdict['default'] = statdict['default'] % ({True:'open',False:'closed'}[self.boolstate],time.strptime(self.since,self.config['stash_time_fmt']).strftime(self.config['default_time_fmt']))
		statdict['full'] = statdict['full'] % ({True:'open',False:'closed'}[self.state['hall_light']],{True:'open',False:'closed'}[self.state['main_light']],{True:'open',False:'closed'}[self.state['work_light']])
		statusdict['raw'] = statusdict['raw'] % str(self.state)
		return json.dumps(statusdict)

	def pushupdate(self):
		str2file(self.config['status_cache'],self._get_status_str())
		for sock in self.socketlist:
				sock.send(self.config['update_flag'])

	def loadsockets(self):
		for sock in socketdict.values():
			self.socketlist += [comms.server(sock)]

	def die(self):
		self.stopnow = True
		self._Thread__stop()

if __name__ == '__main__':
	bot = serial()
	bot.start()
