from bluepy import btle
import time
import logging
import globals
import binascii
from multiconnect import Connector
import struct

class Smartplug():
	def __init__(self):
		self.name = 'smartplug'

	def isvalid(self,name,manuf=''):
		if name.lower().startswith("smp-b16-") or name.lower() == 'smartplug':
			return True
			
	def parse(self,data,mac,name):
		action={}
		action['present'] = 1
		return action
		
	def connect(self,mac):
		logging.debug('Connecting : '+str(mac) + ' with bluetooth ' + str(globals.IFACE_DEVICE))
		i=0
		while True:
			i = i + 1
			try:
				conn = btle.Peripheral(mac,iface=globals.IFACE_DEVICE)
				break
			except Exception, e:
				logging.error(str(e))
				if i >= 4 :
					return
		return conn
	
	def action(self,message):
		mac = message['device']['id']
		handle = message['command']['handle']
		value = message['command']['value']
		conn = Connector(mac)
		conn.connect()
		conn.writeCharacteristic(handle,value)
		conn.disconnect()
		logging.debug('Value ' + value + ' written in handle ' +handle)
		logging.debug('Refreshing ... ')
		result = self.read(mac)
		return result
	
	def read(self,mac):
		global result
		result={}
		try:
			conn = self.connect(mac)
			logging.debug('Connected...')
			value = '0f050400000005ffff'
			arrayValue = [int('0x'+value[i:i+2],16) for i in range(0, len(value), 2)]
			svc = conn.getServiceByUUID('0000fff0-0000-1000-8000-00805f9b34fb')
			cmd_ch = svc.getCharacteristics('0000fff3-0000-1000-8000-00805f9b34fb')[0]
			delegate = NotificationDelegate()
			conn.setDelegate(delegate)
			conn.writeCharacteristic(0x2b,struct.pack('<%dB' % (len(arrayValue)), *arrayValue))
			if conn.waitForNotifications(0.5):
				if result:
					result['id'] = mac
			conn.disconnect()
			logging.debug(str(result))
			return result
		except Exception,e:
			try:
				conn.disconnect()
			except Exception,e:
				pass
			logging.error(str(e))
		return result
		
class NotificationDelegate(btle.DefaultDelegate):
	def __init__(self):
		btle.DefaultDelegate.__init__(self)

	def handleNotification(self, cHandle, data):
		state = False
		global result
		result  = {}
		bytes_data = bytearray(data)
		if bytes_data[0:3] == bytearray([0x0f, 0x0f, 0x04]):
			state = bytes_data[4] == 1
			power = int(binascii.hexlify(bytes_data[6:10]), 16) / 1000
			result['power'] = power
			if state:
				result['status'] = 1
			else:
				result['status'] = 0

globals.COMPATIBILITY.append(Smartplug)