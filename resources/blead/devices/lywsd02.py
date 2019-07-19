# coding: utf-8
from bluepy import btle
import time
import logging
import globals
import struct
from multiconnect import Connector
from notification import Notification

class Lywsd02():
	def __init__(self):
		self.name = 'lywsd02'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if name.lower() in ['lywsd02']:
			return True
		if data.lower().startswith("95fe") and (mac.lower().startswith("3f:59:c8")):
			#broadcasted advertising data
			return True

	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		if data.lower().startswith("95fe"):
			##todo parse data
			logging.debug('Lywsd02 PARSE data: ' + data )
			val_type = data[28:30].lower()
			val_len =  data[32:34]
			val_data = data[34:42]
			if val_type in ['04']:	 # type: temperature
				t_data = val_data[2:4] + val_data[0:2]
				temp = int(t_data,16)/10.0
				logging.debug('Lywsd02------ Advertising Data=> Temp' + str(temp))
				action['temperature'] = temp
			elif val_type in ['06']: # type: moisture
				h_data = val_data[2:4] + val_data[0:2]
				hum = int(h_data,16)/10.0
				logging.debug('Lywsd02------ Advertising Data=> Moist: ' + str(hum))
				action['moisture'] = hum
			elif val_type in ['0a']: # type: battery
				b_data = val_data[0:2]
				batt = int(b_data,16)
				logging.debug('Lywsd02------ Advertising Data=> Batt: ' + str(batt))
				action['battery'] = batt
			elif val_type in ['0d']: # type: temp&moist
				 t_data = val_data[2:4] + val_data[0:2]
				 temp = int(t_data,16)/10.0
				 h_data = val_data[6:8] + val_data[4:6]
				 hum = int(h_data,16)/10.0
				 logging.debug('Lywsd02------ Advertising Data=> Temp: ' + str(temp) + ' Moist: ' + str(hum))
				 action['temperature'] = temp
				 action['moisture'] = hum
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

globals.COMPATIBILITY.append(Lywsd02)
