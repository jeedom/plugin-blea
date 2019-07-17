# coding: utf-8
from bluepy import btle
import time
import logging
import globals
from multiconnect import Connector
import struct
import utils


COLOR_CHARACTERISTIC_UUID = btle.UUID("0000fffc-0000-1000-8000-00805f9b34fb")
EFFECT_CHARACTERISTIC_UUID = btle.UUID("0000fffb-0000-1000-8000-00805f9b34fb")

class Playbulb():
	def __init__(self):
		self.name = 'playbulb'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if manuf.lower().startswith("4d49504f57") or name.lower().startswith('playbulb'):
			return True
	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		return action

	def findCharacteristics(self,mac,conn=''):
		logging.debug("Searching characteristics")
		if conn == '':
			conn = Connector(mac)
			conn.connect()
		if not conn.isconnected:
			conn.connect()
			if not conn.isconnected:
				return
		value=''
		characteristics=[]
		try:
			characteristics = conn.conn.getCharacteristics(0x0001)
		except Exception,e:
			logging.debug(str(e))
			try:
				characteristics = conn.conn.getCharacteristics(0x0001)
			except Exception,e:
				logging.debug(str(e))
				try:
					characteristics = conn.conn.getCharacteristics(0x0001)
				except Exception,e:
					logging.debug(str(e))
					conn.disconnect()
		color_characteristic = next(iter(filter(lambda el: el.uuid == COLOR_CHARACTERISTIC_UUID, characteristics)))
		effect_characteristic = next(iter(filter(lambda el: el.uuid == EFFECT_CHARACTERISTIC_UUID, characteristics)))
		logging.debug('Found ' + hex(color_characteristic.getHandle()) + ' ' + hex(effect_characteristic.getHandle()))
		return [hex(color_characteristic.getHandle()),hex(effect_characteristic.getHandle())]

	def action(self,message):
		type =''
		mac = message['device']['id']
		value = message['command']['value']
		chars=[]
		if 'type' in message['command']:
			type = message['command']['type']
		if mac in globals.KEEPED_CONNECTION:
			logging.debug('Already a connection for ' + mac + ' use it')
			conn = globals.KEEPED_CONNECTION[mac]
		else:
			logging.debug('Creating a new connection for ' + mac)
			conn = Connector(mac)
			conn.connect()
		if not conn.isconnected:
			conn.connect()
			if not conn.isconnected:
				return
		if (mac.upper() in globals.KNOWN_DEVICES):
			if ('specificconfiguration' in globals.KNOWN_DEVICES[mac.upper()] and len(globals.KNOWN_DEVICES[mac.upper()]['specificconfiguration']) >0):
				logging.debug('Already known handles ' + str(globals.KNOWN_DEVICES[mac.upper()]['specificconfiguration']))
				chars = [globals.KNOWN_DEVICES[mac.upper()]['specificconfiguration']['colorhandle'],globals.KNOWN_DEVICES[mac.upper()]['specificconfiguration']['effecthandle']]
		if chars == []:
			logging.debug('Not known handles searching')
			chars = self.findCharacteristics(mac,conn)
			globals.JEEDOM_COM.add_changes('devices::'+mac,{"id" : mac,"specificconfiguration" : {"colorhandle" : chars[0], "effecthandle" : chars[1] }})
		char = chars[0]
		if type == 'speed':
			char = chars[1]
			init = utils.tuple_to_hex(struct.unpack('8B',conn.readCharacteristic(chars[1])))
			speed = 255-int(value);
			if speed == 0:
				speed = 1
			value = str(init)[0:12]+ hex(speed)[2:].zfill(2)+ str(init)[14:16]
		elif type == 'effect':
			char = chars[1]
			init = utils.tuple_to_hex(struct.unpack('8B',conn.readCharacteristic(chars[1])))
			initcolor = utils.tuple_to_hex(struct.unpack('4B',conn.readCharacteristic(chars[0])))
			value = str(initcolor) + value + '00' + str(init)[12:16]
		elif type == 'color':
			char = chars[0]
			initeffect = utils.tuple_to_hex(struct.unpack('8B',conn.readCharacteristic(chars[1])))
			if str(initeffect)[8:10] == '04':
				valueprep = str(initeffect)[0:8] + 'ff' + '00' + str(initeffect)[12:16]
				result = conn.writeCharacteristic(chars[1],valueprep)
				if not result:
					conn.disconnect()
					logging.debug("Failed to write to device probably bad bluetooth connection")
		elif type == 'luminosity':
			value = utils.getTintedColor(message['command']['secondary'],value)
		arrayValue = [int('0x'+value[i:i+2],16) for i in range(0, len(value), 2)]
		result = conn.writeCharacteristic(char,value)
		if not result:
			result = conn.writeCharacteristic(char,value)
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
		chars=[]
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
					conn.connect()
			if not conn.isconnected:
				conn.connect()
				if not conn.isconnected:
					return
			if (mac in globals.KNOWN_DEVICES):
				if ('specificconfiguration' in globals.KNOWN_DEVICES[mac] and len(globals.KNOWN_DEVICES[mac]['specificconfiguration'])>0):
					logging.debug('Already known handles ' + str(globals.KNOWN_DEVICES[mac]['specificconfiguration']))
					chars = [globals.KNOWN_DEVICES[mac]['specificconfiguration']['colorhandle'],globals.KNOWN_DEVICES[mac]['specificconfiguration']['effecthandle']]
			if chars == []:
				logging.debug('Not known handles searching')
				chars = self.findCharacteristics(mac,conn)
				globals.JEEDOM_COM.add_changes('devices::'+mac,{"id" : mac,"specificconfiguration" : {"colorhandle" : chars[0], "effecthandle" : chars[1] }})
			char = chars[0]
			refreshlist = globals.KNOWN_DEVICES[mac]['refreshlist']
			logging.debug('Here is the list to refresh ' + str(refreshlist))
			if 'color' in refreshlist:
				try:
					color = utils.tuple_to_hex(struct.unpack('4B',conn.readCharacteristic(chars[0])))
					if color[0:2] != '00':
						color = 'FFFFFF'
					else:
						color = color[2:]
					result['color'] = '#'+color
				except Exception,e:
					logging.debug(str(e))
			if 'effect' in refreshlist:
				try:
					effect = utils.tuple_to_hex(struct.unpack('8B',conn.readCharacteristic(chars[1])))
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
