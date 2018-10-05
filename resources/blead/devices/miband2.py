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
try:
	from Crypto.Cipher import AES
except:
	logging.debug('No crypto ignoring it')

class Miband2():
	def __init__(self):
		self.name = 'miband2'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data=''):
		if name.lower() in ['mi band 2','mi2a',self.name]:
			return True
			
	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		if mac.upper() not in globals.KNOWN_DEVICES and globals.LEARN_MODE:
			if name.lower() in ['mi band 2','mi2a']:
				action['version'] = 'miband2'
		return action
	
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
		conn.writeCharacteristic('0x55','0100',type='random')
		notification = Notification(conn,Miband2,{'action':'write','handle':handle,'value':value,'type':'random'})
		if handle == '0x2b':
			notification.subscribe(20)
		else:
			notification.subscribe(1)
		conn.writeCharacteristic('0x54', '0200',type='random')
		return
	
	def read(self,mac):
		result={}
		try:
			conn = Connector(mac)
			conn.connect(type='random')
			if not conn.isconnected:
				conn.connect(type='random')
				if not conn.isconnected:
					return
			batteryDatas = bytearray(conn.readCharacteristic('0x47',type='random'))
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
			logging.debug(str(result))
		except Exception,e:
			logging.error(str(e))
		return result
	
	def handlenotification(self,conn,handle,data,action={}):
		result={}
		if hex(handle) == '0x54':
			conn.writeCharacteristic('0x55','0000',type='random')
			auth = binascii.hexlify(bytearray(struct.unpack('19B',data)))[-32:]
			obj = AES.new(binascii.unhexlify('5b4b29dee0ed7cadf3b402d71782024f'), AES.MODE_ECB)
			ciphertext = obj.encrypt(binascii.unhexlify(auth))
			conn.writeCharacteristic('0x50','0300'+binascii.hexlify(bytearray(ciphertext)),type='random')
			if action['handle'] == '0x2b':
				conn.writeCharacteristic('0x26','03',type=action['type'])
				conn.writeCharacteristic(action['handle'],action['value'],type=action['type'],response=True)
				conn.writeCharacteristic('0x29', '0100',response=True)
			elif action['handle'] == '0x3d':
				conn.writeCharacteristic('0x3e', '0100')
				conn.writeCharacteristic('0x41', '0100',response=True)
				conn.writeCharacteristic(action['handle'],action['value'],type=action['type'])
			else:
				conn.writeCharacteristic(action['handle'],action['value'],type=action['type'])
				conn.disconnect()
		elif hex(handle) == '0x28':
			received = bytearray(data)
			conn.writeCharacteristic('0x26','03',type=action['type'])
			conn.disconnect()
			result['heartvalue'] = received[1]
			result['id'] = conn.mac
			result['source'] = globals.daemonname
			globals.JEEDOM_COM.add_changes('devices::'+conn.mac,result)
		elif hex(handle) == '0x40':
			conn.disconnect()
			received = bytearray(data)
			logging.debug(binascii.hexlify(received))

globals.COMPATIBILITY.append(Miband2)
