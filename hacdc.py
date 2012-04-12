DEBUG = True

def get_occ_status():
	return {'default':'fancy status (as seen on twitter)','full':'human friendly occsensor output','raw':'raw occsensor output'}

def debug(msg):
	if DEBUG:
		print(msg)
