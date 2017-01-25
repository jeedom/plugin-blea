# coding: utf-8
from bluepy import btle
import time
import logging
import globals
import struct
import binascii
import base64
from multiconnect import Connector
from notification import Notification

class Miband2():
	def __init__(self):
		self.name = 'miband2'

	def isvalid(self,name,manuf=''):
		if name.lower() in ['mi band 2','mi2a',self.name]:
			return True
			
	def parse(self,data,mac,name):
		action={}
		action['present'] = 1
		if mac.upper() not in globals.KNOWN_DEVICES and globals.LEARN_MODE:
			if name.lower() in ['mi band 2','mi2a']:
				action['version'] = 'miband2'
		return action
	
	def read(self,mac):
		result={}
		try:
			conn = Connector(mac)
			conn.connect(type='random')
			if not conn.isconnected:
				conn.connect(type='random')
				if not conn.isconnected:
					return
			batteryDatas = bytearray(conn.readCharacteristic('0x43',type='random'))
			if len(batteryDatas) >= 11:
				battery = batteryDatas[1]
				status = batteryDatas[2]
				cycle = batteryDatas[7] + batteryDatas[8]
				year = str(int(str(hex(batteryDatas[12])[2:].zfill(2) + hex(batteryDatas[11])[2:].zfill(2)),16))
				month = str(batteryDatas[13]) 
				day = str(batteryDatas[14])
				hour = str(batteryDatas[15])
				minutes = str(batteryDatas[16])
				seconds = str(batteryDatas[17])
				lastchargelevel = str(batteryDatas[19])
				if status == 0:
					status = 'Débranché'
				elif status ==1:
					status = 'En charge'
				else:
					status = 'Inconnu'
				result['battery'] = battery
				result['status'] = status
				result['firmware'] = str(conn.readCharacteristic('0x10'))+'/'+str(conn.readCharacteristic('0x12'))
				result['lastchargelevel'] = lastchargelevel
				result['lastcharge'] = day+'/'+month+'/'+year+' '+hour+'h'+minutes+'min'+seconds+'s'
			result['id'] = mac
			#conn.writeCharacteristic('0x51','0100',type='random')
			#notification = Notification(conn,Miband2,{'action':'write','handle':'0x3d','value':'02','type':'random'})
			#notification.subscribe(10)
			#conn.writeCharacteristic('0x50', '0200',type='random')
			logging.debug(str(result))
		except Exception,e:
			logging.error(str(e))
		return result

globals.COMPATIBILITY.append(Miband2)
