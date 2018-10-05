from bluepy import btle
import time
import logging
import globals
import struct
import base64
import math
import utils
from multiconnect import Connector
from notification import Notification

class Ruuvi():
	def __init__(self):
		self.name = 'ruuvi'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data=''):
		if data[0:4] == 'aafe' or manuf[0:4] in ['9904']:
			return True

	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		if data and data[0:4] == 'aafe':
			toanalyze =''
			base16_split = [data[i:i + 2] for i in range(0, len(data), 2)]
			selected_hexs = filter(lambda x: int(x, 16) < 128, base16_split)
			characters = [chr(int(c, 16)) for c in selected_hexs]
			joined = ''.join(characters)
			index = joined.find('ruu.vi/#')
			if index > -1:
				toanalyze = joined[(index + 8):]
			else:
				index = joined.find('r/')
				if index > -1:
					toanalyze = joined[(index + 2):]
			if toanalyze != '':
				toanalyze=toanalyze[:8]
				decoded = bytearray(base64.b64decode(toanalyze, '-_'))
				temp = (decoded[2] & 127) + decoded[3] / 100.00
				sign = (decoded[2] >> 7) & 1
				if sign == 0:
					temp = round(temp, 2)
				else:
					temp = round(-1 * temp, 2)
				humidity = decoded[1] * 0.5
				pres = (((decoded[4] << 8) + decoded[5]) + 50000) /100.00
				action['temperature'] = temp
				action['humidity'] = humidity
				action['pression'] = pres
		elif manuf and "990403" in manuf :
			payload_start = manuf.index("990403") + 4
			string = manuf[payload_start:]
			analyze = bytearray.fromhex(string)
			temp = (analyze[2] & ~(1 << 7)) + (analyze[3] / 100.00)
			sign = (analyze[2] >> 7) & 1
			if sign == 0:
				temp = round(temp, 2)
			else:
				temp = round(-1 * temp, 2)
			humidity = analyze[1] * 0.5
			pres = ((analyze[4] << 8) + analyze[5] + 50000)/100.00
			accx = utils.twos_complement((analyze[6] << 8) + analyze[7], 16)/1000.00
			accy = utils.twos_complement((analyze[8] << 8) + analyze[9], 16)/1000.00
			accz = utils.twos_complement((analyze[10] << 8) + analyze[11], 16)/1000.00
			battery = ((analyze[12] << 8) + analyze[13])/1000.00
			action['temperature'] = temp
			action['humidity'] = humidity
			action['pression'] = pres
			action['accx'] = accx
			action['accy'] = accy
			action['accz'] = accz
			action['acceleration'] = round(math.sqrt(accx * accx + accy * accy + accz * accz),2)
			action['battery'] = battery
		elif manuf and "990405" in manuf :
			payload_start = manuf.index("990405") + 4
			string = manuf[payload_start:]
			analyze = bytearray.fromhex(string)
			if analyze[1:2] == 0x7FFF:
				temp = None
			else :
				temperature = utils.twos_complement((analyze[1] << 8) + analyze[2], 16) / 200
				temp = round(temperature,2)
			if analyze[3:4] == 0xFFFF:
				humidity = None
			else:
				humidity = round(((analyze[3] & 0xFF) << 8 | analyze[4] & 0xFF) / 400,2)
			if analyze[5:6] == 0xFFFF:
				pres = None
			else :
				pressure = ((data[5] & 0xFF) << 8 | data[6] & 0xFF) + 50000
				pres = round((pressure / 100), 2)
		return action


globals.COMPATIBILITY.append(Ruuvi)