# coding: utf-8
import logging
import globals
from multiconnect import Connector

class SensirionMyCO2():
    
	def __init__(self):
		self.name = 'sensirionmyco2'
		self.ignoreRepeat = False

	def isvalid(self, name, manuf='', data='', mac=''):
		validname = ['MyCO2']
		sensirion_companyId = '0x06D5' # Sensirion
		if name in validname:
			return True		
		if self._get_companyId(manuf) == sensirion_companyId:
			return True
		return False

	def _get_companyId(self, manuf):
		return f'0x{manuf[2:4].upper()}{manuf[0:2].upper()}'

	def parse(self, data, mac, name, manuf):
		action={}
		action['present'] = 1
		try:	
			logging.debug('Sensirion MyCO2 PARSE raw %s %s man_spec_data: %s', mac, name, manuf)			
			companyId = self._get_companyId(manuf)
			advertisementType = int(manuf[4:6])
			advSampleType = int(manuf[6:8])
			deviceId = f'{manuf[8:10]}:{manuf[10:12]}'.upper() # as shown in Sensirion MyAmbience app (last 4 bytes of MAC address)						
			logging.debug('Sensirion MyCO2 PARSE => deviceId: %s, Type: %s, SampleType: %s, companyId: %s', deviceId, advertisementType, advSampleType, companyId)
			# CO2_UUID 00007001-b38d-4985-720e-0f993a68ee41
			# TEMPERATURE_UUID 00002235-b38d-4985-720e-0F993a68ee41
			# HUMIDITY_UUID 00001235-b38d-4985-720e-0F993a68ee41
			if(advertisementType == 0):
				byte_data = manuf[12:]
				if(advSampleType == 8):
					temperature = round((int.from_bytes(bytearray.fromhex(byte_data[0:4]), byteorder='little') / 65535) * 175 - 45, 1)        
					humidity = round((int.from_bytes(bytearray.fromhex(byte_data[4:8]), byteorder='little')  / 65535) * 100, 0)
					raw_co2 = bytearray.fromhex(byte_data[8:12])
					co2 = int.from_bytes(raw_co2, byteorder='little')  
					logging.debug('Sensirion MyCO2------ Advertising Data=> CO2: %s, Temperature: %s, Humidity: %s', co2, temperature, humidity)
					action['co2'] = co2
					action['temperature'] = temperature
					action['moisture'] = humidity
		except Exception as e:
			logging.error('Sensirion MyCO2 PARSE error: %s', e)
		logging.debug(str(action))
		return action

	def read(self, mac):
		result={}
		try:
			conn = Connector(mac)
			conn.connect(type='random')
			if not conn.isconnected:
				conn.connect(type='random')
				if not conn.isconnected:
					return			
			result['id'] = mac
			logging.debug('Sensirion MyCO2 connected ------ %s', result)
			return result
		except Exception as e:
			logging.error('Sensirion MyCO2 read ------ %s', e)
		return result

globals.COMPATIBILITY.append(SensirionMyCO2)
