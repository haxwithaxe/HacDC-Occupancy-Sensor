from util import *
from botutil import *
import json
from config import config

conf = config().config
debug = Debug()

def encode(status):
	apidict = file2json(conf['space_api_tmpl'])
	apidict.update({'open':status['status']})
	apidict.update(file2json(conf['hacdc_spaceapi_json']))
	apidict['sensors']['light-switch'].update(json.loads(status['raw']))
	return apidict

