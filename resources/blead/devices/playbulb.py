# coding: utf-8
from bluepy import btle
import time
import logging
import globals
from multiconnect import Connector
import struct
import utils

class Playbulb():
	def __init__(self):
		self.name = 'playbulb'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data=''):
		if manuf.lower().startswith("4d49504f57") or name.lower().startswith('playbulb'):
			return True
	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		try:
			if mac.upper() not in globals.KNOWN_DEVICES and globals.LEARN_MODE:
				action['version'] = 'candle'
				versionDict ={'btl300_v5' : 'candle',
							'btl300_v6': 'candle6',
							'btl301w_v5':'sphere',
							'btl301w':'sphere',
							'btl301wm_v1.7' : 'sphere17',
							'btl400_v3.7':'garden',
							'btl400m_v1.9':'garden19',
							'btl201_v2': 'bluelabel'}
				version = self.findVersion(mac)
				logging.debug("Found " + str(version).lower())
				if not version or version == '':
					logging.debug("Not able to have consistent info from playbulb device")
					return
				if version.lower() in versionDict:
					action['version'] = versionDict[version.lower()]
				else:
					action['version'] = 'candle'
		except Exception,e:
				logging.debug("Not able to have consistent info from playbulb device")
		return action
	
	def findVersion(self,mac):
		conn = Connector(mac)
		conn.connect()
		if not conn.isconnected:
			conn.connect()
			if not conn.isconnected:
				return
		value=''
		characteristics = conn.getCharacteristics()
		for char in characteristics:
			try:
				if char.supportsRead():
					valueChar = char.read()
					if valueChar and valueChar[0:3] == 'BTL' and len(valueChar)>6 and len(valueChar)>len(value):
						value = valueChar
			except Exception,e:
				continue
		conn.disconnect()
		return value
	
	def action(self,message):
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
		if type == 'speed':
			init = utils.tuple_to_hex(struct.unpack('8B',conn.readCharacteristic(handle)))
			speed = 255-int(value);
			if speed == 0: 
				speed = 1
			value = str(init)[0:12]+ hex(speed)[2:].zfill(2)+ str(init)[14:16]
		elif type == 'effect':
			init = utils.tuple_to_hex(struct.unpack('8B',conn.readCharacteristic(handle)))
			initcolor = utils.tuple_to_hex(struct.unpack('4B',conn.readCharacteristic(message['command']['color'])))
			value = str(initcolor) + value + '00' + str(init)[12:16]
		elif type == 'color':
			initeffect = utils.tuple_to_hex(struct.unpack('8B',conn.readCharacteristic(message['command']['effect'])))
			if str(initeffect)[8:10] == '04':
				valueprep = str(initeffect)[0:8] + 'ff' + '00' + str(initeffect)[12:16]
				result = conn.writeCharacteristic(message['command']['effect'],valueprep)
				if not result:
					conn.disconnect()
					logging.debug("Failed to write to device probably bad bluetooth connection")
		elif type == 'luminosity':
			value = utils.getTintedColor(message['command']['secondary'],value)
		arrayValue = [int('0x'+value[i:i+2],16) for i in range(0, len(value), 2)]
		result = conn.writeCharacteristic(handle,value)
		if not result:
			result = conn.writeCharacteristic(handle,value)
			if not result:
				logging.debug("Failed to write to device probably bad bluetooth connection")
		data={}
		data = self.read(mac,conn)
		if len(data)>2:
			data['source'] = globals.daemonname
			if type == 'luminosity':
				data['luminosity'] = luminosityvalue
			globals.JEEDOM_COM.add_changes('devices::'+mac,data)
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

globals.COMPATIBILITY.append(Playbulb)