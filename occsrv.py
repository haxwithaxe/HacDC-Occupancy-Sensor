#!/usr/bin/env python3

import sys
import threading
import hacdc_ircbot
import tweetbot
import serialbot
from util import *
from botutil import *

class service(threading.Thread):
	def __init__(self):
		self._init_irc()
		self._init_twitter()
		self._init_serial()
		threading.Thread.__init__(self)

	def _init_irc(self):
		self.ircbot = hacdc_ircbot.HacDCBot()
		return

	def _init_twitter(self):
		self.tweeter = tweetbot.tweeter()
		return

	def _init_serial(self):
		self.serialbot = serialbot.serial()
		return

	def cli(self):
		while True:
			line = raw_input().strip()
			if len(line) > 0:
				cmd = line.split()[0].strip()
				if cmd == 'say':
					self.ircbot.say(' '.join(line.split()[1:]))
				elif cmd == 'sayto':
					target = line.split()[1]
					msg = ' '.join(line.split()[2:])
					self.ircbot.sayto(target,msg)
				elif cmd == 'die':
					self.ircbot.die()
					break
				else:
					print(cli_help)
		return

	def run(self):
		self.serialbot.start()
		self.ircbot.start()
		update_on_change(self.ircbot)
		update_on_change(self.tweeter)
		self.cli()

if __name__ == '__main__':
	s = service()
	s.start()
