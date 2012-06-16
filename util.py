import os
import json
import time

class Debug:
	def __init__(self,debug_level = 5,log_level = 5,log_file = None, timestamp = ''):
		self.debug_level = debug_level
		self.log_level = log_level
		self.log_file = log_file
		self.timestamp = timestamp
		if not self.log_file: self.log_level = -1
	def send(self,msg,level=1):
		if self.timestamp:
			timestamp = time.strftime(self.timestamp)
		else:
			timestamp = ''
		msg = [timestamp, str(repr(msg))]
		for i in range(msg.count('')):
			msg.remove('')
		msg = ' '.join(msg)+'\n'
		if self.debug_level >= level:
			print(msg)
		if self.log_level >= level:
			str2file(msg,self.log_file,'a')

def file2str(file_name, mode = 'r'):
	if not os.path.exists(file_name):
		print('File not found: '+file_name)
		return ''
	fileobj = open(file_name,mode)
	filestr = fileobj.read()
	fileobj.close()
	return filestr

def file2json(file_name, mode = 'r'):
	filestr = file2str(file_name, mode)
	try:
		return_value = json.loads(filestr)
	except ValueError as val_e:
		print(repr(val_e))
		return_value = None
	return return_value

def str2file(string,file_name,mode = 'w'):
	fileobj = open(file_name,mode)
	fileobj.write(string)
	fileobj.close()

def json2file(obj, file_name, mode = 'w'):
	try:
		string = json.dumps(obj)
		str2file(string, file_name, mode)
		return True
	except TypeError as type_e:
		print(repr(type_e))
		return False
def to_float(nstr):
	if nstr.replace('.',1).isdigit():
		return float(nstr)
	else:
		return None
