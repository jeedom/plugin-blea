from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals
from multiconnect import Connector
from notification import Notification

class LogiSwitch():
	def __init__(self):
		self.name = 'logiswitch'

	def isvalid(self,name,manuf=''):
		if 'logi switch' in name.lower():
			return True
			
	def parse(self,data,mac,name):
		result={}
		result['present'] = 1
		try:
			conn = Connector(mac)
			conn.connect()
			if not conn.isconnected:
				conn.connect()
				if not conn.isconnected:
					return
			notification = Notification(conn,LogiSwitch)
			notification.subscribe(2)
		except Exception,e:
			logging.error(str(e))
		return result
	
	def handlenotification(self,conn,handle,data):
		result={}
		if hex(handle) == '0x28':
			logging.debug(str(data))
			received = bytearray(data)
			button = received[1]
			logging.debug('button is ' + str(button))

globals.COMPATIBILITY.append(LogiSwitch)