from bluepy import btle
import time
import logging
import globals
import struct
from multiconnect import Connector
from notification import Notification

class Miflora():
	def __init__(self):
		self.name = 'ropot'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data=''):
		validname = ['ropot']
		if name in validname:
			return True
	def parse(self,data,mac,name,manuf):
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
			conn.writeCharacteristic('0x33','a01f',response=True)
			battery = batteryFirm[0]
			firmware = "".join(map(chr, batteryFirm[2:]))
			notification = Notification(conn,Miflora)
			conn.writeCharacteristic('0x36','0100',response=True)
			notification.subscribe(2)
			result['battery'] = battery
			result['firmware'] = firmware
			result['id'] = mac
			logging.debug(str(result))
			return result
		except Exception,e:
			logging.error(str(e))
		return result
	
	def handlenotification(self,conn,handle,data,action={}):
		result={}
		if hex(handle) == '0x35':
			received = bytearray(data)
			temperature = float(received[1] * 256 + received[0]) / 10
			sunlight = received[4] * 256 + received[3]
			moisture = received[7]
			fertility = received[9] * 256 + received[8]
			result['sunlight'] = sunlight
			result['moisture'] = moisture
			result['fertility'] = fertility
			result['temperature'] = temperature
			result['id'] = conn.mac
			result['source'] = globals.daemonname
			globals.JEEDOM_COM.add_changes('devices::'+conn.mac,result)

globals.COMPATIBILITY.append(Miflora)