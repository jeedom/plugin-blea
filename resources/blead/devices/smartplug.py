from bluepy import btle
import time
import logging
import globals
import binascii
from multiconnect import Connector
from notification import Notification
import struct

class Smartplug():
	def __init__(self):
		self.name = 'smartplug'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data=''):
		if name.lower().startswith("smp-b16-") or name.lower() == 'smartplug':
			return True
			
	def parse(self,data,mac,name,manuf):
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
			except Exception, e:
				logging.error(str(e))
				if i >= 4 :
					return
		return conn
	
	def action(self,message):
		mac = message['device']['id']
		handle = message['command']['handle']
		value = message['command']['value']
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
		conn.writeCharacteristic(handle,value)
		logging.debug('Value ' + value + ' written in handle ' +handle)
		logging.debug('Refreshing ... ')
		result = self.read(mac)
		return result
	
	def read(self,mac):
		global result
		result={}
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
			notification = Notification(conn,Smartplug)
			conn.writeCharacteristic('0x2b','0f050400000005ffff')
			notification.subscribe(2)
			return
		except Exception,e:
			try:
				conn.disconnect()
			except Exception,e:
				pass
			logging.error(str(e))
		return
		
	def handlenotification(self,conn,handle,data,action={}):
		state = False
		result  = {}
		bytes_data = bytearray(data)
		if bytes_data[0:3] == bytearray([0x0f, 0x0f, 0x04]):
			state = bytes_data[4] == 1
			power = int(binascii.hexlify(bytes_data[6:10]), 16) / 1000
			result['power'] = power
			if state:
				result['status'] = 1
			else:
				result['status'] = 0
			result['id'] = conn.mac
			result['source'] = globals.daemonname
			globals.JEEDOM_COM.add_changes('devices::'+conn.mac,result)

globals.COMPATIBILITY.append(Smartplug)