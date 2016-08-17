from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals

class Niu():
	def __init__(self):
		self.name = 'niu'

	def isvalid(self,name):
		if name.lower() == self.name:
			return True
			
	def parse(self,data):
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
		   color = 'Tech Blue'
		elif colortrame == '0004':
		   color = 'Cozy Grey'
		elif colortrame == '0005':
		   color = 'Wazabi'
		elif colortrame == '0006':
		   color = 'Lagoon'
		elif colortrame == '0007':
		   color = 'Softberry'
		if buttontrame == '01':
		   button = ' appui simple'
		elif buttontrame == '02':
		   button = ' double appui'
		elif buttontrame == '03':
		   button = ' appui long'
		elif buttontrame == '04':
		   button = ' relachement'
		action['color'] = color
		action['battery'] = battery
		action['button'] = button
		action['buttonid'] = buttontrame[1:2]
		return action

globals.COMPATIBILITY.append(Niu)