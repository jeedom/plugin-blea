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
        logging.debug('Lywsd03 PARSE data: ' + data )
        temp = int.from_bytes(data[0:2],byteorder='little',signed=True)/100
        logging.debug('Lywsd03------ Advertising Data=> Temp' + str(temp))
        action['temperature'] = temp
        hum = int.from_bytes(data[2:3],byteorder='little')
        logging.debug('Lywsd03------ Advertising Data=> Moist: ' + str(hum))
        action['moisture'] = hum
        volt = int.from_bytes(data[3:5],byteorder='little') / 1000.
        batt = min(int(round((voltage - 2.1),2) * 100), 100)
        logging.debug('Lywsd03------ Advertising Data=> Batt: ' + str(batt))
        action['battery'] = batt
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
            val=b'\x01\x00'
            conn.writeCharacteristic(0x0038,val,1,True) #enable notifications of Temperature, Humidity and Battery voltage
            conn.writeCharacteristic(0x0046,b'\xf4\x01\x00',1,True)
			notification = Notification(conn,Lywsd03)
			notification.subscribe(10)
			logging.debug('LYWSD03------'+str(result))
			return result
		except Exception as e:
			logging.error(str(e))
		return result

	def handlenotification(self,conn,handle,data,action={}):
		result={}
		temperature=int.from_bytes(data[0:2],byteorder='little',signed=True)/100
        print("Temperature: " + str(temperature))
        moisture=int.from_bytes(data[2:3],byteorder='little')
        print("Humidity: " + str(moisture))
        voltage=int.from_bytes(data[3:5],byteorder='little') / 1000.
        print("Battery voltage:",voltage)
        batteryLevel = min(int(round((voltage - 2.1),2) * 100), 100) #3.1 or above --> 100% 2.1 --> 0 %
        result['moisture'] = moisture
        result['temperature'] = temperature
        result['battery'] = batteryLevel
        result['id'] = conn.mac
        result['source'] = globals.daemonname
        globals.JEEDOM_COM.add_changes('devices::'+conn.mac,result)

globals.COMPATIBILITY.append(Lywsd03)
