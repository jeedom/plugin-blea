# coding: utf-8
from bluepy import btle
import time
import logging
import globals
from multiconnect import Connector
import struct
import utils

class YeelightCandela():
	def __init__(self):
		self.name = 'yeelight_ms'
		self.ignoreRepeat = True
		self.key = '000abf684a8000000000000000000000'

	def isvalid(self,name,manuf='',data=''):
		if 'yeelight_ms' in [name.lower()] or name.lower()==self.name:
			return True
	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		return action
	
	def action(self,message):
		logging.debug('toto')
		type =''
		mac = message['device']['id']
		handle = message['command']['handle']
		value = message['command']['value']
		if 'type' in message['command']:
			type = message['command']['type']
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
		if type == 'pair':
			conn.writeCharacteristic('0x12','4367'+self.key)
			time.sleep(5)
		if type == 'switch':
			conn.writeCharacteristic('0x12','4367'+self.key)
			conn.writeCharacteristic(handle,value.ljust(36,'0'))
		if type == 'color':
			conn.writeCharacteristic('0x12','4367'+self.key)
			if value == '000000':
				conn.writeCharacteristic(handle,('434002').ljust(36,'0'))
			else:
				conn.writeCharacteristic(handle,('4341'+value).ljust(36,'0'))
		if type == 'brightness':
			init = utils.tuple_to_hex(struct.unpack('18B',conn.readCharacteristic('0x12')))
			conn.writeCharacteristic('0x12','4367'+self.key)
			if str(init)[0:4]=='4343':
				logging.debug(str(init)[0:8])
				conn.writeCharacteristic(handle,str(init)[0:8]+ hex(int(value))[2:].zfill(2)+ str(init)[10:36])
			else:
				conn.writeCharacteristic(handle,str(init)[0:12]+ hex(int(value))[2:].zfill(2)+ str(init)[14:36])
		if type == 'white':
			conn.writeCharacteristic('0x12','4367'+self.key)
			logging.debug('4343'+ (hex(int(value))[2:].zfill(4)+ '00').ljust(36,'0'))
			conn.writeCharacteristic(handle,('4343'+ hex(int(value))[2:].zfill(4)+ '00').ljust(36,'0'))
		conn.disconnect()
		return
	
	def read(self,mac,connection=''):
		result={}
		try:
			if mac in globals.KEEPED_CONNECTION:
				logging.debug('Already a connection for ' + mac + ' use it')
				conn = globals.KEEPED_CONNECTION[mac]
			else:
				if connection != '':
					conn = connection
				else:
					logging.debug('Creating a new connection for ' + mac)
					conn = Connector(mac)
					globals.KEEPED_CONNECTION[mac]=conn
					conn.connect()
			if not conn.isconnected:
				conn.connect()
				if not conn.isconnected:
					return
			refreshlist = globals.KNOWN_DEVICES[mac]['refreshlist']
			logging.debug('Here is the list to refresh ' + str(refreshlist))
			if 'color' in refreshlist:
				try:
					color = utils.tuple_to_hex(struct.unpack('4B',conn.readCharacteristic(refreshlist['color'])))
					if color[0:2] != '00':
						color = 'FFFFFF'
					else:
						color = color[2:]
					result['color'] = '#'+color
				except Exception,e:
					logging.debug(str(e))
			if 'effect' in refreshlist:
				try:
					effect = utils.tuple_to_hex(struct.unpack('8B',conn.readCharacteristic(refreshlist['effect'])))
					mode = effect[8:10]
					if mode == '04':
						result['mode'] = 'Bougie'
					elif mode =='01':
						result['mode'] = 'Fondu uni'
					elif mode =='00':
						result['mode'] = 'Flash uni'
					elif mode =='02':
						result['mode'] = 'Flash arc-en-ciel'
					elif mode =='03':
						result['mode'] = 'Fondu arc-en-ciel'
					else:
						result['mode'] = 'Aucun'
					speed = 255-int(effect[12:14],16)
					result['speed'] = speed
				except Exception,e:
					logging.debug(str(e))
			if 'battery' in refreshlist:
				try:
					if 'hasbatteryinfo' in refreshlist and refreshlist['hasbatteryinfo'] == 1:
						battery = struct.unpack('2B',conn.readCharacteristic(refreshlist['battery']))
					else:
						battery = struct.unpack('1B',conn.readCharacteristic(refreshlist['battery']))
					result['battery'] = battery[0]
					if 'hasbatteryinfo' in refreshlist and refreshlist['hasbatteryinfo'] == 1:
						if battery[1]:
							result['mode'] = result['mode'] + ' (En charge)'
						else:
							result['mode'] = result['mode'] + ' (En décharge)'
				except Exception,e:
					logging.debug(str(e))
		except Exception,e:
			logging.debug(str(e))
			conn.disconnect()
			return
		logging.debug(str(result))
		conn.disconnect()
		result['id'] = mac
		return result

globals.COMPATIBILITY.append(YeelightCandela)