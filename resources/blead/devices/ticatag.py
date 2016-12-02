from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals

class Ticatag():
	def __init__(self):
		self.name = 'ticatag'

	def isvalid(self,name,manuf=''):
		if name.lower() == self.name:
			return True
			
	def parse(self,data):
		action={}
		action['present'] = 1
		temperaturetrame = data[32:34]
		temperature = str(int(temperaturetrame,16))
		action['temperature'] = temperature
		batterytrame = data[28:30]
		battery = str(int(batterytrame,16))
		action['battery'] = battery
		buttontrame = data[35:36]
		if buttontrame == '1':
			button = 'appui'
		elif buttontrame == '2':
			button = 'double appui'
		elif buttontrame == '3':
			button = 'appui long'
		elif buttontrame == '0':
			button = 'relachement'
		else:
			button = ''
		action['button'] = button
		action['buttonid'] = buttontrame

		return action

globals.COMPATIBILITY.append(Ticatag)
