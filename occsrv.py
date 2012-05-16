#!/usr/bin/env python3

import sys
import threading
import hacdc_ircbot
from util import *

class service(threading.Thread):
	def __init__(self):
		_init_irc()
		_init_twitter()
		_init_serial()
		threading.Thread.__init__(self)
	def _init_irc(self):
		self.ircbot = hacdc_ircbot.HacDCBot()
		return

	def _init_twitter(self):
		self.tweeter = tweetbot.tweetbot()
		return

	def _init_serial(self):
		self.serialbot = serialbot.serialbot()
		return

	def cli(self):
		while True:
			line = raw_input().strip()
			if len(line) > 0:
				cmd = line.split()[0].strip()
				if cmd == 'say':
					self.bot.say(' '.join(line.split()[1:]))
				elif cmd == 'sayto':
					target = line.split()[1]
					msg = ' '.join(line.split()[2:])
					self.bot.sayto(target,msg)
				elif cmd == 'die':
					self.bot.die()
					break
				else:
					print(cli_help)
	return

	def run(self):
		self.serialbot.start()
		self.ircbot.start()
		self.tweeter.start()
		self.cli()

