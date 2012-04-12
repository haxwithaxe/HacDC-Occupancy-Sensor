import twitter
from util import *

class tweeter:
   def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret):
		self.tweeter = None
		self.cantweet
      try:
         self.tweeter = twitter.Api( consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=access_token_key, access_token_secret=access_token_secret)
         self.cantwit = self.twit.VerifyCredentials()
         debug('TWITTER: Can Tweet')
      except:
         e = sys.exc_info()[1]
         debug(e)

	def tweet(self,msg):
