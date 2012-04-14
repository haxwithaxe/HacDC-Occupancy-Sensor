DEBUG = True

import socket
import config as configmod

config = configmod()

def get_occ_status():
	return {'default':'fancy status (as seen on twitter)','full':'human friendly occsensor output','raw':'raw occsensor output'}

def debug(msg):
	if DEBUG:
		print(msg)

def connect_to_socket(sock):
	return False

def file2str(fname,mode = 'r'):
	fobj = open(fname,mode)
	fstr = fobj.read()
	fobj.close()
	return fstr

def str2file(fname,fstr,mode = 'w'):
	fobj = open(fname,mode)
	fobj.write(fstr)
	fobj.close()

def stash(cachestr):
	str2file(config.cache_file)
