from util import *

class config:
	def __init__(self, conf_file = 'occenseor.conf'):
		self.conf_filename = conf_file
		self.socketsdict = {}
		self.config = {}
	
	def _parse_config(self):
		conf_str = file2str(self.conf_filename)
		for item in conf_str.strip().split('\n'):
			key, val = [x.strip() for x in item.strip().split('=',1)]
			if key.lower().startswith('client.'):
				self.socketdict[key] = val
			else:
				self.config[key] = val

