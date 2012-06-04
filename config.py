from util import *

class config:
	def __init__(self, conf_file = 'occsensor.conf'):
		self.conf_filename = conf_file
		self.socketsdict = {}
		self.config = {}
		self._parse_config()
	
	def _parse_config(self):
		conf_str = file2str(self.conf_filename)
		for item in conf_str.strip().split('\n'):
			if item.strip()[0] != '#':
				key, val = [x.strip() for x in item.strip().split('=',1)]
				if key.lower().startswith('client.'):
					self.socketsdict[key] = val
				else:
					self.config[key] = val

if __name__ == '__main__':
	c = config()
	print(c.config)
	print(c.socketsdict)

