#!/usr/bin/env python3

import sys
import threading
import comms
from util import *
from botutil import *
from config import config as configmod
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr, is_channel

CMDPREFIX = ['.','!']
CMDS = ['space', 'help']
HELPSTR = ['?', 'help', 'usage']
HELPMSG = {
	'help':'use .space to see the occupancy status of HacDC',
	'space':'usage: .space [full|raw]'
	}

config = configmod()
socketdict = config.socketsdict
config = config.config

class HacDCBot(SingleServerIRCBot):
	def __init__(self):
		SingleServerIRCBot.__init__(self, [(config['irc.server'], int(config['irc.port']))], config['irc.nick'], config['irc.nick'])
		self.sock = comms.client(socketdict['client.irc'])
		self.channel = config['irc.channel']

	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + "_")

	def on_welcome(self, c, e):
		c.join(self.channel)

	def on_privmsg(self, c, e):
		debug(('event source',e.source()))
		debug(('event target',e.target()))
		debug(('event arguments',e.arguments()))
		self._handle_msg(c, e)

	def on_pubmsg(self, c, e):
		debug(('event source',e.source()))
		debug(('event target',e.target()))
		debug(('event arguments',e.arguments()))
		self._handle_msg(c, e)
	
	def _handle_msg(self, c, e):
		line = []
		words = e.arguments()[0].split(":", 1)
		debug(('words',words))
		if len(words[0]) > 0:
			if len(words) == 2:
				if len(words[1]) > 0: line = [words[1].strip()]
			word0 = words[0]
			debug(('line post name split of _handle_msg',line))
			mynick = irc_lower(self.connection.get_nickname())
			if irc_lower(word0) == mynick:
				line += e.arguments()[1:]
			else:
				line = e.arguments()
			if len(line) > 0:
				debug(('line of _handle_msg',line))
				self._handle_cmds(c, e, line)
		return

	def on_dccmsg(self, c, e):
		c.privmsg("You said: " + e.arguments()[0])
		self._handle_cmds(c, e, False)

	def on_dccchat(self, c, e):
		if len(e.arguments()) != 2:
			return
		args = e.arguments()[1].split()
		if len(args) == 4:
			try:
				address = ip_numstr_to_quad(args[2])
				port = int(args[3])
			except ValueError:
				return
			self.dcc_connect(address, port)

	def do_command(self, e, cmd):
		debug(('cmd in do_command',cmd))
		nick = nm_to_n(e.source())
		chan = e.target()
		if chan == irc_lower(self.connection.get_nickname()): chan = nick
		c = self.connection
		if self._isboss(nick):
			if cmd == "disconnect":
				self.disconnect()
			elif cmd == "die":
				self.die()
			elif cmd == "stats":
				for chname, chobj in self.channels.items():
					c.privmsg(nick, "--- Channel statistics ---")
					c.privmsg(nick, "Channel: " + chname)
					users = chobj.users()
					users.sort()
					c.privmsg(nick, "Users: " + ", ".join(users))
					opers = chobj.opers()
					opers.sort()
					c.privmsg(nick, "Opers: " + ", ".join(opers))
					voiced = chobj.voiced()
					voiced.sort()
					c.privmsg(nick, "Voiced: " + ", ".join(voiced))
			elif cmd == "dcc":
				dcc = self.dcc_listen()
				c.ctcp("DCC", nick, "CHAT chat %s %d" % (ip_quad_to_numstr(dcc.localaddress), dcc.localport))
		elif cmd in ('disconnect','die','stats','dcc','cycle'):
			c.privmsg(chan,'''you're not the boss of me :P''')
		return

	def _isboss(self,nick):
		if nick in config['boss_list']:
			return True
		return False

	def _handle_cmds(self, c, e, line):
		debug('in _handle_cmds')
		sendhelp = False
		chan = self.channel
		if chan == irc_lower(self.connection.get_nickname()): chan = irc_lower(nm_to_n(e.source()))
		debug(('chan in _handle_cmds',chan))
		cmd = line[0].lower()[1:]
		debug(('cmd in _handle_cmds',cmd))
		args = []
		if len(line) > 1: args = [x.strip() for x in line[1:]]
		debug(('args in _handle_cmds',args))
		if len(args) > 0 and args[0].lower() in HELPSTR:
			sendhelp = True
		if cmd == 'space':
			if sendhelp:
				self._send_help(c,cmd,chan)
			else:
				self._status_msg(c,args,chan)
		elif cmd == 'help':
			self._send_help(c,cmd,args,chan)
		else:
			self.do_command(e,line[0].lower())

	def _send_help(self, c, cmd = 'help', args = [], chan = False):
		arg1 = False
		if not chan: chan = self.channel
		if len(args) > 0: arg1 = args[0].lower()
		if cmd == 'help' and arg1 in CMDS:
			c.privmsg(chan, HELPMSG[arg1])
		else:
			c.privmsg(chan, HELPMSG[cmd])

	def _status_msg(self, c, args = [], chan = False):
		msg = False
		if not chan: chan = self.channel
		statusdict = unstash('dict')
		if not statusdict: msg = '''My data is missing.'''
		if len(args) > 0:
			arg1 = args[0].lower()
		else:
			arg1 = False
		if not msg:
			if not arg1:
				msg = statusdict['default']
			elif 'full' == arg1:
				msg = statusdict['full']
			elif 'raw' == arg1:
				msg = statusdict['raw']
		if msg:
			self.sayto(chan,msg)
		return

	def update(self):
		statusdict = unstash('dict')
		self.say(statusdict['default'] or '''My data is missing.''')

	def say(self,msg):
		self.sayto(self.channel,msg)

	def sayto(self,target,msg):
		c = self.connection
		c.privmsg(target,msg)


def main():
	bot = HacDCBot()
	bot.start()
	update_on_change(bot)

if __name__ == "__main__":
	main()
