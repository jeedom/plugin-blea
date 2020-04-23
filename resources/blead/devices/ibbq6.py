# coding: utf-8
from bluepy import btle
import time
import logging
import globals
import struct
from multiconnect import Connector
from notification import Notification

class Ibbq4():
	def __init__(self):
		self.name = 'ibbq6'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if name.lower() in [self.name,'ibbq']:
			return True

	def parse(self,data,mac,name,manuf):
		logging.debug('IBBQ ' + data +' '+manuf)
		action={}
		t1 = manuf[22:24] + manuf[20:22]
		t2 = manuf[26:28] + manuf[24:26]
		t3 = manuf[30:32] + manuf[28:30]
		t4 = manuf[34:36] + manuf[32:34]
		t5 = manuf[38:40] + manuf[36:38]
		t6 = manuf[44:48] + manuf[40:44]
		temp1=int(t1,16)/10.0
		temp2=int(t2,16)/10.0
		temp3=int(t3,16)/10.0
		temp4=int(t4,16)/10.0
		temp5=int(t5,16)/10.0
		temp6=int(t6,16)/10.0
		if temp1 < 1500:
			action['temp1'] = temp1
		else:
			action['temp1'] = -1
		if temp2 < 1500:
			action['temp2'] = temp2
		else:
			action['temp2'] = -1
		if temp3 < 1500:
			action['temp3'] = temp3
		else:
			action['temp3'] = -1
		if temp4 < 1500:
			action['temp4'] = temp4
		else:
			action['temp4'] = -1
		if temp5 < 1500:
			action['temp5'] = temp5
		else:
			action['temp5'] = -1
		if temp6 < 1500:
			action['temp6'] = temp6
		else:
			action['temp6'] = -1
		action['present'] = 1
		return action

	def read(self,mac):
		result={}
		#account verify : 0x29
		#realtimedata : 0x30
		#settings : 0x34
		#settingsresult : 0x25
		#historydata : 0x2c
		#
		#credentials :  0x21, 0x07, 0x06, 0x05, 0x04, 0x03, 0x02, 0x01, 0xb8, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00
		#
		#enablerealtime : 0x0B, 0x01, 0x00, 0x00, 0x00, 0x00
		#
		#units celcisu : 0x02, 0x00, 0x00, 0x00, 0x00, 0x00
		# defini seuil : dans 0x34 ecrire 010X48f4YYYY  avec x numero de sonde (commencant a 0) et y temperature x10 inverse
		#
		#0x31 0100 activer notif temp
		#batterie 0x34 082400000000
		try:
			conn = Connector(mac)
			conn.connect()
			if not conn.isconnected:
				conn.connect()
				if not conn.isconnected:
					return
			conn.writeCharacteristic('0x29','2107060504030201b8220000000000',response=True)
			notification = Notification(conn,Ibbq6)
			conn.writeCharacteristic('0x26','0100',response=True)
			conn.writeCharacteristic('0x34','082400000000',response=True)
			notification.subscribe(10)
			return result
		except Exception as e:
			logging.error(str(e))
		return result

	def action(self,message):
		if 'type' in message['command']:
			type = message['command']['type']
		mac = message['device']['id']
		data={}
		data['source'] = globals.daemonname
		data['id'] = mac
		data['sendstatus'] = '-'
		globals.JEEDOM_COM.add_changes('devices::'+mac,data)
		handle = message['command']['handle']
		value = message['command']['value']
		conn = Connector(mac)
		conn.connect()
		if not conn.isconnected:
			data['sendstatus'] = 'KO'
			globals.JEEDOM_COM.add_changes('devices::'+mac,data)
			return
		conn.writeCharacteristic('0x29','2107060504030201b8220000000000',response=True)
		if type == 'setTarget':
			logging.debug('IBBQ set Target for probe ' + message['command']['probe'] + ' value ' + value)
			valuetohex = hex(int(value)*10)[2:].zfill(4)
			towrite = '010'+message['command']['probe']+'48f4'+valuetohex[2:4]+valuetohex[0:2]
			logging.debug('IBBQ writing ' + towrite + ' on handle ' + handle)
			conn.writeCharacteristic(handle,towrite,response=True)
			data['sendstatus'] = 'OK'
			globals.JEEDOM_COM.add_changes('devices::'+mac,data)
		conn.disconnect()
		return

	def handlenotification(self,conn,handle,data,action={}):
		result={}
		logging.debug('IBBQ NOTIFICATION :' +str(handle) + ' '+ str(data.hex()))

globals.COMPATIBILITY.append(Ibbq6)
