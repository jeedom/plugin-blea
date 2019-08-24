from bluepy import btle
import time
import logging
import globals
import struct
from multiconnect import Connector
from notification import Notification

class Miflora():
	def __init__(self):
		self.name = 'miflora'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		validname = ['Flower mate','Flower care',self.name]
		if name in validname:
			return True
	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		try:
			if data.lower().startswith("95fe"):
				##todo parse data
				logging.debug('Xiaomi Flower Care PARSE data: ' + data ) 
				val_type = data[28:30].lower()
				val_len =  data[32:34]
				val_data = data[34:]
				if val_type in ['04']:	 # type: temperature
					t_data = int(val_data[2:4]+val_data[0:2],16)
					temp = t_data/10.0
					if temp>3276.8:
						temp = 0-(6553.6 - temp)
					logging.debug('XiaomiFlower------ Advertising Data=> Temp' + str(temp))
					action['temperature'] = temp
				elif val_type in ['06']: # type: humidity
					h_data = int(val_data[2:4]+val_data[0:2],16)
					hum = h_data/10.0
					logging.debug('XiaomiFlower------ Advertising Data=> Humidity: ' + str(hum))
					action['humidity'] = hum
				elif val_type in ['07']: # type: illuminance
					h_data = int(val_data[4:6]+val_data[2:4]+val_data[0:2],16)
					ill = h_data
					logging.debug('XiaomiFlower------ Advertising Data=> Illuminance: ' + str(ill))
					action['sunlight'] = ill
				elif val_type in ['08']: # type: moisture
					h_data = int(val_data[2:4]+val_data[0:2],16)
					moist = h_data
					logging.debug('XiaomiFlower------ Advertising Data=> Moist: ' + str(moist))
					action['moisture'] = moist
				elif val_type in ['09']: # type: fertility
					h_data = int(val_data[2:4]+val_data[0:2],16)
					fert = h_data
					logging.debug('XiaomiFlower------ Advertising Data=> Fertility: ' + str(fert))
					action['fertility'] = fert
				elif val_type in ['0a']: # type: battery
					b_data = val_data[0:2]
					batt = int(b_data,16)
					logging.debug('XiaomiFlower------ Advertising Data=> Batt: ' + str(batt))
					action['battery'] = batt
				elif val_type in ['0d']: # type: temp&moist
					t_data = int(val_data[2:4]+val_data[0:2],16)
					temp = t_data/10.0
					if temp>3276.8:
						temp = 0-(6553.6 - temp)
					h_data = int(val_data[6:8]+val_data[4:6],16)
					hum = h_data/10.0
					logging.debug('XiaomiFlower------ Advertising Data=> Temp: ' + str(temp) + ' Moist: ' + str(hum))
					action['temperature'] = temp
					action['moisture'] = hum
		except Exception as e:
			logging.error(str(e))
		except Exception as e:
			logging.debug('SCANNER------Parse failed ' +str(mac) + ' ' + str(e))
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
			result['battery'] = battery
			result['firmware'] = firmware
			result['id'] = mac
			received = bytearray(conn.readCharacteristic('0x35'))
			temperature = float(received[1] * 256 + received[0]) / 10
			if temperature>3276.8:
				temperature = 0-(6553.6 - temperature)
			sunlight = received[4] * 256 + received[3]
			moisture = received[7]
			fertility = received[9] * 256 + received[8]
			result['sunlight'] = sunlight
			result['moisture'] = moisture
			result['fertility'] = fertility
			result['temperature'] = temperature
			result['source'] = globals.daemonname
			logging.debug(str(result))
			globals.JEEDOM_COM.add_changes('devices::'+conn.mac,result)
			return result
		except Exception as e:
			logging.error(str(e))
		return result
	
	def handlenotification(self,conn,handle,data,action={}):
		result={}

globals.COMPATIBILITY.append(Miflora)
