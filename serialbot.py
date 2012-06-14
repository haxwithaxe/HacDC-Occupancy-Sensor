
import time
import datetime
import pytty
import json
from util import *
from botutil import *
from config import config as configmod

config = configmod().config
debug = Debug(5,5,'serialbot.log','[%Y/%m/%d %H:%M:%S GMT%z]')
devlog = Debug(5,5,'serial_output.log','[%Y/%m/%d %H:%M:%S GMT%z]')

DEFAULT_INTERVAL=3

class serial:
	def __init__(self):
		cachestr = file2str(config['status_cache'],'r')
		if len(cachestr) > 1:
			cache = json.loads(cachestr)
		else:
			cache = {'changed':0000000000.0,'status':False,'default':'','full':'','raw':'','main_light':0,'hall_light':0,'work_light':0}
			stash(json.dumps(cache))
		self.state = cache
		self.changed = cache['changed'] or time.time()
		self.boolstate = cache['status']
		self.laststate = None
		self.notify = False
		self.die = False
		self.tty = pytty.TTY(config['serial.device'])

	def run(self):
		while not self.die:
			time.sleep(int(config['serial.check_device_every'] or DEFAULT_INTERVAL))
			rawmsg = self.tty.readline()
			debug.send(('serial device said',rawmsg),5)
			try:
				rawmsgdict = json.loads(rawmsg.split('\r\n',1)[0].decode())
			except:
				rawmsgdict = False

			if rawmsgdict and 'main_light' in rawmsgdict and 'work_light' in rawmsgdict and 'hall_light' in rawmsgdict:
				debug.send('DEVICE SAYS: %s' % rawmsg,2)
				self.state = rawmsgdict
				current_boolstate = (0 < (self.state['hall_light'] + self.state['main_light'] + self.state['work_light'])) #+ self.state['main_pir'] + self.state['work_pir']

				if (self.boolstate != current_boolstate and self.laststate != current_boolstate):
					debug.send('OCCSENSOR STATE SET: %s' % current_boolstate)
					self.boolstate = current_boolstate
					self.changed = time.time()
					self.notify = True

					stash(self._get_status_str())

				if self.notify:
					self.notify = False
					self.pushupdate()
				self.laststate = current_boolstate
		# end while
		return

	def _get_status_str(self):
		if self.state == None: return ''
		statusdict = {'changed':self.changed,'status':self.boolstate,'default':config['default_msg_fmt'],'full':config['full_msg_fmt'],'raw':config['raw_msg_fmt']}
		statusdict['default'] = statusdict['default'] % ({True:'open',False:'closed'}[self.boolstate],datetime.datetime.fromtimestamp(self.changed).strftime(config['default_time_fmt']))
		statusdict['full'] = statusdict['full'] % ({True:'open',False:'closed'}[self.state['hall_light']],{True:'open',False:'closed'}[self.state['main_light']],{True:'open',False:'closed'}[self.state['work_light']])
		statusdict['raw'] = statusdict['raw'] % str(self.state)
		status = json.dumps(statusdict)
		debug.send(('_get_status_str status',status),5)
		return status

	def update_cache(self):
		stash(self._get_status_str())

	def pushupdate(self):
		self.update_cache()

	def _die(self):
		self.die = True

if __name__ == '__main__':
	bot = serial()
	bot.run()
