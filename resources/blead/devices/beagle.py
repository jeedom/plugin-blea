from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals

class Beagle():
	def __init__(self):
		self.name = 'beagle'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if name.lower() == self.name:
			return True
		if manuf.lower()[0:8] == 'b6028e44':
			return True
			
	def parse(self,data,mac,name,manuf):
		action={}
		logging.debug('Parsing data ' + manuf)
		cf= manuf[12:14]
		if cf == '00' and mac.upper() in globals.KNOWN_DEVICES:
			action['present'] = 1
			action['firmware'] = manuf[24:30]
			if manuf[22:24] == '02':
				action['value'] = '1'
				action['label'] = 'Toggle'
			elif manuf[22:24] == '05':
				action['value'] = '2'
				action['label'] = 'Haut'
			elif self.manuf[22:24] == '06':
				action['value'] = '3'
				action['label'] = 'Bas'
		elif cf == '01' and mac.upper() not in globals.KNOWN_DEVICES:
			action['present'] = 1
		else:
			action['bind'] = False
			return action
		return action

globals.COMPATIBILITY.append(Beagle)