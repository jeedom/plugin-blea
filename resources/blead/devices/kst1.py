from bluepy import btle
import time
import logging
import globals
from multiconnect import Connector
from notification import Notification


NOTIFICATION_CHARACTERISTIC_UUID=btle.UUID("0000fff3-0000-1000-8000-00805f9b34fb")

class KST1():
	def __init__(self):
		self.name = 'kst1'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if 'ks-t1' in name.lower() or name.lower()==self.name:
			return True
			
	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		try:
			conn = Connector(mac)
			conn.connect()
			if not conn.isconnected:
					return
			notification = Notification(conn,KST1)
			conn.writeCharacteristic('0x2c','0100',response=True)
			batteryData = (conn.readCharacteristic('0x3a')).hex()
			logging.debug(str(batteryData))
			action['battery']= int(batteryData,16)
			notification.subscribe(20)
		except Exception as e:
			logging.error(str(e))
		return action
	
	def handlenotification(self,conn,handle,data,action={}):
		result={}
		logging.debug('KST01 NOTIFICATION ' + str(data.hex())) 
		if hex(handle) == '0x2b':
			received = data.hex()
			type = str(received[-2:])
			result['mode'] = 'Oreille'
			if type == '02':
				result['mode'] = 'Front'
			temperature = round((float(int(received[4:6],16))*2.56) + (float(int(received[2:4],16))/100),2)
			result['id'] = conn.mac
			result['temperature'] = str(temperature)
			result['source'] = globals.daemonname
			globals.JEEDOM_COM.add_changes('devices::'+conn.mac,result)
globals.COMPATIBILITY.append(KST1)
