from bluepy import btle
import time
import logging
import globals
from multiconnect import Connector
import struct

class Playbulb():
	def __init__(self):
		self.name = 'playbulb'

	def isvalid(self,name,manuf=''):
		if manuf.lower().startswith("4d49504f57") or name.lower().startswith('playbulb'):
			return True
	def parse(self,data,mac):
		action={}
		action['present'] = 1
		if mac.upper() not in globals.KNOWN_DEVICES and globals.LEARN_MODE:
			action['version'] = 'candle'
			versionDict ={'BTL300_v5' : 'candle',
						'BTL300_v6': 'candle6',
						'BTL300': 'candle6',
						'BTL301W_v5':'sphere',
						'BTL301WM_V1.7' : 'sphere17',
						'BTL400_V3.7':'garden',
						'BTL400':'garden'}
			version = self.findVersion(mac)
			if version in versionDict:
				action['version'] = versionDict[version]
			else:
				action['version'] = 'candle'
		return action
	
	def findVersion(self,mac):
		conn = Connector(mac)
		conn.connect()
		value=''
		characteristics = conn.getCharacteristics()
		for char in characteristics:
			try:
				if char.supportsRead():
					value = char.read()
					if value[0:3] == 'BTL':
						break
			except Exception,e:
				continue
		conn.disconnect()
		return value
	
	def action(self,message):
		type =''
		mac = message['device']['id']
		handle = message['command']['handle']
		value = message['command']['value']
		if 'type' in message['command']:
			type = message['command']['type']
		conn = Connector(mac)
		init = self.read(conn,handle)
		if type == 'speed':
			speed = 255-int(value);
			if speed == 0: 
				speed = 1
			value = str(init)[0:12]+ hex(speed)[2:].zfill(2)+ str(init)[14:16]
		elif type == 'effect':
			initcolor = self.read(conn,message['command']['color'])
			value = str(initcolor) + value + '00' + str(init)[12:16]
		elif type == 'color':
			initeffect = self.read(conn,message['command']['effect'])
			if str(initeffect)[8:10] == '04':
				valueprep = str(initeffect)[0:8] + '01' + '00' + str(initeffect)[12:16]
				conn.writeCharacteristic(message['command']['effect'],valueprep)
		elif type == 'luminosity':
			value = self.getTintedColor(message['command']['secondary'],value)
		arrayValue = [int('0x'+value[i:i+2],16) for i in range(0, len(value), 2)]
		while True:
			i = i + 1
			try:
				conn.writeCharacteristic(handle,value)
				break
			except Exception,e:
				if i >= 10 :
					return
		color = self.read(conn,handle)
		conn.disconnect()
		return
		
	def read(self,conn,handle):
		try:
			value = struct.unpack('<4B',conn.readCharacteristic(handle))
		except:
			value = struct.unpack('<8B',conn.readCharacteristic(handle))
		color=''
		for x in value:
			itercolor = "%x" % x
			color = color + itercolor.zfill(2)
		return color
	
	def getTintedColor(self,color,lum):
		initColor = color
		color = color.replace('#','')
		lum = float(lum)/100
		if lum == 1:
			return initColor
		logging.debug(str(color) + ' ' + str(lum))
		rgb = "";
		for i in range(0,4):
			c = int(color[i*2:i*2+2], 16)
			c = int(min(max(0,(c * lum)), 255))
			rgb = rgb + hex(c)[2:].zfill(2)
		return rgb

globals.COMPATIBILITY.append(Playbulb)