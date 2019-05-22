from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals
import struct
from multiconnect import Connector

class Hector():
	def __init__(self):
		self.name = 'hector'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data=''):
		if name.lower() == self.name:
			return True
			
	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
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
			battery = struct.unpack('2B',conn.readCharacteristic('0x2e'))
                        battery = int(str(hex(battery[0])[2:].zfill(2) + hex(battery[1])[2:].zfill(2)),16)
			temperature = struct.unpack('2B',conn.readCharacteristic('0x34'))
			temperature = int(str(hex(temperature[0])[2:].zfill(2) + hex(temperature[1])[2:].zfill(2)),16)
			humidity = struct.unpack('2B',conn.readCharacteristic('0x3c'))
			humidity = int(str(hex(humidity[0])[2:].zfill(2) + hex(humidity[1])[2:].zfill(2)),16)
                        # If pression == Ox00014601 (83457) -> read again at least for 3 attempts
			# Hector's sensor seems to always return Ox00014601 at first read attempt
			pression = struct.unpack('4B',conn.readCharacteristic('0x44'))
			pression = int(str(hex(pression[0])[2:].zfill(2) + hex(pression[1])[2:].zfill(2)+ hex(pression[2])[2:].zfill(2)+ hex(pression[3])[2:].zfill(2)),16)
                        pression_read = 0
                        while (pression <= 83457 and pression_read < 3):
                            time.sleep(1)
                            pression = struct.unpack('4B',conn.readCharacteristic('0x44'))
			    pression = int(str(hex(pression[0])[2:].zfill(2) + hex(pression[1])[2:].zfill(2)+ hex(pression[2])[2:].zfill(2)+ hex(pression[3])[2:].zfill(2)),16)
                            pression_read += 1
			logging.debug(str(pression))
			result['temperature'] = float(temperature)/10
			result['humidity'] = float(humidity)/10
			result['pressure'] = float(pression)/100
			result['batteryvoltage'] = round(float(battery)*0.00051029,2)
			if round(float(battery)*0.00051029,2) > 3:
				battery = 100
			elif round(float(battery)*0.00051029,2) < 2:
				battery = 0
			else:
				battery = round((float(battery)*0.00051029 - 2) *100,0)
			result['battery'] = battery
		except Exception,e:
			logging.error('HECTOR------'+str(e))
			conn.disconnect()
		conn.disconnect()
		result['id'] = mac
		return result

globals.COMPATIBILITY.append(Hector)
