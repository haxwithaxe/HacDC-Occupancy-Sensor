#!/usr/bin/env python

import sys
import threading
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
MISSING_DATA_MSG='''My data is missing.'''

default_statusdict = {'default':'','full':'','raw':''}

config = configmod().config
debug = Debug(5,5,'ircbot.log','[%Y/%m/%d %H:%M:%S GMT%z]')

class HacDCBot(SingleServerIRCBot):
	def __init__(self):
		SingleServerIRCBot.__init__(self, [(config['irc.server'], int(config['irc.port']))], config['irc.nick'], config['irc.nick'])
		self.channel = config['irc.channel']

	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + "_")

	def on_welcome(self, c, e):
		c.join(self.channel)
		debug.send('joined irc',2)

	def on_privmsg(self, c, e):
		debug.send(('event source',e.source()),5)
		debug.send(('event target',e.target()),5)
		debug.send(('event arguments',e.arguments()),5)
		self._handle_msg(c, e)

	def on_pubmsg(self, c, e):
		debug.send(('event source',e.source()),5)
		debug.send(('event target',e.target()),5)
		debug.send(('event arguments',e.arguments()),5)
		self._handle_msg(c, e)
	
	def _handle_msg(self, c, e):
		line = []
		words = e.arguments()[0].split(":", 1)
		debug.send(('words in HacDCBot._handle_msg',words),5)
		if len(words[0]) > 0:
			if len(words) == 2:
				if len(words[1]) > 0: line = [words[1].strip()]
			word0 = words[0]
			debug.send(('line post name split of HacDCBot._handle_msg',line),5)
			mynick = irc_lower(self.connection.get_nickname())
			if irc_lower(word0) == mynick:
				line += e.arguments()[1:]
			else:
				line = e.arguments()
			if len(line) > 0:
				debug.send(('line of _handle_msg',line),5)
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
		debug.send(('cmd in do_command',cmd),3)
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
		if nick in config['boss_list'].split(','):
			return True
		return False

	def _handle_cmds(self, c, e, line):
		debug.send('in _handle_cmds',5)
		sendhelp = False
		chan = self.channel
		if chan == irc_lower(self.connection.get_nickname()): chan = irc_lower(nm_to_n(e.source()))
		debug.send(('chan in _handle_cmds',chan),5)
		cmd_args_list = line[0].lower()[1:].strip().split()
		cmd = cmd_args_list[0]
		debug.send(('cmd,line,cmd_args_list in _handle_cmds',cmd,line,cmd_args_list),5)
		args = []
		if len(cmd_args_list) > 1: args = [x.strip() for x in cmd_args_list[1:]]
		debug.send(('args in _handle_cmds',args),5)
		if len(args) > 1 and args[1] in HELPSTR:
			sendhelp = True
		if cmd == 'space':
			if sendhelp:
				self._send_help(c,cmd,chan)
			else:
				self._status_msg(c,args,chan)
		elif cmd == 'help':
			self._send_help(c,cmd,args,chan)
		else:
			self.do_command(e,cmd.lower())

	def _handle_sock_cmd(self,cmd,args):
		if cmd == 'say':
			self.say(' '.join(args))
		elif cmd == 'sayto' and len(args) > 1:
			self.sayto(args[0],' '.join(args[1:]))
		elif cmd == 'die':
			self.die()
		elif cmd == 'cycle':
			pass
		elif cmd == 'reconnect':
			self.connection.reconnect()

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
		statusdict = unstash('dict') or default_statusdict
		if len(args) > 0:
			arg1 = args[0].lower()
		else:
			arg1 = False
		if not msg:
			if not arg1:
				msg = statusdict['default'] or MISSING_DATA_MSG
			elif 'full' == arg1:
				msg = statusdict['full'] or MISSING_DATA_MSG
			elif 'raw' == arg1:
				msg = statusdict['raw'] or MISSING_DATA_MSG
		if msg:
			self.sayto(chan,msg)
		return

	def update(self):
		print('update')
		statusdict = unstash('dict') or default_statusdict
		self.say(statusdict['default'] or MISSING_DATA_MSG)

	def pass_msg(self,msg):
		bits = msg.split()
		cmd = bits[0]
		args = bits[1:]
		self._handle_sock_cmd(cmd,args)

	def cycle(self):
		pass

	def say(self,msg):
		self.sayto(self.channel,msg)

	def sayto(self,target,msg):
		debug.send('said "'+msg+'" in "'+target+'"',3)
		c = self.connection
		c.privmsg(target,msg)

class _RunThreaded(threading.Thread):
	def __init__(self,bot):
		self.bot = bot
		threading.Thread.__init__(self)

	def run(self):
		self.bot.start()

if __name__ == "__main__":
	cli_usage = 'help msg here'
	print('initializing ircbot')
	bot = HacDCBot()
	print('about to run update_on_change')
	update_on_change(bot)
	print('starting ircbot')
	t = _RunThreaded(bot)
	t.start()
	die = False
	while not die:
		line = raw_input('bot.irc>>').strip()
		if len(line) > 0:
			args = []
			cmd = line.split(' ',1)[0].replace(':','')
			if len(line.split()) > 1: args = line.split()[1:]
			if cmd == 'say':
				bot.say(' '.join(args))
			elif cmd == 'sayto' and len(args) > 1:
				bot.sayto(args[0],' '.join(args[1:]))
			elif cmd == 'cycle':
				bot.cycle()
			elif cmd == 'die':
				bot.die()
			else:
				print(cli_usage)
