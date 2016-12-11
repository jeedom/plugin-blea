from bluepy import btle
import time
import logging
import globals
import struct

class Connector():
	def __init__(self,mac):
		self.name = 'connector'
		self.mac = mac
		self.conn = ''
		self.isconnected = False

	def connect(self):
		logging.debug('Connecting : '+str(self.mac) + ' with bluetooth ' + str(globals.IFACE_DEVICE))
		i=0
		while True:
			i = i + 1
			try:
				connection = btle.Peripheral(self.mac,iface=globals.IFACE_DEVICE)
				break
			except Exception,e:
				if i >= 50:
					self.isconnected = False
				time.sleep(0.02)
		self.isconnected = True
		self.conn = connection
		logging.debug('Connected...')
		return
		
	def disconnect(self):
		self.conn.disconnect()
		self.isconnected = False
		logging.debug('Disconnected...')

	def readCharacteristic(self,handle):
		if not self.isconnected:
			self.connect()
		i=0
		while True:
			i = i + 1
			try:
				result = self.conn.readCharacteristic(int(handle,16))
				break
			except Exception,e:
				logging.debug(str(e))
				self.connect()
				if i >= 50:
					return
		return result

	def writeCharacteristic(self,handle,value):
		if not self.conn:
			self.connect()
		i=0
		while True:
			i = i + 1
			try:
				arrayValue = [int('0x'+value[i:i+2],16) for i in range(0, len(value), 2)]
				self.conn.writeCharacteristic(int(handle,16),struct.pack('<%dB' % (len(arrayValue)), *arrayValue))
				break
			except Exception,e:
				self.connect()
				if i >= 50:
					return
		return
		
	def getCharacteristics(self,handle='',handleend=''):
		if not self.conn:
			self.connect()
		if handleend == '':
			handleend = handle
		i=0
		while True:
			i = i + 1
			try:
				if handle == '':
					char = self.conn.getCharacteristics()
				else:
					char = self.conn.getCharacteristics(int(handle,16), int(handleend,16)+4)
				logging.debug(str(char))
				break
			except Exception,e:
				logging.debug(str(e))
				self.connect()
				if i >= 50:
					return
		return char