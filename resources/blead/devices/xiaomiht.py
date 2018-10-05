# coding: utf-8
from bluepy import btle
import time
import logging
import globals
import struct
from multiconnect import Connector
from notification import Notification

class XiaomiHT():
	def __init__(self):
		self.name = 'xiaomiht'
		self.ignoreRepeat = True

	def isvalid(self,name,manuf='',data=''):
		if name.lower() in ['mj_ht_v1']:
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
			Firm = bytearray(conn.readCharacteristic('0x24'))
			batt = bytearray(conn.readCharacteristic('0x18'))
			battery = batt[0]
			firmware = "".join(map(chr, Firm))
			notification = Notification(conn,XiaomiHT)
			conn.writeCharacteristic('0x10','0100',response=True)
			notification.subscribe(2)
			result['battery'] = battery
			result['firmware'] = firmware
			result['id'] = mac
			logging.debug('XIAOMIHT------'+str(result))
			return result
		except Exception,e:
			logging.error(str(e))
		return result
	
	def handlenotification(self,conn,handle,data,action={}):
		result={}
		if hex(handle) == '0xe':
			received = bytearray(data)
			temp,hum = "".join(map(chr, received)).replace("T=", "").replace("H=", "").rstrip(' \t\r\n\0').split(" ")
			result['moisture'] = hum
			result['temperature'] = temp
			result['id'] = conn.mac
			result['source'] = globals.daemonname
			globals.JEEDOM_COM.add_changes('devices::'+conn.mac,result)

globals.COMPATIBILITY.append(XiaomiHT)