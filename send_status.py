#!/usr/bin/env python

from util import *
from botutil import *
from config import config
import urllib,urllib2
import json

conf = config().config
debug = Debug(5,5)

class remote_update(object):
	def get_status(self):
		debug.send('getting status',2)
		statusdict = unstash('dict')
		if statusdict:
			urlargs = urllib.urlencode(statusdict)
		else:
			urlargs = None
		debug.send('got status',2)
		return urlargs

	def send_status(self,urlargs):
		debug.send('sending status',2)
		url = conf['remote_status_cache_url']
		url = '?'.join([url,urlargs])
		debug.send(url,5)
		rep = urllib2.urlopen(url)
		debug.send(rep,5)
		debug.send('sent status',2)

	def update(self):
		debug.send('updating ...',2)
		urlargs = self.get_status()
		if urlargs: self.send_status(urlargs)

	def die(self):
		pass
		
if __name__ == '__main__':
	bot = remote_update()
	bot.update()
	#update_on_change(bot)
