#!/usr/bin/env python

from utils import *
from botutils import *
import urllib,urllib2

conf = config().config

def get_status():
	urlargs='?'
	statusdict = file2json(conf['status_cache'],'dict')
	if statusdict:
		for k,v in statusdict.items():
			if k == 'raw':
				for sensor,state in json.loads(v).items():
					urlargs+=sensor+'='+urllib.urlencode(str(state))
			else:
				urlargs+=k+'='+urllib.urlencode(str(v))
	else:
		urlargs = '?status-not-available=true'
	return urlargs

def send_status(urlargs):
	url = conf['remote_status_cache_url']
	url += urlargs
	rep = urllib2.urlopen(url)
	debug(rep,5)
