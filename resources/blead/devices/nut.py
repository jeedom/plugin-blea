from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals
from multiconnect import Connector

class Nut():
	def __init__(self):
		self.name = 'nut'

	def isvalid(self,name,manuf=''):
		if name.lower() == self.name:
			return True
			
	def parse(self,data,mac,name):
		action={}
		action['present'] = 1
		return action
	
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
		conn.writeCharacteristic(handle,value)
		conn.disconnect()
		return

globals.COMPATIBILITY.append(Nut)