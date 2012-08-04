DEBUG = True

import json
import threading
import time
import os
from util import *
from config import config as configmod

config = configmod().config

def stash(cachestr):
	str2file(cachestr,config['status_cache'])

def unstash(fmt = 'raw'):
	output = None
	contents = file2str(config['status_cache'])
	if fmt == 'dict':
		if len(contents) > 1:
			output = json.loads(contents)
	else:
		output = contents
	return output

class _update_on_change(threading.Thread):
	def __init__(self,bot):
		self.die = False
		self.bot = bot
		threading.Thread.__init__(self)

	def run(self):
		time.sleep(7)
		last_status = None
		last_mod_time = 0
		while not self.die:
			mod_time = os.path.getmtime(config['status_cache'])
			if last_mod_time and mod_time and (mod_time - last_mod_time) > 0:
				last_mod_time = mod_time
				status = unstash()
				if not last_status: last_status = status
				if last_status != status:
					self.bot.update()
					time.sleep(3)
					last_status = status
			time.sleep(0.1)

	def die(self):
		self.die = True
		self._Thread__stop()

def update_on_change(bot):
	o = _update_on_change(bot)
	o.start()
	return o
