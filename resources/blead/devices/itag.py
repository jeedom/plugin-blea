from bluepy import btle
import time
import logging
import globals
from multiconnect import Connector
from notification import Notification

class Itag():
	def __init__(self):
		self.name = 'itag'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data=''):
		if name.lower() in [self.name,'mle-15']:
			return True
			
	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		if mac.upper() in globals.KNOWN_DEVICES and globals.KNOWN_DEVICES[mac.upper()]['emitterallowed'] == globals.daemonname and globals.KNOWN_DEVICES[mac.upper()]['islocked'] == 1:
			conn = Connector(mac)
			conn.connect()
			if not conn.isconnected:
				conn.connect()
				if not conn.isconnected:
					return action
			conn.writeCharacteristic('0x36','0100')
			notification = Notification(conn,Itag)
			notification.subscribe()
			globals.KEEPED_CONNECTION[mac.upper()]=conn
		return action
	
	def action(self,message):
		mac = message['device']['id']
		handle = message['command']['handle']
		value = message['command']['value']
		conn = Connector(mac)
		conn.connect()
		if not conn.isconnected:
			return
		conn.writeCharacteristic(handle,value)
		conn.disconnect()
		return
	
	def handlenotification(self,conn,handle,data,action={}):
		result={}
		result['button'] = 1
		result['id'] = conn.mac
		result['source'] = globals.daemonname
		globals.JEEDOM_COM.add_changes('devices::'+conn.mac,result)

globals.COMPATIBILITY.append(Itag)
