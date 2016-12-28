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
			if mac in globals.KEEPED_CONNECTION:
				logging.debug('Already a connection for ' + mac + ' use it')
				conn = globals.KEEPED_CONNECTION[mac]
			else:
				logging.debug('Creating a new connection for ' + mac)
				conn = Connector(mac)
				globals.KEEPED_CONNECTION[mac]=conn
				conn.connect()
			if not conn.isconnected:
				conn.connect()
				if not conn.isconnected:
					return
			#conn.writeCharacteristic('0x29','0100',response=True)
			#conn.writeCharacteristic('0x2b','015201',response=True)
			notification = Notification(conn,LogiSwitch)
			notification.subscribe(5)
		except Exception,e:
			logging.error(str(e))
		return result
	
	def handlenotification(self,conn,handle,data):
		result={}
		logging.debug('Received notfi')

globals.COMPATIBILITY.append(LogiSwitch)