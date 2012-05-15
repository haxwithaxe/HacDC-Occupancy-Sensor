DEBUG = True

from config import config as configmod

config = configmod().config

def get_occ_status():
	return {'default':'fancy status (as seen on twitter)','full':'human friendly occsensor output','raw':'raw occsensor output'}

def stash(cachestr):
	str2file(config['cache_file'])
