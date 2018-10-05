from bluepy import btle
import time
import logging
import globals
import struct
import math
from multiconnect import Connector
from notification import Notification

class ParrotPlant():
	def __init__(self):
		self.ignoreRepeat = False
		self.characteristicHandles = {}

	def parse(self,data,mac,name,manuf):
		logging.debug('parse: data: '+str(data)+', mac: '+str(mac)+', name: '+str(name))
		action={}
		action['present'] = 1
		return action

	def action(self,message):
		logging.debug('action:  '+str(message))
		mac = message['device']['id']
		handle = message['command']['handle']
		value = message['command']['value']
		try:
			conn = Connector(mac)
			conn.connect()
			if not conn.isconnected:
				conn.connect()
				if not conn.isconnected:
					return
			conn.writeCharacteristic(handle,value)
			logging.debug('action:  (done) '+str(message))
		except Exception,e:
			logging.error(str(e))


	def read(self,mac):
		logging.debug('read: '+mac)
		result={}
		try:
			conn = Connector(mac)
			conn.connect()
			if not conn.isconnected:
				conn.connect()
				if not conn.isconnected:
					return
			result['sunlight'] = self.__convertSunlightData(conn.readCharacteristic(self.characteristicHandles['sunlight']))
			result['soilec'] = self.__convertSoilECData(conn.readCharacteristic(self.characteristicHandles['soilec']))
			result['soiltemp'] = self.__convertTempData(conn.readCharacteristic(self.characteristicHandles['soiltemp']))
			result['airtemp'] = self.__convertTempData(conn.readCharacteristic(self.characteristicHandles['airtemp']))
			result['soilmoisture'] = self.__convertSoilMoistureData(conn.readCharacteristic(self.characteristicHandles['soilmoisture']))
			result['calibratedsoilmoisture'] = self.__convertFloatData(conn.readCharacteristic(self.characteristicHandles['calibratedsoilmoisture']))
			result['calibratedairtemp'] = self.__convertFloatData(conn.readCharacteristic(self.characteristicHandles['calibratedairtemp']))
			result['calibratedli'] = self.__convertFloatData(conn.readCharacteristic(self.characteristicHandles['calibratedli']))
			result['color'] = self.__convertColorData(conn.readCharacteristic(self.characteristicHandles['color']))
			result['battery'] = self.__convertBatteryData(conn.readCharacteristic(self.characteristicHandles['battery']))
			result['id'] = mac
			logging.debug(str(result))
			return result
		except Exception,e:
			logging.error(str(e))
		return result

	def __convertSunlightData(self,data):
		return round(10981.31391 * math.exp(1.0/float(self.__safeUnpack('<H', data))) - 10981.3812,2)

	def __convertSoilECData(self,data):
		# TODO
		result = self.__safeUnpack('<H', data)
		return result

	def __convertTempData(self,data):
		return round(0.0473711045 * float(self.__safeUnpack('<H', data)) - 11.19891627,2)

	def __convertSoilMoistureData(self,data):
		return round(0.179814297 * float(self.__safeUnpack('<H', data)) - 40.76741498,2)

	def __convertFloatData(self,data):
		return round(self.__safeUnpack('f', data),2)

	def __convertColorData(self,data):
		choices = {
			4: 'brown',
			6: 'green',
			7: 'blue'
		}
		return choices.get(self.__safeUnpack('<H', data), 'unknown')

	def __convertBatteryData(self,data):
		return self.__safeUnpack('B', data)

	def __safeUnpack(self,fmt,data):
		try:
			return struct.unpack(fmt, data)[0]
		except Exception,e:
			logging.error(str(e))
		return 0

class FlowerPower(ParrotPlant):
	def __init__(self):
		self.name = 'flowerpower'
		self.ignoreRepeat = False
		self.characteristicHandles = {
			'sunlight': '0x25',
			'soilec': '0x29',
			'soiltemp': '0x2d',
			'airtemp': '0x31',
			'soilmoisture': '0x35',
			'calibratedsoilmoisture': '0x3f',
			'calibratedairtemp': '0x43',
			'calibratedli': '0x47',
			'color': '0x85',
			'battery': '0x4c'
		}

	def isvalid(self,name,manuf='',data=''):
		return str(name).startswith('Flower power')

globals.COMPATIBILITY.append(FlowerPower)

class ParrotPot(ParrotPlant):
	def __init__(self):
		self.name = 'parrotpot'
		self.ignoreRepeat = False
		self.characteristicHandles = {
			'sunlight': '0x25',
			'soilec': '0x31',
			'soiltemp': '0x34',
			'airtemp': '0x37',
			'soilmoisture': '0x3a',
			'calibratedsoilmoisture': '0x41',
			'calibratedairtemp': '0x44',
			'calibratedli': '0x47',
			'color': '0x72',
			'battery': '0x4b'
		}

	def isvalid(self,name,manuf='',data=''):
		return str(name).startswith('Parrot pot')

globals.COMPATIBILITY.append(ParrotPot)
