from bluepy import btle
import logging
import globals
import utils
from multiconnect import Connector
from notification import Notification
import traceback

STATUS_CHARACTERISTIC_UUID = btle.UUID("0000fcd9-0000-1000-8000-00805f9b34fb")

class Aqualin():
	def __init__(self):
		self.name = 'aqualin'
		self.ignoreRepeat = False
		self.characteristicHandles = {
			'program': '0x28',
			'sprayMist': '0x2b',
			'timestamp': '0x2e',
			'spray': '0x32',
			'durationSpray': '0x36',
			'cycleSpray': '0x3a',
			'start1Spray': '0x3d',
			'start2Spray': '0x40',
			'rainDelaySpray': '0x43',
			'autoOnSpray': '047',
			'autoOffSpray': '04a',
			'triggerSpray': '0x4d',
			'mist': '0x52',
			'start1Mist': '0x56',
			'end1Mist': '0x59',
			'start2Mist': '0x5c',
			'end2Mist': '0x5f',
			'durationMist': '0x62',
			'intervalMist': '0x66',
			'weekdaysCycleMist': '0x6a',
			'autoOnMist': '06d',
			'autoOffMist': '070',
			'triggerMist': '0x73',
			'battery': '0x81'
		}
		self.characteristic = {
			'program': {'handle' : '0x28', 'prefix' :'5201'},
			'sprayMist': {'handle' : '0x2b', 'prefix' :'5301'},
			'timestamp': {'handle' : '0x2e', 'prefix' :'5401'},
			'spray': {'handle' : '0x32', 'prefix' :'6101'},
			'durationSpray': {'handle' : '0x36', 'prefix' :'6202'},
			'cycleSpray': {'handle' : '0x3a', 'prefix' :'6303'},
			'dayCycleSpray': {'handle' : '0x3a', 'prefix' :'6303'},
			'weekCycleSpray': {'handle' : '0x3a', 'prefix' :'6303'},
			'weekdaysCycleSpray': {'handle' : '0x3a', 'prefix' :'6303'}, 
			'start1Spray': {'handle' : '0x3d', 'prefix' :'6402'},
			'start2Spray': {'handle' : '0x40', 'prefix' :'6502'},
			'rainDelaySpray': {'handle' : '0x43', 'prefix' :'6601'},
			'autoOnSpray': {'handle' : '047', 'prefix' :'670155'},
			'autoOffSpray': {'handle' : '04a', 'prefix' :'6801a5'},
			'triggerSpray': {'handle' : '0x4d', 'prefix' :'6903'},
			#'off': {'handle' : '0x4d', 'prefix' :'6903000000'},
			#'on': {'handle' : '0x4d', 'prefix' :'6903010000'},
			'mist': {'handle' : '0x52', 'prefix' :'7101'},
			'start1Mist': {'handle' : '0x56', 'prefix' :'7202'},
			'end1Mist': {'handle' : '0x59', 'prefix' :'7302'},
			'start2Mist': {'handle' : '0x5c', 'prefix' :'7402'},
			'end2Mist': {'handle' : '0x5f', 'prefix' :'7502'},
			'durationMist': {'handle' : '0x62', 'prefix' :'7603'},
			'intervalMist': {'handle' : '0x66', 'prefix' :'7703'},
			'weekdaysCycleMist': {'handle' : '0x6a', 'prefix' :'7801'},
			'autoOnMist': {'handle' : '06d', 'prefix' :'790155'},
			'autoOffMist': {'handle' : '070', 'prefix' :'7a01a5'},
			'triggerMist': {'handle' : '0x73', 'prefix' :'7b03'},
			'off': {'handle' : '0x73', 'prefix' :'7b03000000'},
			'on': {'handle' : '0x73', 'prefix' :'7b0301'},
			'battery': {'handle' : '0x81', 'prefix' :''}
		}
		self.countConn=0
		
	def isvalid(self, name, manuf='', data='', mac=''):
		validname = ['spray-mist 1ded',self.name]
		if name.lower().startswith('spray') or name.lower() in validname:
			return True
			
	def parse(self, data='vide', mac='?', name='??', manuf='empty'):
		action={}
		action['present'] = 1
		if (len(data)):
			logging.debug('**** Aqualin PARSE with data len : ' + str(len(data)) + ' - data =' + data + ' - name =' + name + ' - manuf =' + manuf)
		if mac not in globals.LAST_STORAGE:
			globals.LAST_STORAGE[mac]={}
			if mac in globals.LAST_STORAGE:
				logging.debug('======== now aqualin mac is in globals.last_storage but empty...')			
		return action
			  
	def action(self, message):
		try:
			mac = message['device']['id']
			logging.debug('ACTION aqualin:'+mac)
			action = message['command']['action']
			if mac not in globals.LAST_STORAGE:
				globals.LAST_STORAGE[mac]={}
			
			logging.debug('-> action aqualin ='+action)
			
			conn = self.__connect(mac, 'ACTION')
			
			if not conn:
				return False
			
			handle = self.characteristic[action]['handle']
			logging.debug('-> action aqualin handle ok ='+action)
			if 'value' in message['command'] :
				#logging.debug('-> action aqualin value exist ! ='+action)
				value = message['command']['value']
			else:
				#logging.debug('-> action aqualin value does not exist ! ='+action)
				value = ''
			logging.debug('-> action aqualin value ok ='+action)
			message = self.characteristic[action]['prefix']
			#logging.debug('-> action aqualin prefix ok ='+action)
			
			if action == 'refresh':
				logging.debug('ACTION refresh aqualin do nothing !')
				return
			
			if action == 'on':
				#handle = '0x004d'
				#value = message['command']['value']
				logging.debug('-> action value aqualin ' + value)
				hexValue = str(hex(int(value))[2:].zfill(4))
				logging.debug('-> action value aqualin ' + hexValue)
				
				#message = '690301' + hexValue
				message += hexValue
	
			elif action == 'off':
				logging.debug('===-> handle aqualin autoOnMist ' + handle)
				logging.debug('===-> action message aqualin autoOnMist ' + message)
			
			elif action == 'sprayMist':
				#handle = self.characteristic[action]['handle']
				#value = message['command']['value']
				#message = '5301'+value
				message += value
				logging.debug('-> action value aqualin sprayMist ' + message)
			
			
			elif action == 'durationSpray':
				logging.debug('===-> handle aqualin durationSpray ' + handle)
				value = value.zfill(4)
				logging.debug('===-> action value aqualin durationSpray ' + value)
				hexValue = str(hex(int(value[0:2]))[2:].zfill(2)) + str(hex(int(value[2:4]))[2:].zfill(2))
				hexValue = hexValue.zfill(4)
				logging.debug('===-> action hexvalue aqualin durationSpray ' + hexValue)
				message += hexValue
				logging.debug('===-> action message aqualin durationSpray ' + message)
				
			elif action == 'rainDelaySpray':
				logging.debug('===-> handle aqualin rainDelaySpray ' + handle)
				value = value.zfill(2)
				logging.debug('===-> action value aqualin rainDelaySpray ' + value)
				hexValue = str(hex(int(value[0:2]))[2:].zfill(2)) 
				hexValue = hexValue.zfill(2)
				logging.debug('===-> action hexvalue aqualin rainDelaySpray ' + hexValue)
				message += hexValue
				logging.debug('===-> action message aqualin rainDelaySpray ' + message)
			
			elif action == 'cycleSpray':
				#logging.debug('!!!-> start action aqualin cycleSpray ')
				oldValue = conn.readCharacteristic(self.characteristicHandles['cycleSpray'])
				logging.debug('!!!-> action old complete value aqualin cycleSpray ' + oldValue.decode())
				logging.debug('!!!-> action old complete value aqualin cycleSpray ' + str(oldValue))
				#newValue = hex(int(value[0:]))
				if value == 'day':
					newValue = '00'
				else :
					newValue = '01'
				logging.debug('!!!-> action new value aqualin cycleSpray ' + newValue)
				#logging.debug('!!!-> action new value in byte aqualin cycleSpray ' + newValue[2:])
				#newCompleteValue = hex(int(value[0:]))[2:].zfill(2)+hex(oldValue[3])[2:].zfill(2)+hex(oldValue[4])[2:].zfill(2)
				newCompleteValue = newValue+hex(oldValue[3])[2:].zfill(2)+hex(oldValue[4])[2:].zfill(2)
				
				logging.debug('!!!-> action new complete value aqualin cycleSpray ' + newCompleteValue)
				message += newCompleteValue
				logging.debug('!!!-> action value aqualin cycleSpray ' + message)
			
			elif action == 'dayCycleSpray':
				#logging.debug('!!!-> start action aqualin dayCycleSpray ')
				oldValue = conn.readCharacteristic(self.characteristicHandles['cycleSpray'])
				logging.debug('!!!-> action old complete value aqualin dayCycleSpray ' + oldValue.decode())
				logging.debug('!!!-> action old complete value aqualin dayCycleSpray ' + str(oldValue))
				newValue = hex(int(value[0:]))
				newValue = hex(int(value[0:]))[2:].zfill(2)
				logging.debug('!!!-> action new value aqualin dayCycleSpray ' + newValue)
				newCompleteValue = hex(oldValue[2])[2:].zfill(2)+hex(int(value[0:]))[2:].zfill(2)+hex(oldValue[4])[2:].zfill(2)
				#newCompleteValue = oldValue[2:4]+oldValue[4:6]+oldValue[6:]
				
				logging.debug('!!!-> action new complete value aqualin dayCycleSpray ' + newCompleteValue)
				#handle = self.characteristic[action]['handle']
				#value = message['command']['value']
				#message = '5301'+value
				#message += value
				message += newCompleteValue
				logging.debug('!!!-> action value aqualin dayCycleSpray ' + message)
				
			elif action == 'weekCycleSpray':
				#logging.debug('!!!-> start action aqualin weekCycleSpray ')
				oldValue = conn.readCharacteristic(self.characteristicHandles['cycleSpray'])
				logging.debug('!!!-> action old complete value aqualin weekCycleSpray ' + oldValue.decode())
				logging.debug('!!!-> action old complete value aqualin weekCycleSpray ' + str(oldValue))
				newValue = value
				logging.debug('!!!-> action new value aqualin weekCycleSpray ' + newValue)
				logging.debug('!!!-> action new value in byte aqualin weekCycleSpray ' + newValue[2:])
				newCompleteValue = hex(oldValue[2])[2:].zfill(2)+hex(oldValue[3])[2:].zfill(2)+'7f'
				
				logging.debug('!!!-> action new complete value aqualin weekCycleSpray ' + newCompleteValue)
				message += newCompleteValue
				logging.debug('!!!-> action value aqualin weekCycleSpray ' + message)
				
			elif action == 'weekdaysCycleSpray':
				logging.debug('!!!-> start action aqualin weekdaysCycleSpray value = '+value)
				oldValue = conn.readCharacteristic(self.characteristicHandles['cycleSpray'])
				logging.debug('!!!-> action old complete value aqualin weekdaysCycleSpray ' + oldValue.decode())
				logging.debug('!!!-> action old complete value aqualin weekdaysCycleSpray ' + str(oldValue))
				newValue = self.__convertWeekdays(value)
				logging.debug('!!!-> action new value aqualin weekdaysCycleSpray ' + newValue)
				newCompleteValue = hex(oldValue[2])[2:].zfill(2)+hex(oldValue[3])[2:].zfill(2)+newValue
				logging.debug('!!!-> action new complete value aqualin weekdaysCycleSpray ' + newCompleteValue)
				message += newCompleteValue
				logging.debug('!!!-> action value aqualin weekdaysCycleSpray ' + message)
			
			elif action == 'start1Spray':
				#handle = self.characteristic[action]['handle']
				logging.debug('===-> handle aqualin start1Spray ' + handle)
				#handle = self.characteristicHandles[action]
				#logging.debug('===-> handle aqualin start1Spray ' + handle)
				#value = message['command']['value']
				if value == 'ffff' or value == '65635':
					hexValue = 'ffff'
				else :
					value = value.zfill(4)
					logging.debug('===-> action value aqualin start1Spray ' + value)
					hexValue = str(hex(int(value[0:2]))[2:].zfill(2)) + str(hex(int(value[2:]))[2:].zfill(2))
					hexValue = hexValue.zfill(4)
				logging.debug('===-> action hexvalue aqualin start1Spray ' + hexValue)
				#message = '6402'+hexValue
				message += hexValue
				logging.debug('===-> action message aqualin start1Spray ' + message)
				
			elif action == 'start2Spray':
				if value == 'ffff' or value == '65635':
					hexValue = 'ffff'
				else :
					value = value.zfill(4)
					logging.debug('===-> action value aqualin start2Spray ' + value)
					hexValue = str(hex(int(value[0:2]))[2:].zfill(2)) + str(hex(int(value[2:]))[2:].zfill(2))
					hexValue = hexValue.zfill(4)
				logging.debug('===-> action hexvalue aqualin start2Spray ' + hexValue)
				#message = '6502'+hexValue
				message += hexValue
			
			elif action == 'autoOnSpray':
				logging.debug('===-> handle aqualin autoOnSpray ' + handle)
				logging.debug('===-> action message aqualin autoOnSpray ' + message)
				
			elif action == 'autoOffSpray':
				logging.debug('===-> handle aqualin autoOffSpray ' + handle)
				logging.debug('===-> action message aqualin autoOnSpray ' + message)
			
			elif action == 'autoOnMist':
				logging.debug('===-> handle aqualin autoOnMist ' + handle)
				logging.debug('===-> action message aqualin autoOnMist ' + message)
				
			elif action == 'autoOffMist':
				logging.debug('===-> handle aqualin autoOffMist ' + handle)
				logging.debug('===-> action message aqualin autoOnMist ' + message)
				
			elif action == 'weekdaysCycleMist':
				#logging.debug('!!!-> start action aqualin weekdaysweekdaysCycleMist ')
				oldValue = conn.readCharacteristic(self.characteristicHandles['weekdaysCycleMist'])
				logging.debug('!!!-> action old complete value aqualin weekdaysCycleMist ' + oldValue.decode())
				logging.debug('!!!-> action old complete value aqualin weekdaysCycleMist ' + str(oldValue))
				newValue = self.__convertWeekdays(value)
				logging.debug('!!!-> action new value aqualin weekdaysCycleMist ' + newValue)
				message += newValue
				logging.debug('!!!-> action value aqualin weekdaysCycleMist ' + message)
				
			elif action == 'durationMist':
				logging.debug('===-> handle aqualin durationMist ' + handle)
				value = value.zfill(6)
				logging.debug('===-> action value aqualin durationMist ' + value)
				hexValue = str(hex(int(value[0:2]))[2:].zfill(2)) + str(hex(int(value[2:4]))[2:].zfill(2)) + str(hex(int(value[4:]))[2:].zfill(2))
				hexValue = hexValue.zfill(6)
				logging.debug('===-> action hexvalue aqualin durationMist ' + hexValue)
				message += hexValue
				logging.debug('===-> action message aqualin durationMist ' + message)
			
			elif action == 'intervalMist':
				logging.debug('===-> handle aqualin intervalMist ' + handle)
				value = value.zfill(6)
				logging.debug('===-> action value aqualin intervalMist ' + value)
				hexValue = str(hex(int(value[0:2]))[2:].zfill(2)) + str(hex(int(value[2:4]))[2:].zfill(2)) + str(hex(int(value[4:]))[2:].zfill(2))
				hexValue = hexValue.zfill(6)
				logging.debug('===-> action hexvalue aqualin intervalMist ' + hexValue)
				message += hexValue
				logging.debug('===-> action message aqualin intervalMist ' + message)
			
			elif action == 'start1Mist':
				if value == 'ffff' or value == '65635':
					hexValue = 'ffff'
				else :
					value = value.zfill(4)
					logging.debug('===-> action value aqualin start1Mist ' + value)
					hexValue = str(hex(int(value[0:2]))[2:].zfill(2)) + str(hex(int(value[2:]))[2:].zfill(2))
					hexValue = hexValue.zfill(4)
				message += hexValue
				logging.debug('===-> action hexvalue aqualin start1Mist ' + message)
				
			elif action == 'end1Mist':
				if value == 'ffff' or value == '65635':
					hexValue = 'ffff'
				else :
					value = value.zfill(4)
					logging.debug('===-> action value aqualin end1Mist ' + value)
					hexVlue = str(hex(int(value[0:2]))[2:].zfill(2)) + str(hex(int(value[2:]))[2:].zfill(2))
					hexValue = hexValue.zfill(4)
				logging.debug('===-> action hexvalue aqualin end1Mist ' + hexValue)
				message += hexValue
				logging.debug('===-> action hexvalue aqualin end1Mist ' + message)
				
			elif action == 'start2Mist':
				if value == 'ffff' or value == '65635':
					hexValue = 'ffff'
				else :
					value = value.zfill(4)
					logging.debug('===-> action value aqualin start2Mist ' + value)
					hexValue = str(hex(int(value[0:2]))[2:].zfill(2)) + str(hex(int(value[2:]))[2:].zfill(2))
					hexValue = hexValue.zfill(4)
				logging.debug('===-> action hexvalue aqualin start2Mist ' + hexValue)
				message += hexValue
				logging.debug('===-> action hexvalue aqualin start2Mist ' + message)
				
			elif action == 'end2Mist':
				if value == 'ffff' or value == '65635':
					hexValue = 'ffff'
				else :
					value = value.zfill(4)
					logging.debug('===-> action value aqualin end2Mist ' + value)
					hexValue = str(hex(int(value[0:2]))[2:].zfill(2)) + str(hex(int(value[2:]))[2:].zfill(2))
					hexValue = hexValue.zfill(4)
				logging.debug('===-> action hexvalue aqualin end2Mist ' + hexValue)
				message += hexValue
				logging.debug('===-> action hexvalue aqualin end2Mist ' + message)
				
			else:
				logging.debug('-> action aqualin not yet implemented or ungnown ='+action)
				return 404
			
			logging.debug('-> action aqualin before write ='+action)
			conn.writeCharacteristic(handle,message)
			
			
		except Exception as e:
			logging.error('ACTION exception aqualin general '+ str(e))
		
		self.__disconnect(conn)
		logging.debug('ACTION aqualin end - disconnect done')
		return True
			  
	def findCharacteristics(self, mac, conn=''):
		logging.debug("*** --- **** aqualin Searching characteristics mac ="+mac)
		try:
			conn = self.__connect(mac, 'findChar')
			if not conn:
				return result
		except Exception as e:
			logging.debug('$$$ find aqualin:'+str(e))
		
		logging.debug("***  aqualin conn is ok, continue..")
		characteristics=[]
		
		try:
			logging.debug("***  aqualin before getCharacteristics..")
			characteristics = conn.getCharacteristics()
			logging.debug("***  aqualin after getCharacteristics..")
		except Exception as e:
			logging.debug('$$$1 find aqualin:'+str(e))
			try:
				characteristics = conn.getCharacteristics()
			except Exception as e:
				logging.debug('$$$2 find retry aqualin:'+str(e))
				try:
					characteristics = conn.getCharacteristics()
				except Exception as e:
					logging.debug('$$$3 find aqualin:'+str(e))
					self.__disconnect(conn)
		
		logging.debug("***  aqualin before next iter getCharacteristics..")
		try:
			if (characteristics):
				logging.debug("***  aqualin before next iter getCharacteristics done  count ="+str(len(characteristics)))
				for p in characteristics:
					logging.debug('***  aqualin élément ='+str(p)+' - '+hex(p.getHandle())+' - '+p.uuid.getCommonName())
					status_characteristic = p
				logging.debug("***  aqualin before filter getCharacteristics ")	
				new = filter(lambda el: el.uuid == STATUS_CHARACTERISTIC_UUID, characteristics)
				logging.debug("***  aqualin before iter getCharacteristics ")
				new2 = iter(new)
				logging.debug("***  aqualin before next getCharacteristics ")
				status_characteristic = next(new2)
				#status_characteristic = next(iter(new))
				logging.debug("***  aqualin after next iter getCharacteristics done STATUS_CHARACTERISTIC_UUID= "+STATUS_CHARACTERISTIC_UUID.getCommonName())
				logging.debug("***  aqualin after next iter getCharacteristics done !")
				logging.debug('***  aqualin Found ' + hex(status_characteristic.getHandle()))
				self.__disconnect(conn)
				return [hex(status_characteristic.getHandle())]
			else:
				logging.warning('***==== aqualin Error in getting characteristics return empty ! find retry aqualin:')
		except Exception as e:
			logging.error('==== aqualin exception return empty ! find retry aqualin:'+str(e))
			return []
		self.__disconnect(conn)

	def read(self, mac):
		logging.debug('READ aqualin:'+mac)
		result={}
		try:
			conn = self.__connect(mac, 'READ')
			if not conn:
				return result
			#logging.debug('READ aqualin connection ok')
			#result = self.findCharacteristics(mac, conn)
			
			timestamp = conn.readCharacteristic(self.characteristicHandles['timestamp'])
			logging.debug('READ aqualin timestamp='+self.__convertJHHMMSS(timestamp))
			
			program = conn.readCharacteristic(self.characteristicHandles['program'])[2]
			logging.debug('READ aqualin program='+str(program))
			
			sprayMist = ['spray', 'mist']
			result['sprayMist'] = sprayMist[conn.readCharacteristic(self.characteristicHandles['sprayMist'])[2]]
			logging.debug('READ aqualin sprayMist='+result['sprayMist'])
			
			spray = conn.readCharacteristic(self.characteristicHandles['spray'])[2]
			logging.debug('READ aqualin spray='+str(spray))
			
			triggerSpray = conn.readCharacteristic(self.characteristicHandles['triggerSpray'])
			runSpray = triggerSpray[2]
			remainSprayTime = int.from_bytes(triggerSpray[3:], byteorder='big')
			logging.debug('READ aqualin triggerSpray='+str(triggerSpray[2:]))
			
			mist = conn.readCharacteristic(self.characteristicHandles['mist'])[2]
			logging.debug('READ aqualin mist='+str(mist))
			
			triggerMist = conn.readCharacteristic(self.characteristicHandles['triggerMist'])
			logging.debug('READ aqualin triggerMist='+str(triggerMist))
			runMist = conn.readCharacteristic(self.characteristicHandles['triggerMist'])[2]
			remainMistTime = int.from_bytes(conn.readCharacteristic(self.characteristicHandles['triggerMist'])[3:], byteorder='big')
			logging.debug('READ aqualin remainMistTime='+str(conn.readCharacteristic(self.characteristicHandles['triggerMist'])[2:]))
			
			result['duration'] = remainMistTime
			logging.debug('READ aqualin remaining duration =' + str(result['duration']))
			result['remainingDuration'] = remainMistTime
			
			result['program'] = self.__convertProgram(program,spray,triggerSpray,mist,triggerMist,result['sprayMist'])
			
			#############   spray
			result['activeSpray'] = self.__convertActivStatus(conn.readCharacteristic(self.characteristicHandles['spray'])[2])
			result['autoSpray'] = self.__convertAutoStatus(conn.readCharacteristic(self.characteristicHandles['spray'])[2])
			cycleSpray = ['Jour','Semaine']
			result['cycleSpray'] = cycleSpray[conn.readCharacteristic(self.characteristicHandles['cycleSpray'])[2]]
			logging.debug('READ aqualin cycleSpray =' + str(result['cycleSpray']))
			result['dayCycleSpray'] = conn.readCharacteristic(self.characteristicHandles['cycleSpray'])[3]
			logging.debug('READ aqualin dayCycleSpray =' + str(result['dayCycleSpray']))
			result['weekCycleSpray'] = self.__convertDSVJMML(conn.readCharacteristic(self.characteristicHandles['cycleSpray'])[-1])
			logging.debug('READ aqualin weekCycleSpray =' + str(result['weekCycleSpray']))
			result['weekdaysCycleSpray'] = result['weekCycleSpray']
			logging.debug('READ aqualin weekdaysCycleSpray =' + str(result['weekdaysCycleSpray']))
			result['durationSpray'] = int.from_bytes(conn.readCharacteristic(self.characteristicHandles['durationSpray'])[2:], byteorder='big')
			logging.debug('READ aqualin durationSpray =' + str(result['durationSpray']))
			result['start1Spray'] = self.__convertHHMMint(conn.readCharacteristic(self.characteristicHandles['start1Spray'])[2:])
			logging.debug('READ aqualin start1Spray =' + str(result['start1Spray']))
			result['start2Spray'] = self.__convertHHMMint(conn.readCharacteristic(self.characteristicHandles['start2Spray'])[2:])
			logging.debug('READ aqualin start2Spray =' + str(result['start2Spray']))
			result['rainDelaySpray'] = conn.readCharacteristic(self.characteristicHandles['rainDelaySpray'])[-1]
			logging.debug('READ aqualin rainDelaySpray =' + str(result['rainDelaySpray']))
			
			#logging.debug('READ aqualin spray ended')
			
			########    mist
			result['activeMist'] = self.__convertActivStatus(conn.readCharacteristic(self.characteristicHandles['mist'])[2])
			#logging.debug('READ aqualin end mist1')
			result['autoMist'] = self.__convertAutoStatus(conn.readCharacteristic(self.characteristicHandles['mist'])[2])
			#logging.debug('READ aqualin end mist2')
			result['weekdaysCycleMist'] = self.__convertDSVJMML(conn.readCharacteristic(self.characteristicHandles['weekdaysCycleMist'])[-1])
			logging.debug('READ aqualin weekdaysCycleMist =' + result['weekdaysCycleMist'])
			result['intervalMist'] = self.__convertHHMMSSint(conn.readCharacteristic(self.characteristicHandles['intervalMist'])[2:])
			logging.debug('READ aqualin intervalMist =' + str(result['intervalMist']))
			result['start1Mist'] = self.__convertHHMMint(conn.readCharacteristic(self.characteristicHandles['start1Mist'])[2:])
			logging.debug('READ aqualin start1Mist =' + str(result['start1Mist']))
			result['end1Mist'] = self.__convertHHMMint(conn.readCharacteristic(self.characteristicHandles['end1Mist'])[2:])
			logging.debug('READ aqualin end1Mist =' + str(result['end1Mist']))
			result['start2Mist'] = self.__convertHHMMint(conn.readCharacteristic(self.characteristicHandles['start2Mist'])[2:])
			logging.debug('READ aqualin start2Mist =' + str(result['start2Mist']))
			result['end2Mist'] = self.__convertHHMMint(conn.readCharacteristic(self.characteristicHandles['end2Mist'])[2:])
			logging.debug('READ aqualin end2Mist =' + str(result['end2Mist']))
			result['durationMist'] = self.__convertHHMMSSint(conn.readCharacteristic(self.characteristicHandles['durationMist'])[2:])
			logging.debug('READ aqualin durationMist =' + str(result['durationMist']))
			
			
			result['battery'] = conn.readCharacteristic(self.characteristicHandles['battery'])[0]
			result['id'] = mac
			result['source'] = globals.daemonname
			
		except Exception as e:
			logging.error('READ exception aqualin general '+ str(e))
			var = traceback.format_exc()
			logging.debug('READ exception aqualin details : '+ var)
		globals.JEEDOM_COM.add_changes('devices::'+conn.mac,result)
		self.__disconnect(conn)
		logging.debug('READ aqualin end - disconnect done')
		return result
	
	def handlenotification(self, conn, handle, data={}, action={}):
		logging.debug('NOTIFy aqualin ')
		self.__disconnect(conn)
	
		result={}
		result['id'] = conn.mac
		logging.debug('aqualin id : '+result['id'])
		size = len(data)
		logging.debug('aqualin data : '+str(size))
		result['source'] = globals.daemonname
		logging.debug('aqualin source : '+result['source'])
		if (size <= 6):
			result['mode'] = 'False'
			logging.debug('aqualin mode : '+result['mode'])
			result['battery'] = '0'
			logging.debug('aqualin battery : '+result['battery'])
		else:
			result['temps'] = str(int(data[6].encode('hex'),16))
			logging.debug('aqualin temps : '+result['temps'])
			tension = int(data[7].encode('hex'),16)
			logging.debug('aqualin tension : '+str(tension))
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
			logging.debug('aqualin battery : '+result['battery'])	
			result['rssi'] = str(int(data[8].encode('hex'),16))
			result['mode'] = str((int(data[4].encode('hex'),16) > 0))
			logging.debug('aqualin mode : '+result['mode'])
			if result['mode'] == 'False':
				result['temps'] = '0'
				logging.debug('aqualin temps : '+result['temps'])
		globals.LAST_STORAGE[conn.mac] = result['mode']
		globals.JEEDOM_COM.add_changes('devices::'+conn.mac,result)
	
	def __connect(self, mac, command='undefined'):
		conn = Connector(mac)
		if not conn.isconnected:
			conn.connect(type='public')
			if not conn.isconnected:
				logging.debug('** '+command+' aqualin connection failed, retry 1...')
				conn.connect(type='public')
				if not conn.isconnected:
					logging.debug('** '+command+' aqualin connection failed, retry 2...')
					conn.connect(type='public')
					if not conn.isconnected:
						conn = False
		if conn:
			logging.debug('** '+command+' aqualin connection done for :'+mac)
			self.countConn += 1
		else:
			logging.warning('** '+command+' aqualin connection failed for :'+mac)
		
		return conn
		
	def __disconnect(self, conn):
		if self.countConn != 1:
			logging.debug('***** bug aqualin count conn = '+str(countConn))
		conn.disconnect(force=True)
		self.countConn = 0
		logging.debug('**  aqualin disconnected')
		return 	
		
	def __convertHHMM(self, data):
		try:
			#logging.debug('aqualin debug convertHHMM : '+ str(data))
			if data == b'\xff\xff':
				return '-+-'
			else:
				return str(data[0]).zfill(2) + ':' + str(data[1]).zfill(2)
		except Exception as  e:
			logging.debug('aqualin debug exception convertHHMM : '+ str(e))
			
	def __convertHHMMint(self, data):
		try:
			#logging.debug('aqualin debug convertHHMM : '+ str(data))
			if data == b'\xff\xff':
				return 9999
			else:
				return data[0]*100+data[1]
		except Exception as  e:
			logging.debug('aqualin debug exception convertHHMMint : '+ str(e))
			
	def __convertHHMMSS(self,data):
		return str(data[0]).zfill(2) + ':' + str(data[1]).zfill(2) + ':' + str(data[2]).zfill(2)
	
	def __convertHHMMSSint(self,data):
		return data[0]*10000 + data[1]*100 + data[2]
    
	def __convertJHHMMSS(self,data):
		return str(data[-1]).zfill(2) + '-'+ str(data[2]).zfill(2) + ':'+ str(data[3]).zfill(2) + ':'+ str(data[4]).zfill(2)
	
	def __convertDSVJMML(self,data):
		#logging.debug('aqualin debug1 : '+ str(data))
		bin_str= str(bin(data))[2:].zfill(7)
		#logging.debug('aqualin debug2 : '+bin_str)
		Tab = [int(bin_str[-(1+i)]) for i in range(7)]
		Letter = ['l','m','m','j','v','s','d']
		#logging.debug('aqualin debug3 : ')
		weekdays = [Letter[i].upper()  if Tab[i] else Letter[i] for i in range(7)]
		#logging.debug('aqualin debug4 : '+ "".join(weekdays))
		return "".join(weekdays)
	
	def __convertWeekdays(self,data):
		#data = "lMmjvsd"
		#print (data)
		lundi = 1
		mardi = 2
		mercredi = 4
		jeudi = 8
		vendredi = 16
		samedi = 32
		dimanche = 64
		
		lu,ma,me,je,ve,sa,di = data
		#print (lu,ma)
		out = 0
		if lu == 'L':
		  out =  out | lundi
		if ma == 'M':
		  out = out | mardi
		if me == 'M':
		  out = out | mercredi
		if je == 'J':
		  out = out | jeudi
		if ve == 'V':
		  out = out | vendredi
		if sa == 'S':
		  out = out | samedi
		if di == 'D':
		  out = out | dimanche
		#out = lundi | mardi | mercredi | jeudi | vendredi | samedi | dimanche
		
		#print (out)
		#print (hex(out))
		#print (hex(out)[2:])
		return hex(out)[2:].zfill(2)
		

	def __convertProgram(self,program,spray,triggerSpray,mist,triggerMist,sprayMist):
		'''
		program
			00 = aucun programme
			01 = programme arrosage
			02 = programme brumisateur
			04 = n'existe pas actif auto
			09 = n'existe pas actif manuel
		'''
		value = program & 15
		if value != program :
			logging.warning('aqualin debug  programme value unknown : '+ str(program))
			
		if value not in [0,1,2]:
			logging.warning('aqualin debug  programme value unknown : '+ str(value))
			value = 255
		choices = {
			0: "aucun",
			1: "arrosage",
			2: "brumisateur",
			255: "anomalie"
		}
		return choices.get(value)
		
	def __convertAutoStatus(self,data):
		'''
			00 = inactif off
			01 = inactif auto
			02 = actif spray
			04 = actif spray
			09 = actif manuel
		'''
		value = data & 15
		if value != data :
			logging.warning('aqualin debug auto mode  value unknown : '+ str(data))
		if value not in [0,1,2,4,9]:
			logging.debug('aqualin debug  auto mode  data value unknown : '+ str(data))
		choices = {
			0: 0,
			1: 0,
			2: 1,
			4: 1,
			9: 0
		}
		return choices.get(value)	
		
	def __convertActivStatus(self,data):
		'''
			00 = inactif off => désactivé
			01 = inactif/suspendu auto
			02 = actif spray
			04 = actif auto
			09 = actif manuel
		'''
		value = data & 15
		if value != data :
			logging.warning('aqualin debug active mode  value unknown : '+ str(data))
		if value not in [0,1,2,4,9]:
			logging.debug('aqualin debug  active mode  data value unknown : '+ str(value))
		choices = {
			0: "désactivé off",
			1: "désactivé",
			2: "activé",
			4: "actif",
			9: "actif manuellement"
		}
		return choices.get(value)
	
	

	def __convertBatteryData(self,data):
		logging.debug('READ aqualin battery='+ str(data));
		return data.hex()

			  
globals.COMPATIBILITY.append(Aqualin)
