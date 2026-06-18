# coding: utf-8
import logging
import globals
from multiconnect import Connector

class BeeWiBBW200():
	def __init__(self):
		self.name = 'beewibbw200'
		self.ignoreRepeat = False
		
	def readDataString(self,value):
		logging.debug('BBW200--readDataString() : %s',value.hex())
		
		temperature = value[2]*256 + value[1]

		if (temperature > 0x8000):
			temperature = temperature - 0x10000

		temperature = temperature / 10.0

		humidity = value[4]
		# sometimes value is greater than 100
		if humidity > 100:
			humidity = 100
		battery = value[9]
		result={}
		
		result['moisture'] = humidity
		result['temperature'] = temperature
		result['battery'] = battery
		result['present'] = 1
		logging.debug('BBW200--readDataString() : result =%s',str(result))
		return result

	def isvalid(self,name,manuf='',data='',mac=''):
		if name.lower() == self.name or manuf[0:6] == '0d0005':
			logging.debug('BBW200--isValid()=true name=%s manuf=%s data=%s mac=%s', name, manuf, data, mac)
			return True
		return False

	def parse(self,data,mac,name,manuf):
		result={}
		logging.debug('BBW200--parse() name=%s manuf=%s data=%s mac=%s', name, manuf, data, mac)
		# ignore 6 first chars
		result = self.readDataString(bytearray.fromhex(manuf[6:]))
		result['present'] = 1
		result['id'] = mac
		return result
	
	def read(self,mac):
		result={}
		if 'present' in globals.SEEN_DEVICES[mac.upper()] and globals.SEEN_DEVICES[mac.upper()]['present'] == 1:
			try:
				logging.debug('BBW200--read() Creating a new connection for %s', mac)
				conn = Connector(mac)
				conn.connect()
				if not conn.isconnected:
					conn.connect()
					if not conn.isconnected:
						return
				bytesarr = conn.readCharacteristic('0x003f')
				if bytesarr:
					logging.debug('BBW200-- data 0x3f=%s', bytesarr.hex())
					result = self.readDataString(bytesarr)
				result['id'] = mac
				
			except Exception as e:
				logging.exception(str(e))
				
			if conn.isconnected:
				logging.debug('BBW200--read() close connection')
				conn.disconnect()
		else:
			logging.info("BBW200--read() : Device %s isn't present, can't read values !",mac)
		return result
		
globals.COMPATIBILITY.append(BeeWiBBW200)