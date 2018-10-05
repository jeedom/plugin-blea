from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals
from multiconnect import Connector

class Nut():
	def __init__(self):
		self.name = 'nut'
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
			conn.connect(type='random')
			if not conn.isconnected:
				conn.connect(type='random')
				if not conn.isconnected:
					return
			batteryDatas = bytearray(conn.readCharacteristic('0x17'),type='random')
			result['battery'] = batteryDatas[0]
			result['id'] = mac
			logging.debug(str(result))
			return result
		except Exception,e:
			logging.error(str(e))
			conn.disconnect()
		conn.disconnect()
		return result
	
	def action(self,message):
		mac = message['device']['id']
		handle = message['command']['handle']
		value = message['command']['value']
		conn = Connector(mac)
		conn.connect(type='random')
		if not conn.isconnected:
			conn.connect(type='random')
			if not conn.isconnected:
				return
		conn.writeCharacteristic(handle,value,type='random')
		conn.disconnect()
		return

globals.COMPATIBILITY.append(Nut)