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

	def connect(self,retry=5):
		logging.debug('Connecting : '+str(self.mac) + ' with bluetooth ' + str(globals.IFACE_DEVICE))
		i=0
		while True:
			i = i + 1
			try:
				connection = btle.Peripheral(self.mac,iface=globals.IFACE_DEVICE)
				self.isconnected = True
				break
			except Exception,e:
				logging.debug(str(e) + ' attempt ' + str(i) )
				if i >= retry:
					self.isconnected = False
					return
				time.sleep(1)
		if self.isconnected:
			self.conn = connection
			logging.debug('Connected... ' + str(self.mac))
		return
		
	def disconnect(self,force=False):
		if self.mac in globals.KNOWN_DEVICES and globals.KNOWN_DEVICES[self.mac]['islocked'] == 1 and globals.KNOWN_DEVICES[self.mac]['emitterallowed'] == globals.daemonname and force==False:
			logging.debug('Not Disconnecting I\'m configured to keep connection with this device... ' + str(self.mac))
			return
		logging.debug('Disconnecting... ' + str(self.mac))
		i=0
		while True:
			i = i + 1
			try:
				self.conn.disconnect()
				break
			except Exception,e:
				logging.debug(str(e) + ' attempt ' + str(i) )
				if i >= 5:
					self.isconnected = False
					return
				time.sleep(1)
		if self.mac in globals.KEEPED_CONNECTION:
			del globals.KEEPED_CONNECTION[self.mac]
		self.isconnected = False
		logging.debug('Disconnected...'+ str(self.mac))

	def readCharacteristic(self,handle,retry=4):
		logging.debug('Reading Characteristic...'+ str(self.mac))
		ireadCharacteristic=0
		while True:
			ireadCharacteristic = ireadCharacteristic + 1
			try:
				result = self.conn.readCharacteristic(int(handle,16))
				break
			except Exception,e:
				logging.debug(str(e))
				if ireadCharacteristic >= retry:
					self.disconnect(True)
					return False
				logging.debug('Retry connection '+ str(self.mac))
				self.connect()
		logging.debug('Characteristic Readen .... ' + str(self.mac))
		return result

	def writeCharacteristic(self,handle,value,retry=4):
		logging.debug('Writing Characteristic... ' + str(self.mac))
		iwriteCharacteristic=0
		while True:
			iwriteCharacteristic = iwriteCharacteristic + 1
			try:
				arrayValue = [int('0x'+value[i:i+2],16) for i in range(0, len(value), 2)]
				self.conn.writeCharacteristic(int(handle,16),struct.pack('<%dB' % (len(arrayValue)), *arrayValue))
				break
			except Exception,e:
				logging.debug(str(e))
				if iwriteCharacteristic >= retry:
					self.disconnect(True)
					return False
				logging.debug('Retry connection ' + str(self.mac))
				self.connect()
		logging.debug('Characteristic written... ' + str(self.mac))
		return True
	
	def getCharacteristics(self,handle='',handleend='',retry=2):
		logging.debug('Getting Characteristics... ' + str(self.mac))
		if handleend == '':
			handleend = handle
		igetCharacteristics=0
		while True:
			igetCharacteristics = igetCharacteristics + 1
			try:
				if handle == '':
					char = self.conn.getCharacteristics()
					break
				else:
					char = self.conn.getCharacteristics(int(handle,16), int(handleend,16)+4)
					break
			except Exception,e:
				logging.debug(str(e))
				if igetCharacteristics >= retry:
					self.disconnect(True)
					return False
				logging.debug('Retry connection ' + str(self.mac))
				self.connect()
		logging.debug('Characteristics gotten... '+ str(self.mac))
		return char