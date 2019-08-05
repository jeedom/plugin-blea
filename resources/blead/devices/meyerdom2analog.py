import time
import logging
import globals

class Meyerdom2Analog():
	def __init__(self):
		self.name = 'meyerdom2analog'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if 'meyerdom 2 contacteurs analog' in name.lower() or name.lower()==self.name:
			return True

	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		try:
			action['analog1'] = int(bytearray.fromhex(manuf[8:16]).decode())
			action['analog2'] = int(bytearray.fromhex( manuf[16:24]).decode())
			action['voltage'] = float(bytearray.fromhex(manuf[24:]).decode())
		except Exception as e:
			logging.error(str(e))
		logging.debug(str(action))
		return action
globals.COMPATIBILITY.append(Meyerdom2Analog)
