import twitter
from config import config as configmod
from util import *

config = configmod().config

class tweeter:
   def __init__(self, config['consumer_key'], config['consumer_secret'], config['access_token_key'], config['access_token_secret']):
		self.tweeter = None
		self.cantweet
      try:
         self.tweeter = twitter.Api( consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=access_token_key, access_token_secret=access_token_secret)
         self.cantwit = self.tweet.VerifyCredentials()
         debug('TWITTER: Can Tweet')
      except Exception as e:
         e = sys.exc_info()[1]
         debug(e)

	def tweet(self,msg):
		if self.cantweet:
			self.tweeter.PostUpdate(msg)
