from bluepy import btle
import time
import logging
import globals
import struct
from multiconnect import Connector
from notification import Notification

class BeeWiSmartDoor():
	def __init__(self):
		self.name = 'beewi smart door'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data=''):
		if name.lower() == self.name:
			return True
			
	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1		
		logging.debug('PARSE: manuf[4:9]= ' + manuf[4:9] )
		if manuf[4:8] == '080c':              
			status = manuf[9:10]
			if manuf[4:8] == '080c':
				status = manuf[9:10]
				if status == '1':
					status = '0'
				elif status == '0':
					status = '1'
			battery = manuf[12:14]
			action['status'] = status
			action['battery'] = int(battery,16)
			logging.debug('BeeWi PARSE: status = ' + status )
		else:
			logging.debug('BeeWi PARSE: wrong frame ')		
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
			batt = bytearray(conn.readCharacteristic('0x19'))
			battery = batt[0]
			result['battery'] = battery
			result['id'] = mac
			logging.debug('BeeWiiSmartDoor------'+str(result) + ' Battery: ' + battery + '%')
			return result
		except Exception,e:
			logging.error(str(e))
		return result
			
globals.COMPATIBILITY.append(BeeWiSmartDoor)