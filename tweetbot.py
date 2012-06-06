import twitter
import time
import sys
from config import config as configmod
from util import *
from botutil import *

config = configmod()
socketdict = config.socketsdict
config = config.config

class tweeter:
	def __init__(self):
		self.tweeter = None
		self.cantweet = False
		try:
			self.tweeter = twitter.Api( consumer_key=config['consumer_key'], consumer_secret=config['consumer_secret'], access_token_key=config['access_token_key'], access_token_secret=config['access_token_secret'])
			self.cantwit = self.tweeter.VerifyCredentials()
			debug('TWITTER: Can Tweet')
		except Exception as e:
			e = sys.exc_info()[1]
			debug(e)

	def tweet(self,msg):
		if self.cantweet:
			self.tweeter.PostUpdate(msg)

	def update(self):
		tweetmsg = unstash('dict')['default']
		self.tweeter.tweet(tweetmsg)
	
	def pass_msg(self,cmd,args):
		pass

if __name__ == '__main__':
	bot = tweeter()
	update_on_change(bot)
