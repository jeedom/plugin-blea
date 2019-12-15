# coding: utf-8
from bluepy import btle
import time
import logging
import globals
from multiconnect import Connector
import struct
import utils

class BeeWiSmartLite():
	def __init__(self):
		self.name = 'beewismartlite'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if manuf[0:8] == '0d000603':
			return True
		if name.lower() == self.name:
			return True
		self.log('manuf: '+manuf+' name:'+ name + ' data:'+data)
		return False

	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		return action

	#logs a debug message
	def log(self, logmessage):
		logging.debug('BeeWiSmartLite------'+ logmessage)
		return

	#writes a command to the bulb
	def writeCommandToBulb(self, conn, command):
		# settings commands are sent to the 0x0021 characteristic
		# all commands are prefixed with 0x55 (85) and suffixed with 0x0d 0x0a (CR LF)
		if command != '' :
			command = '55' + command + '0D0A'
		self.log('sending command ' + command + ' to handle 0X0021')
		conn.writeCharacteristic('0x0021',command)
		return
	
	#reads settings from the bulb
	def readSettings(self, conn):
		settings = [0,0,0,0,0]
		raw_data=conn.readCharacteristic('0x0024').hex()
		self.log('read characteristic: ' + raw_data)
		for i in range(0, 5) :
			j = int(raw_data[0+(i*2):2+(i*2)], 16)
			settings[i] = j

		result={}

		if (settings[0] % 2) == 1:
			result['state'] = 1
		else:
			result['state'] = 0
		if result['state'] == 1:
			result['white'] = (settings[1] & 15) > 0
			brightness = (((settings[1] & 240) >> 4) - 1)
			if brightness < 0 :
				brightness = 0
			result['brightness'] = brightness
			tone = (settings[1] & 15) - 2
			if tone < 0 :
				tone = 0
			result['tone'] = tone
			result['color'] = '#%02x%02x%02x' % (settings[2], settings[3], settings[4])
		else:
			result['white'] = False
			result['brightness'] = 0
			result['tone'] = 0
			result['color'] = '#000000'
			
		self.log('read settings')
		self.log('state: ' + str(result['state']))
		self.log('white: ' + str(result['white']))
		self.log('brightness: ' + str(result['brightness']))
		self.log('tone: ' + str(result['tone']))
		self.log('color: ' + result['color'])
		return result
	
	#get level to set in a command
	def getLevel(self,value, offset = 2):
		level = (int(float(value)))
		if level > 11 - offset :
			level = 11 - offset
		level = level + offset
		return ('%02x' % level).upper()

	def setBrightness(self, conn, value) :
		# brightness command is 12 [02 to 0B] (18, [2 to 11])
		level = self.getLevel(value, 1)
		self.writeCommandToBulb(conn, '12' + level)

	def setBulbWhiteTone(self, conn, tone) :
		# brightness command is 11 [02 to 0B] (17, [2 to  11])
		level = self.getLevel(tone)
		self.writeCommandToBulb(conn, '11' + level)

	def setBulbWhite(self, conn) :
		# set to white command is 14 FF FF FF (20, -128, -128, -128)
		self.writeCommandToBulb(conn, '14FFFFFF')

	def setBulbColor(self, conn, color) :
		# colour command is 13 RR GG BB (19, Red, Green, Blue)
		value = '13' + color
		self.writeCommandToBulb(conn, value)

	def switchBulbOn(self, conn) :
		# on command is 10 01 (16, 1)
		self.writeCommandToBulb(conn, '1001')

	def switchBulbOff(self, conn) :
		# off command is 10 00 (16, 0)
		self.writeCommandToBulb(conn, '1000')

	def launchSequence(self, conn, value) :
		# sequence command is 17 [08 to 0C] (23 [8 to 12])
		seqNo = '%02x' % (8 + int(value))
		self.writeCommandToBulb(conn, '17' + seqNo)

	#execute a command
	def action(self,message):
		type =''
		mac = message['device']['id']
		value = message['command']['value']
		if 'type' in message['command']:
			type = message['command']['type']
		if mac in globals.KEEPED_CONNECTION:
			self.log('Already a connection for ' + mac + ' use it')
			conn = globals.KEEPED_CONNECTION[mac]
		else:
			self.log('Creating a new connection for ' + mac)
			conn = Connector(mac)
			conn.connect()
		if not conn.isconnected:
			conn.connect()
			if not conn.isconnected:
				return
		settings = self.readSettings(conn)
		
		# Turn On
		if type == 'switchon' :
			self.switchBulbOn(conn)

		# Turn Off
		elif type == 'switchoff' :
			self.switchBulbOff(conn)

		# Toggle On/Off
		elif type == 'toggle' :
			if settings['state'] == 0 :
				self.switchBulbOn(conn)
			else :
				self.switchBulbOff(conn)

		# Brightness
		elif type == 'brightness' :
			if value == '0' :
				self.switchBulbOff(conn)
			else :
				if settings['state'] == 0 :
					self.switchBulbOn(conn)
				self.setBrightness(conn,value)

		elif settings['state'] == 1 :

			# White tone
			if type == 'tone' :
				self.setBulbWhiteTone(conn,value)

			# white mode
			elif type == 'white' :
				self.setBulbWhite(conn)

			# color mode
			elif type == 'color' :
				if value == '000000':
					self.setBulbWhite(conn)
				else:
					self.setBulbColor(conn, value)

			# sequence
			elif type == 'sequence' :
				self.launchSequence(conn, value)

		time.sleep(0.1)
		result=self.readSettings(conn)
		result['id'] = mac

		conn.disconnect()
		return result

	def read(self,mac,connection=''):
		result={}
		try:
			if mac in globals.KEEPED_CONNECTION:
				self.log('Already a connection for ' + mac + ' use it')
				conn = globals.KEEPED_CONNECTION[mac]
			else:
				if connection != '':
					conn = connection
				else:
					self.log('Creating a new connection for ' + mac)
					conn = Connector(mac)
					conn.connect()
			if not conn.isconnected:
				conn.connect()
			try:
				if not conn.isconnected:
					result['state'] = 0
					result['white'] = False
					result['brightness'] = 0
					result['tone'] = 0
					result['color'] = '#000000'
				else:
					result = self.readSettings(conn)
			except Exception as e:
				self.log(str(e))
		except Exception as e:
			self.log(str(e))
			if conn.isconnected:
				conn.disconnect()
			return
			
		if conn.isconnected:
			conn.disconnect()
		result['id'] = mac
		return result

globals.COMPATIBILITY.append(BeeWiSmartLite)