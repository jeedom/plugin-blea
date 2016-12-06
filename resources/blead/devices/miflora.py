from bluepy.btle import Scanner, DefaultDelegate, Peripheral
import time
import logging
import globals
import struct

class Miflora():
	def __init__(self):
		self.name = 'miflora'

	def isvalid(self,name,manuf=''):
		if name == 'Flower mate':
			return True
			
	def parse(self,data):
		action={}
		action['present'] = 1
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

	def read(self,mac):
		action={}
		try:
			conn = self.connect(mac)
			batteryFirm = conn.readCharacteristic(56)
			value = 'A01F'
			arrayValue = [int('0x'+value[i:i+2],16) for i in range(0, len(value), 2)]
			conn.writeCharacteristic(51,struct.pack('<%dB' % (len(arrayValue)), *arrayValue))
			datas = conn.readCharacteristic(53)
			conn.disconnect()
		except Exception,e:
			logging.error(str(e))
		return action

globals.COMPATIBILITY.append(Miflora)
