from util import *
from botutil import *
import json
from config import config

conf = config().config
debug = Debug()

def encode(status):
	apidict = file2json(conf['space_api_tmpl_json'])
	apidict.update({'open':status['status']})
	apidict.update(file2json(conf['hacdc_spaceapi_json']))
	rs = json.loads(status['raw'])
	apidict['sensors'] = [
				{'light-switch':
					{'main_room':rs['main_light'],'work_room':rs['work_light'],'hall':rs['hall_light']}
				},
				{'motion':
					{'main_room':rs['main_pir'],'work_room':rs['work_pir'],'hall':rs['hall_pir']}
				}
			]
	return json.dumps(apidict)

if __name__ == '__main__':
	status = unstash('dict')
	print(encode(status))
