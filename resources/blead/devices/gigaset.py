from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals
from multiconnect import Connector

class Gigaset():
	def __init__(self):
		self.name = 'gigaset g-tag'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data=''):
		if name.lower() == self.name:
			return True
				
	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		return action
	def read(self,mac):
		result={}		
		try:
			conn = Connector(mac)
			conn.connect()
			if not conn.isconnected:
				conn.connect()
				if not conn.isconnected:
					return
			batterytrame = conn.readCharacteristic('0x1b')
			logging.debug('GIGASET------Parsing data ' + batterytrame)
			battery = int(batterytrame.encode("hex"), 16)
			result['battery'] = battery
			result['present'] = 1
		except Exception,e:
			logging.error(str(e))
			conn.disconnect()
		conn.disconnect()
		result['id'] = mac
		return result		
globals.COMPATIBILITY.append(Gigaset)
