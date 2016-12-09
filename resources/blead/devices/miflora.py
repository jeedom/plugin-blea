from bluepy import btle
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
				conn = btle.Peripheral(mac,iface=globals.IFACE_DEVICE)
				break
			except Exception,e:
				if i >= 4 :
					return
		return conn

	def read(self,mac):
		result={}
		try:
			conn = self.connect(mac)
			logging.debug('Connected...')
			batteryFirm = conn.readCharacteristic(0x38)
			value = 'A01F'
			arrayValue = [int('0x'+value[i:i+2],16) for i in range(0, len(value), 2)]
			conn.writeCharacteristic(0x33,struct.pack('<%dB' % (len(arrayValue)), *arrayValue))
			datas = conn.readCharacteristic(0x35)
			conn.disconnect()
			battery, firmware = struct.unpack('<B6s',batteryFirm)
			temperature, sunlight, moisture, fertility = struct.unpack('<hxIBHxxxxxx',datas)
			temperature = float(temperature)/10
			result['battery'] = battery
			result['firmware'] = firmware.replace('\x10','')
			result['sunlight'] = sunlight
			result['moisture'] = moisture
			result['fertility'] = fertility
			result['temperature'] = temperature
			result['id'] = mac
			logging.debug(str(result))
			return result
		except Exception,e:
			logging.error(str(e))
		return result

globals.COMPATIBILITY.append(Miflora)
