from bluepy import btle
import time
import logging
import globals
from multiconnect import Connector

BATTERY_CHARACTERISTIC_UUID=btle.UUID("00002a19-0000-1000-8000-00805f9b34fb")

class Nut():
	def __init__(self):
		self.name = 'nut'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if name.lower() == self.name:
			return True

	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		return action
	
	def findCharacteristics(self,mac,conn=''):
		logging.debug("Searching characteristics")
		if conn == '':
			conn = Connector(mac)
			conn.connect(type='random')
		if not conn.isconnected:
			return
		value=''
		characteristics=[]
		try:
			characteristics = conn.conn.getCharacteristics(0x0001)
		except Exception as e:
			logging.debug(str(e))
			try:
				characteristics = conn.conn.getCharacteristics(0x0001)
			except Exception as e:
				logging.debug(str(e))
				try:
					characteristics = conn.conn.getCharacteristics(0x0001)
				except Exception as e:
					logging.debug(str(e))
					conn.disconnect()
		battery_characteristic = next(iter(filter(lambda el: el.uuid == BATTERY_CHARACTERISTIC_UUID, characteristics)))
		logging.debug('Found ' + hex(battery_characteristic.getHandle()))
		return [hex(battery_characteristic.getHandle())]

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
					conn.connect(type='random')
			if not conn.isconnected:
				return
			if (mac in globals.KNOWN_DEVICES):
				if ('specificconfiguration' in globals.KNOWN_DEVICES[mac] and len(globals.KNOWN_DEVICES[mac]['specificconfiguration'])>0):
					logging.debug('Already known handles ' + str(globals.KNOWN_DEVICES[mac]['specificconfiguration']))
					chars = [globals.KNOWN_DEVICES[mac]['specificconfiguration']['batteryhandle']]
			if chars == []:
				logging.debug('Not known handles searching')
				chars = self.findCharacteristics(mac,conn)
				globals.JEEDOM_COM.add_changes('devices::'+mac,{"id" : mac,"specificconfiguration" : {"batteryhandle" : chars[0]}})
			char = chars[0]
			batteryDatas = bytearray(conn.readCharacteristic(char,type='random'))
			logging.debug(str(batteryDatas))
			result['battery'] = batteryDatas[0]
			result['id'] = mac
			logging.debug(str(result))
			return result
		except Exception as e:
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