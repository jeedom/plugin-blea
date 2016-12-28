# coding: utf-8
from bluepy import btle
import time
import logging
import globals
import struct
import binascii
from multiconnect import Connector
from notification import Notification

class Miband():
	def __init__(self):
		self.name = 'miband'

	def isvalid(self,name,manuf=''):
		if name.lower() in ['mi1a','mi1s', 'mi',self.name]:
			return True
			
	def parse(self,data,mac,name):
		action={}
		action['present'] = 1
		if mac.upper() not in globals.KNOWN_DEVICES and globals.LEARN_MODE:
			if name.lower() in ['mi1a']:
				action['version'] = 'miband1'
			elif name.lower() in ['mi1s']:
				action['version'] = 'miband1s'
			elif name.lower() in ['mi']:
				action['version'] = 'mibandcolor'
		return action
	
	def action(self,message):
		mac = message['device']['id']
		handle = message['command']['handle']
		value = message['command']['value']
		conn = Connector(mac)
		conn.connect()
		if not conn.isconnected:
			return
		conn.writeCharacteristic(handle,value)
		conn.disconnect()
		return
	
	def read(self,mac):
		result={}
		try:
			conn = Connector(mac)
			conn.connect()
			if not conn.isconnected:
				conn.connect()
				if not conn.isconnected:
					return
			batteryDatas = bytearray(conn.readCharacteristic('0x2c'))
			if len(batteryDatas) == 10:
				battery = batteryDatas[0]
				status = batteryDatas[9]
				cycle = batteryDatas[7] + batteryDatas[8]
				year = str(batteryDatas[1] +2000)
				month = str(batteryDatas[2]+1) 
				day = str(batteryDatas[3])
				hour = str(batteryDatas[4])
				minutes = str(batteryDatas[5])
				seconds = str(batteryDatas[6])
				if status == 1:
					status = 'Faible'
				elif status ==2:
					status = 'En charge'
				elif status ==3:
					status = 'Branché Full'
				elif status ==4:
					status = 'Débranché'
				else:
					status = 'Inconnu'
				result['battery'] = battery
				result['status'] = status
				result['cycle'] = cycle
				result['lastcharge'] = day+'/'+month+'/'+year+' '+hour+'h'+minutes+'min'+seconds+'s'
			firmwareDatas = bytearray(conn.readCharacteristic('0x12'))
			firmware = str(firmwareDatas[15])+'.'+str(firmwareDatas[14])+'.'+str(firmwareDatas[13])+'.'+str(firmwareDatas[12])
			stepsDatas = conn.readCharacteristic('0x1d')
			steps = ord(stepsDatas[0]) + (ord(stepsDatas[1]) << 8)
			result['steps'] = steps
			result['firmware']=firmware
			result['id'] = mac
			logging.debug(str(result))
			return result
		except Exception,e:
			logging.error(str(e))
			conn.disconnect()
		conn.disconnect()
		return result
	
	def handlenotification(self,conn,handle,data):
		result={}
		result['button'] = 1
		result['id'] = conn.mac
		result['source'] = globals.daemonname
		globals.JEEDOM_COM.add_changes('devices::'+conn.mac,result)

globals.COMPATIBILITY.append(Miband)
