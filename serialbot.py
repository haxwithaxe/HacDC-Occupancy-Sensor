
import time
import threading
import pytty
import json
from util import *

class serial(threading.Thread):
   def __init__(self,stateflag):
      cache = json.loads(file2str(CACHE,'r'))
		self.config = config()
      self.state = None
		self.stateflag = stateflag
      self.since = cache['since']
      self.smstate = cache['status']
      self.lastmsg = None
      self.notify = False
      self.stopnow = False
      self.tty = pytty.TTY(self.config.serialdev)
      threading.Thread.__init__( self )

	def run(self):
		while not self.stopnow:
			time.sleep(1)
         rawmsg = self.tty.readline()
         try:
            rawmsgdict = json.loads(rawmsg.split('\r\n',1)[0].decode())
         except:
            rawmsgdict = None

         if rawmsgdict:
            debug('DEVICE SAYS: %s' % rawmsg)
            self.state = rawmsgdict
            current_boolstate = (0 < (self.state['hall_light'] + self.state['main_light'] + self.state['work_light'])) #+ self.state['main_pir'] + self.state['work_pir']

            if (self.boolstate != current_boolstate and self.lastmsg != current_boolstate):
               debug('OCCSENSOR STATE SET: %s' % current_boolstate)
               self.boolstate = current_boolstate
               self.since = time.strptime('%s').strftime('%a, %b %d at %I:%M %p')
               self.notify = True

               stash(json.dumps({'status':current_boolstate,'since':self.since}))

            if self.notify and self.bot:
               self.notify = False
					self.pushupdate()
            self.lastmsg = tmp
		# end while
      return

	def _get_status_str():
		statdict = {'default':self.config.default_msg_fmt,'full':self.config.full_msg_fmt,'raw':self.config.raw_msg_fmt}
		statdict['default'] = statdict['default'] % ({True:'open',False:'closed'}[self.boolstate],time.strptime(self.since,self.config.stash_time_fmt).strftime(self.config.default_time_fmt))
		statdict['full'] = statdict['full'] % ({True:'open',False:'closed'}[self.state['hall_light']],{True:'open',False:'closed'}[self.state['main_light']],{True:'open',False:'closed'}[self.state['work_light']])

	def pushupdate():
		str2file(self.config.status_file,self._get_status_str())
		socketdict = self.config.statussocket
		sock = connect_to_socket(socketdict)
		if sock:
			sock.send(self.config.update_flag)
			sock.close()

	def die(self):
		self.stopnow = True
		self._Thread__stop()
