DEBUG = True

import json
import threading
from util import *
from config import config as configmod

config = configmod().config

def stash(cachestr):
	str2file(config['status_cache'],cachestr)

def unstash(fmt = 'raw'):
	contents = file2str(config['status_cache'])
	if fmt == 'dict' and len(contents) > 1:
		output = json.loads(contents)
	else:
		output = contents
	return output

class _update_on_change(threading.Thread):
	def __init__(self,bot):
		self.die = False
		self.bot = bot
		self.sock = self.bot.sock
		threading.Thread.__init__(self)

	def run(self):
		while not self.die:
			msg = self.sock.msg[:]
			if config['update_flag'] in [x.strip() for x in msg]:
				self.bot.update()
	def die(self):
		self.die = True
		self._Thread__stop()

def update_on_change(bot):
	o = _update_on_change(bot)
	o.start()
	return o
