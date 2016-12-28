from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals
import struct
from multiconnect import Connector

class Hector():
	def __init__(self):
		self.name = 'hector'

	def isvalid(self,name,manuf=''):
		if name.lower() == self.name:
			return True
			
	def parse(self,data,mac,name):
		action={}
		action['present'] = 1
		return action
	
	def read(self,mac):
		result={}
		try:
			conn = Connector(mac)
			conn.connect(type='random')
			if not conn.isconnected:
				conn.connect(type='random')
				if not conn.isconnected:
					return
			battery = struct.unpack('2B',conn.readCharacteristic('0x2e'))
			temperature = struct.unpack('2B',conn.readCharacteristic('0x34'))
			humidity = struct.unpack('2B',conn.readCharacteristic('0x3c'))
			pression = struct.unpack('4B',conn.readCharacteristic('0x44'))
			logging.debug(str(battery))
			logging.debug(str(float(temperature[1])/10))
			logging.debug(str(float(humidity[1])*100/255))
			logging.debug(str(pression))
			result['temperature'] = float(temperature[1])/10
			result['humidity'] = round(float(humidity[1])*100/256,2)
		except Exception,e:
			logging.error(str(e))
			conn.disconnect()
		conn.disconnect()
		result['id'] = mac
		return result

globals.COMPATIBILITY.append(Hector)