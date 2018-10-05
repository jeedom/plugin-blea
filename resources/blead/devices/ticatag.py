from bluepy import btle
import time
import logging
import globals
from multiconnect import Connector

class Ticatag():
	def __init__(self):
		self.name = 'ticatag'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data=''):
		if name.lower() == self.name:
			return True
			
	def parse(self,data,mac,name,manuf):
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
			button = 'simple appui'
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
	
	def action(self,message):
		mac = message['device']['id']
		handle = message['command']['handle']
		value = message['command']['value']
		conn = Connector(mac)
		conn.connect()
		if not conn.isconnected:
			return
		conn.writeCharacteristic(handle,value)
		conn.disconnect()
		return

globals.COMPATIBILITY.append(Ticatag)
