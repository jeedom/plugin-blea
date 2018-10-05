# coding: utf-8
from bluepy import btle
import logging
import globals
from multiconnect import Connector

class DreamScreen():
	def __init__(self):
		self.name = 'dreamscreen'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data=''):
		if name.lower() in [self.name]:
			return True
			
	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		return action
	
	def action(self,message):
		mac = message['device']['id']
		handle = message['command']['handle']
		value = message['command']['value']
		type = message['command']['type']
		conn = Connector(mac)
		conn.connect()
		if not conn.isconnected:
			conn.connect()
			if not conn.isconnected:
				return
		try:
			if type == 'color':
				if value == '000000':
					conn.writeCharacteristic(handle,'234277305C72')
				else:
					value=self.intToStr(int(value[0:2], 16))+self.intToStr(int(value[2:4], 16))+self.intToStr(int(value[4:6], 16))
					conn.writeCharacteristic(handle,'234577'+value+'5C72')
			elif type == 'ambient':
				conn.writeCharacteristic(handle,'234D77'+value+'5C72')
			elif type == 'brightness':
				conn.writeCharacteristic(handle,'234377'+self.intToStr(int(value))+'5C72')
			else:
				conn.writeCharacteristic(handle,value)
			conn.disconnect()
		except Exception,e:
			logging.error('Oups ' +str(e))
			conn.disconnect()
		return
	def intToStr(self,s):
		return "".join("{:02x}".format(ord(c)) for c in str(s).rjust(3,'0'))

globals.COMPATIBILITY.append(DreamScreen)
