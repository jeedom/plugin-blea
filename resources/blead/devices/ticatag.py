from bluepy.btle import Scanner, DefaultDelegate, Peripheral
import time
import logging
import globals
import struct

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
	
	def connect(self,mac):
		logging.debug('Connecting : '+str(mac) + ' with bluetooth ' + str(globals.IFACE_DEVICE))
		i=0
		while True:
			i = i + 1
			try:
				conn = Peripheral(mac,iface=globals.IFACE_DEVICE)
				break
			except Exception as err:
				if i >= 4 :
					return
		return conn
	
	def action(self,message):
		mac = message['device']['id']
		handle = message['command']['handle']
		value = message['command']['value']
		conn = self.connect(mac)
		arrayValue = [int('0x'+value[i:i+2],16) for i in range(0, len(value), 2)]
		conn.writeCharacteristic(int(handle,16),struct.pack('<%dB' % (len(arrayValue)), *arrayValue))
		conn.disconnect()
		return

globals.COMPATIBILITY.append(Ticatag)
