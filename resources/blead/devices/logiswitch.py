from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals
from multiconnect import Connector
from notification import Notification

class LogiSwitch():
	def __init__(self):
		self.name = 'logiswitch'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data=''):
		if 'logi switch' in name.lower():
			return True
			
	def parse(self,data,mac,name,manuf):
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
	
	def handlenotification(self,conn,handle,data,action={}):
		result={}
		if hex(handle) == '0x28':
			received = bytearray(data)
			button = str(received[0])
			if button == '2':
				result['button'] = 1
				result['buttonlabel'] = 'appui simple'
			elif button == '4':
				result['button'] = 2
				result['buttonlabel'] = 'appui double'
			elif button == '3':
				result['button'] = 3
				result['buttonlabel'] = 'appui long'
			result['id'] = conn.mac
			result['source'] = globals.daemonname
			globals.JEEDOM_COM.add_changes('devices::'+conn.mac,result)

globals.COMPATIBILITY.append(LogiSwitch)