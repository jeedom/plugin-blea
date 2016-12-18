from bluepy import btle
import time
import logging
import globals
import struct
from multiconnect import Connector

class Miflora():
	def __init__(self):
		self.name = 'miflora'

	def isvalid(self,name,manuf=''):
		validname = ['Flower mate','Flower care']
		if name in validname:
			return True
	def parse(self,data,mac):
		action={}
		action['present'] = 1
		return action

	def read(self,mac):
		result={}
		try:
			conn = Connector(mac)
			conn.connect()
			if not conn.isconnected:
				conn.connect()
				if not conn.isconnected:
					return
			batteryFirm = bytearray(conn.readCharacteristic('0x38'))
			value = 'A01F'
			conn.writeCharacteristic('0x33',value)
			datas = conn.readCharacteristic('0x35')
			conn.disconnect()
			received = bytearray(datas)
			logging.debug(str(received))
			battery = batteryFirm[0]
			firmware = "".join(map(chr, batteryFirm[2:]))
			temperature = float(received[1] * 256 + received[0]) / 10
			sunlight = received[4] * 256 + received[3]
			moisture = received[7]
			fertility = received[9] * 256 + received[8]
			result['battery'] = battery
			result['firmware'] = firmware.replace('\x10','')
			result['sunlight'] = sunlight
			result['moisture'] = moisture
			result['fertility'] = fertility
			result['temperature'] = temperature
			result['id'] = mac
			logging.debug(str(result))
			return result
		except Exception,e:
			logging.error(str(e))
		return result

globals.COMPATIBILITY.append(Miflora)
