DEBUG = 5


def debug(msg,level=1):
	if DEBUG >= level:
		print(msg)

def file2str(fname,mode = 'r'):
	fobj = open(fname,mode)
	fstr = fobj.read()
	fobj.close()
	return fstr

def str2file(fname,fstr,mode = 'w'):
	fobj = open(fname,mode)
	fobj.write(fstr)
	fobj.close()
