# coding: utf-8
from bluepy import btle
import time
import logging
import globals
import struct
from multiconnect import Connector
from notification import Notification

class Lywsd03():
	def __init__(self):
		self.name = 'lywsd03'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if name.lower() in [self.name]:
			return True
		if data.lower().startswith("95fe") and (mac.lower().startswith("a4:c1:38")):
			#broadcasted advertising data
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
			batt = bytearray(conn.readCharacteristic('0x3a'))
			battery = batt[0]
			notification = Notification(conn,Lywsd03)
			notification.subscribe(10)
			result['battery'] = battery
			result['id'] = mac
			logging.debug('LYWSD03------'+str(result))
			return result
		except Exception as e:
			logging.error(str(e))
		return result

	def handlenotification(self,conn,handle,data,action={}):
		result={}
		if hex(handle) == '0x36':
			received = bytearray(data)
			temperature = float(received[1] * 256 + received[0]) / 100
			moisture = received[2]
			result['moisture'] = moisture
			result['temperature'] = temperature
			result['id'] = conn.mac
			result['source'] = globals.daemonname
			globals.JEEDOM_COM.add_changes('devices::'+conn.mac,result)

globals.COMPATIBILITY.append(Lywsd03)