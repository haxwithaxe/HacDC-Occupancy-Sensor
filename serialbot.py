
import time
import threading
import pytty
import json
from util import *


class serial(threading.Thread):
   def __init__(self,stateflag):
      cache = json.loads(open(CACHE,'r').read())
      self.state = None
		self.stateflag = stateflag
      self.since = cache['since']
      self.smstate = cache['status']
      self.lastmsg = None
      self.notify = False
      self.stopnow = False
      self.tty = pytty.TTY(SERIALDEV)
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
               self.since = time.strftime('%a, %b %d at %I:%M %p')
               self.notify = True

               stash(json.dumps({'status':tmp,'since':self.since}))

            if self.notify and self.bot:
               self.notify = False
               self.bot.sendmsg(self.is_open(),self.bot.chan.name)
               if self.cantwit:
                  self.twit.PostUpdate(self.is_open())
                  stdout('TWITTER: TWEETED: '+self.is_open())
               else:
                  stdout('TWITTER: CAN\'T TWEET')

            self.lastmsg = tmp

         time.sleep(10)

      return


	def die(self):
		self._Thread__stop()
