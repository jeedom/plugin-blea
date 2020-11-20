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
			if manuf[22:24] == '00':
				action['value'] = '0'
				action['label'] = 'Off'
			elif manuf[22:24] == '01':
				action['value'] = '1'
				action['label'] = 'On'
			elif manuf[22:24] == '02':
				action['value'] = '2'
				action['label'] = 'Toggle'
			elif manuf[22:24] == '03':
				action['value'] = '3'
				action['label'] = 'Dim Up'
			elif manuf[22:24] == '04':
				action['value'] = '4'
				action['label'] = 'Dim Down'
			elif manuf[22:24] == '05':
				action['value'] = '5'
				action['label'] = 'Haut'
			elif manuf[22:24] == '06':
				action['value'] = '6'
				action['label'] = 'Bas'
			elif manuf[22:24] == '07':
				action['value'] = '7'
				action['label'] = 'Stop'
			elif manuf[22:24] == '08':
				action['value'] = '8'
				action['label'] = 'Scene User'
			elif manuf[22:24] == '09':
				action['value'] = '9'
				action['label'] = 'Scene In'
			elif manuf[22:24] == '0a':
				action['value'] = '10'
				action['label'] = 'Scene Out'
		elif cf == '01' and mac.upper() not in globals.KNOWN_DEVICES:
			action['present'] = 1
		else:
			action['bind'] = False
			return action
		return action

globals.COMPATIBILITY.append(Beagle)