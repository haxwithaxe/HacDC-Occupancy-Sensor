#! /usr/bin/env python

import sys
import threading
from hacdc import *

class serivice(threading.Thread):
	def _init_irc(self):
		server = 'irc.freenode.net'
		port = 6667
		channel = '#hacdc-bot'
		nickname = 'occsensor'
		global globalbotconfig
		globalbotconfig = {'channel':channel, 'nick':nickname, 'server':server, 'port':port}
		bot = NeedleBot()
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

