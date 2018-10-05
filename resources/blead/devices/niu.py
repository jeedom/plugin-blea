from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals

class Niu():
	def __init__(self):
		self.name = 'niu'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data=''):
		if name.lower() == self.name:
			return True
			
	def parse(self,data,mac,name,manuf):
		action={}
		logging.debug('Parsing data ' + data)
		buttontrame = data[34:36]
		batterytrame = data[28:30]
		colortrame = data[24:28]
		battery = str(int(batterytrame,16))
		if colortrame == '0001':
			color = 'No color'
		elif colortrame == '0002':
			color = 'White'
		elif colortrame == '0003':
			color = 'TechBlue'
		elif colortrame == '0004':
			color = 'CozyGrey'
		elif colortrame == '0005':
			color = 'Wazabi'
		elif colortrame == '0006':
			color = 'Lagoon'
		elif colortrame == '0007':
			color = 'Softberry'
		else:
			color = 'No color'
		if buttontrame == '01':
			button = 'simple appui'
		elif buttontrame == '02':
			button = 'double appui'
		elif buttontrame == '03':
			button = 'appui long'
		elif buttontrame == '04':
			button = 'relachement'
		elif buttontrame == '05':
			buttontrame = '05'
			button = 'triple appui'
		elif buttontrame == '06':
			buttontrame = '06'
			button = 'quadruple appui'
		elif buttontrame == '07':
			buttontrame = '07'
			button = 'quintuple appui'
		else:
			button = ''
		action['color'] = color
		action['battery'] = battery
		action['button'] = button
		action['buttonid'] = buttontrame[1:2]
		return action

globals.COMPATIBILITY.append(Niu)