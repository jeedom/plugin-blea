import time
import logging
import globals

class Meyerdom4contacts():
	def __init__(self):
		self.name = 'meyerdom4contacts'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if 'meyerdom 4 contacteurs' in name.lower() or name.lower()==self.name:
			return True

	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		try:
			action['contact1'] = 0
			action['contact2'] = 0
			action['contact3'] = 0
			action['contact4'] = 0
			if manuf[0:2] == '31':
				action['contact1'] = 1
			if manuf[2:4] == '31':
				action['contact2'] = 1
			if manuf[4:6] == '31':
				action['contact3'] = 1
			if manuf[6:8] == '31':
				action['contact4'] = 1
			action['voltage'] = float(bytearray.fromhex(manuf[24:]).decode())
		except Exception as e:
			logging.error(str(e))
		logging.debug(str(action))
		return action
globals.COMPATIBILITY.append(Meyerdom4contacts)
