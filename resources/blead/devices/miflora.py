from bluepy import btle
import time
import logging
import globals
import struct
from multiconnect import Connector

class Miflora():
	def __init__(self):
		self.name = 'miflora'

	def isvalid(self,name,manuf=''):
		validname = ['Flower mate','Flower care']
		if name in validname:
			return True
			
	def parse(self,data,mac):
		action={}
		action['present'] = 1
		return action

	def read(self,mac):
		result={}
		try:
			conn = Connector(mac)
			conn.connect()
			if not conn.isconnected:
				return
			batteryFirm = conn.readCharacteristic(0x38)
			value = 'A01F'
			conn.writeCharacteristic(0x33,value)
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
