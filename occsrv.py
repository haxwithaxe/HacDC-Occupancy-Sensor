#!/usr/bin/env python3

import sys
import threading
import ircbot
from util import *

class serivice(threading.Thread):
	def _init_irc(self):
		bot = ircbot.HacDCBot()
		return

	def _init_twitter(self):
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
		self.bot.start()
		self.cli()

