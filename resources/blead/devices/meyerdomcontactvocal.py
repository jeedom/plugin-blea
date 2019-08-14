import time
import logging
import globals

class MeyerdomContactVocal():
	def __init__(self):
		self.name = 'meyerdomcontactvocal'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if 'meyerdom contacteur vocal' in name.lower() or name.lower()==self.name:
			return True

	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		try:
			action['contact1'] = 0
			if manuf[0:2] == '31':
				action['contact1'] = 1
			action['voltage'] = float(bytearray.fromhex(manuf[24:]).decode())
		except Exception as e:
			logging.error(str(e))
		logging.debug(str(action))
		return action
globals.COMPATIBILITY.append(MeyerdomContactVocal)
