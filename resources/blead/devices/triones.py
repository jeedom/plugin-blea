from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals
import binascii
from multiconnect import Connector

class Triones():
	def __init__(self):
		self.name = 'triones_rgb'
		self.ignoreRepeat = True

	def isvalid(self,name,manuf='',data=''):
		if name.lower() in [self.name,'triones']:
			return True

	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		return action

	def action(self,message):
		mac = message['device']['id']
		handle = message['command']['handle']
		value = message['command']['value']
		repeat=0
		if 'repeat' in message['command']:
			repeat = int(message['command']['repeat'])
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
		if repeat != 0:
			conn.writeCharacteristic('Ox12','010000000000000000000d0a')
			time.sleep(2)
			for x in range(repeat):
				conn.writeCharacteristic(handle,value)
				time.sleep(0.4)
		else:
			conn.writeCharacteristic(handle,value)
		conn.disconnect()
		return

globals.COMPATIBILITY.append(Triones)
