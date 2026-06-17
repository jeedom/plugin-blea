# coding: utf-8
import logging
import globals
import utils

class WiserShutter():
	def __init__(self):
		self.name = 'wisershutter'
		self.ignoreRepeat = False
		self.handles = {
			# standard fields
			'device_name' : '0x03',
			'apparence'   : '0x05',
			'model_number': '0x08',
			'firmware_revision':'0x0a',
			'manufacturer_name':'0x0c',
			# schneider fields
			'request_service'  :'0x0f',
			'response_service' :'0x12',
			'notice_service'   :'0x16',
			'firmware_version' :'0x1a',
			'ble_control_point':'0x1d',
			'access_level'     :'0x20', # 0 = not paired, 1 = paired
			# probably firmware update fields (no name in gatt): 0x25 + 0x27
			# control fields
			'on_off'           :'0x2b',
			'set_level'        :'0x2f',
			'relative_operations':'0x33',
			'blue_roc'         :'0x37'
		}
		self.notifications = {
			'response_service' :'0x13',
			'notice_service'   :'0x17',
			'access_level'     :'0x21',
			'on_off'           :'0x2c',
			'set_level'        :'0x30',
			'relative_operations':'0x34',
			'blue_roc'         :'0x38'
		}
		self.statusNames = {
			'opened' : 'Ouvert',
			'closed' : 'Fermé',
			'opening' : 'Ouverture',
			'closing' : 'Fermeture',
			'middle'  : 'Mi ouvert',
			'unknown' : 'Inconnu'
		}
		self.notifier = None

	def readStatus(self, conn):
		if conn and conn.isconnected:
			name = bytearray(conn.readCharacteristic(self.handles['device_name']))
			level =  bytearray(conn.readCharacteristic(self.handles['access_level']))
			paired = False
			nameStr = ''
			if len(level) > 0 and len(name) > 0:
				paired= bool(level[0])
				nameStr = name.decode()
				logging.info('WiserShutter--readStatus() : read name=%s and paired=%s', nameStr, str(paired))
			else:
				logging.error('WiserShutter--readStatus() : error read current status for %s!')
				return None
			return(nameStr,paired)
		return None
		
	def sendConfigTime(self,mac,conn,value):
		logging.info('WiserShutter--sendConfigTime() : Configure time to %s',value)
		# value has format HHMM
		valInt = int(value)
		minutes = int(valInt / 100)
		secondes = valInt % 100
		valSend = '{:0>4X}'.format(minutes * 60 + secondes)
		written = conn.writeCharacteristic(self.handles['request_service'],'FFFF09FF108000000102'+valSend,retry=3,response=True)
		logging.debug('WiserShutter--sendConfigTime() : Configured time to %s=%s',valSend,str(written))
		return written

	def sendCmdPosition(self, mac, conn, value):
		logging.info('WiserShutter--sendCmdPosition() : Set position to %s ',value)
		# position is from 0 to 10000 (0x2710 => send 0x1027)
		hexe = '{:0>4X}'.format(int(value) * 100)
		# reverse ordre byte
		valSend = hexe[2:4] + hexe[0:2]
		written = conn.writeCharacteristic(self.handles['set_level'],valSend,retry=3,response=True)
		logging.debug('WiserShutter--sendCmdPosition() : Set position to %s=%s',valSend,str(written))
		return written

	def initConnection(self, mac):
		logging.debug('WiserShutter--initConnection() for %s ', mac)
		tupleVal = utils.getConnection(mac)
		if tupleVal:
			(conn, reuse) = tupleVal
			tupleVal = self.readStatus(conn)
			if tupleVal:
				(name, paired) = tupleVal
				if paired:
					logging.debug('WiserShutter--initConnection(): success %s for %s ',name, mac)
					return (conn,name)
				else:
					logging.error("WiserShutter--initConnection(): Action received on not appaired shutter %s, do nothing !", mac)
					return (None,None)
		return (None,None)

	def sendCommand(self,mac,action,value = None):
		result={}
		try:
			globals.PENDING_ACTION = True
			globals.KNOWN_DEVICES[mac.upper()]['islocked'] = 1
			
			logging.debug('WiserShutter--sendCommand() : %s on %s', action, mac)
			(conn,name) = self.initConnection(mac)
			if conn:
				written = None
				if action == 'up':
					logging.debug('WiserShutter--sendCommand() : UP')
					written = conn.writeCharacteristic(self.handles['relative_operations'],'01',retry=3,response=True)
				elif action == 'down':
					logging.debug('WiserShutter--sendCommand() : DOWN')
					written = conn.writeCharacteristic(self.handles['relative_operations'],'02',retry=3,response=True)
				elif action == 'stop':
					logging.debug('WiserShutter--sendCommand() : STOP')
					written = conn.writeCharacteristic(self.handles['relative_operations'],'00',retry=3,response=True)
				elif action == 'position':
					if value == None:
						logging.error('WiserShutter--sendCommand() : Missing Position in command !')
					else:
						written = self.sendCmdPosition(mac, conn, value)
				elif action == 'time_movement':
					if value == None:
						logging.error('WiserShutter--sendCommand() : Missing Time in command !')
					else:
						written= self.sendConfigTime(mac, conn, value)
				if not(written):
					logging.error('WiserShutter--sendCommand() : Action %s writed: %s for %s',action, str(written), mac)
				else:
					logging.info('WiserShutter--sendCommand() : Action %s writed: %s for %s',action, str(written), mac)
			else:
				logging.error('WiserShutter--sendCommand() : Failed to initConnection for %s', mac)

		except Exception as e:
			logging.exception(e)
			

		finally:
			globals.PENDING_ACTION = False
		#	globals.KNOWN_DEVICES[mac.upper()]['islocked'] = 0
			if conn and conn.isconnected:
				logging.debug('WiserShutter--sendCommand() close connection')
				conn.disconnect()
		return result
		
	def isvalid(self,name,manuf='',data='',mac=''):
		if name.lower() == self.name or manuf[0:14] == 'b602010020000b':
			logging.debug('WiserShutter--isValid()=true : name=%s manuf=%s data=%s mac=%s', name, manuf, data, mac)
			return True
		return False

	def parse(self,data,mac,name,manuf):
		result={}
		logging.debug('WiserShutter--parse() : name=%s manuf=%s data=%s mac=%s', name, manuf, data, mac)
		operation = manuf[16:18]
		position = manuf[18:20]
		# appairing = 
		# b6-02-01-00-20-00-0b-00-00-00-00-09-07-00-01-0000000000000000000000
		# standard status = 
		# b6-02-01-00-20-00-0b-00-00-00-00-09-06-00-00-0000000000000000000000
		status = manuf[24:26]
		logging.debug('WiserShutter--parse() : operation=%s position=%s',operation,position)
		status = None

		if status == '07':
			logging.info('WiserShutter--parse() : Appairing in progress ... please start refresh.')
		else:
			if operation == '00':
				if position == '00':
					status = 'opened'
				elif position == 'ff':
					status = 'closed'
				else:
					status = 'middle'
			elif operation =='01':
				result['button'] = 'up'
				status = 'opening'
			elif operation =='02':
				result['button'] = 'down'
				status = 'closing'
			elif operation =='03':
				result['button'] = 'up_short'
			elif operation =='04':
				result['button'] = 'down_short'
			
		if status in ['opened','closed','middle']:
			globals.KNOWN_DEVICES[mac.upper()]['islocked'] = 0

		if status != None:
			result['status'] = status
			result['label'] = self.statusNames[status]

		result['position'] = int((int(position, 16) / 255.0)*100.0)
		result['present'] = 1
		result['id'] = mac
		logging.debug("WiserShutter--parse() : %s", str(result))
		return result
	
	def action(self,message):
		logging.debug("WiserShutter--action(): %s", str(message))
		mac = message['device']['id']
		
		
		action = message['command']['action']
		if action == 'up':
			self.sendCommand(mac, 'up')
		elif action == 'down':
			self.sendCommand(mac, 'down')
		elif action == 'stop':
			self.sendCommand(mac, 'stop')
		elif action == 'position':
			value = message['command']['value']
			self.sendCommand(mac, 'position', value)
		elif action == 'time_movement':
			value = message['command']['value']
			self.sendCommand(mac, 'time_movement', value)
		else:
			logging.error('WiserShutter--action() : Action %s unknown for %s', action, mac)
		
	
	def read(self,mac):
		result={}
		result['id'] = mac

		try:
			globals.PENDING_ACTION = True
		#	globals.KNOWN_DEVICES[mac.upper()]['islocked'] = 1

			(conn,name) = self.initConnection(mac)
			if conn:
				result['present'] = 1
				result['paired'] = True
				result['localname'] = name
			# init error or read status error
			else:
				result['present'] = 0
				logging.error('WiserShutter--read() : Failed to initConnection or read status for %s', mac)
		except Exception as e:
			result['present'] = 0
			logging.exception(e)
		finally:
			
			globals.PENDING_ACTION = False
		#	globals.KNOWN_DEVICES[mac.upper()]['islocked'] = 0
			#if conn.isconnected:
			#	logging.debug('WiserShutter--sendCommand() close connection')
			#	conn.disconnect()
		return result

globals.COMPATIBILITY.append(WiserShutter)