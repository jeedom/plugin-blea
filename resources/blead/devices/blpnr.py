from bluepy import btle
import logging
import globals
import utils
from multiconnect import Connector
from notification import Notification

class Blpnr():
	def __init__(self):
		self.name = 'blpnr'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if name.lower().startswith('blnr') or name.lower() in [self.name]:
			return True
			
	def parse(self,data,mac,name,manuf):
		logging.debug('PARSE BLPNR')
		action={}
		action['present'] = 1
		if mac not in globals.LAST_STORAGE:
			logging.debug('MODE IS ? READ BLPNR')
			globals.LAST_STORAGE[mac]={}
			self.getStatus(mac)
		return action

			  
	def action(self,message):
		logging.debug('ACTION BLPNR')
		mac = message['device']['id']
		logging.debug('MAC BLPNR '+mac)
		action = message['command']['action']
		if mac not in globals.LAST_STORAGE:
			globals.LAST_STORAGE[mac]={}
		logging.debug('action BLPNR '+action)
		handle = '0X0011'
		conn = Connector(mac)
		conn.connect(type='random')
		if not conn.isconnected:
			conn.connect(type='random')
			if not conn.isconnected:
				return
		logging.debug('connected BLPNR')
		if action == 'refresh':
			logging.debug('refresh BLPNR')
			self.getStatus(mac)
			return
		if action == 'off':
			message = '050400900000009900'
		if action == 'on':
			value = message['command']['value']
			logging.debug('value BLPNR ' + str(value))
			liste = [5,4,0,10,0,int(value),0]
			checksum1 = sum(liste)%256
			checksum2 = sum(liste)/256
			liste.append(checksum1)
			liste.append(checksum2)
			message = utils.tuple_to_hex(liste)
		conn.writeCharacteristic(handle,message)
		conn.disconnect()
		self.getStatus(mac)
			  
	def getStatus(self,mac):
		logging.debug('STATUS BLPNR')
		try:
			conn = Connector(mac)
			if not conn.isconnected:
				conn.connect(type='random')
				if not conn.isconnected:
					return
			conn.writeCharacteristic('0x000f','2902')
			conn.disconnect()
		except Exception as e:
			logging.error(str(e))
		try:
			conn = Connector(mac)
			if not conn.isconnected:
				conn.connect(type='random')
				if not conn.isconnected:
					return
			logging.debug('READ notif BLPNR')
			notification = Notification(conn,Blpnr)
			#notification.subscribe(10,disconnect=True)
			notification.subscribe() 
			conn.writeCharacteristic('0x0011','0d00000d00')
		except Exception as e:
			logging.error(str(e))

	def read(self,mac):
		logging.debug('READ BLPNR')
		if mac not in globals.LAST_STORAGE:
			logging.debug('MODE IS ? READ BLPNR')
			globals.LAST_STORAGE[mac]={}
			self.getStatus(mac)
		elif mac in globals.LAST_STORAGE and globals.LAST_STORAGE[mac] == 'True':
			logging.debug('MODE IS ON READ BLPNR')
			self.getStatus(mac)
		else:
			logging.debug('MODE IS OFF DONT READ BLPNR')
	
	def handlenotification(self,conn,handle,data={},action={}):
		logging.debug('NOTIFI BLPNR ')
		conn.disconnect()
	
		result={}
		result['id'] = conn.mac
		logging.debug('BLPNR id : '+result['id'])
		size = len(data)
		logging.debug('BLPNR data : '+str(size))
		result['source'] = globals.daemonname
		logging.debug('BLPNR source : '+result['source'])
		if (size <= 6):
			result['mode'] = 'False'
			logging.debug('BLPNR mode : '+result['mode'])
			result['battery'] = '0'
			logging.debug('BLPNR battery : '+result['battery'])
		else:
			result['temps'] = str(int(data[6].encode('hex'),16))
			logging.debug('BLPNR temps : '+result['temps'])
			tension = int(data[7].encode('hex'),16)
			logging.debug('BLPNR tension : '+str(tension))
			battery = 0			  
			if tension >= 80:
				battery = 5
			elif tension >= 75:
				battery = 4	  
			elif tension >= 70:
				battery = 3	  
			elif tension >= 65:
				battery = 2	  
			elif tension >= 60:
				battery = 1
			result['battery'] = str(tension)# str(battery * 20)			 
			logging.debug('BLPNR battery : '+result['battery'])	
			result['rssi'] = str(int(data[8].encode('hex'),16))
			result['mode'] = str((int(data[4].encode('hex'),16) > 0))
			logging.debug('BLPNR mode : '+result['mode'])
			if result['mode'] == 'False':
				result['temps'] = '0'
				logging.debug('BLPNR temps : '+result['temps'])
		globals.LAST_STORAGE[conn.mac] = result['mode']
		globals.JEEDOM_COM.add_changes('devices::'+conn.mac,result)

			  
globals.COMPATIBILITY.append(Blpnr)