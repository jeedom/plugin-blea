from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals
from multiconnect import Connector
import utils

class Dotti():
	def __init__(self):
		self.name = 'dotti'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data=''):
		if self.name in name.lower():
			return True

	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		return action
		
	def action(self,message):
		mac = message['device']['id']
		if mac not in globals.LAST_STORAGE:
			globals.LAST_STORAGE[mac]={}
		handle = message['command']['handle']
		value = message['command']['value']
		type = message['command']['type']
		if mac in globals.KEEPED_CONNECTION:
			logging.debug('DOTTI------Already a connection for ' + mac + ' use it')
			conn = globals.KEEPED_CONNECTION[mac]
		else:
			logging.debug('DOTTI------Creating a new connection for ' + mac)
			conn = Connector(mac)
			globals.KEEPED_CONNECTION[mac]=conn
			conn.connect()
		if not conn.isconnected:
			conn.connect()
			if not conn.isconnected:
				return
		try:
			if type == 'mode':
				logging.debug('DOTTI------Changing Mode')
				data = message['command']['value']
				conn.writeCharacteristic('0x2a',data)
				globals.LAST_STORAGE[mac]={}
			elif type == 'color':
				logging.debug('DOTTI------Sending Color')
				data = message['command']['data']
				conn.writeCharacteristic('0x2a','0601'+utils.twoDigitHex(int(data[0]))+utils.twoDigitHex(int(data[1]))+utils.twoDigitHex(int(data[2]))+'00')
				colorArray ={}
				for i in range(64): 
					colorArray[int(i) + 1] = self.rgb_to_hex((int(data[0]), int(data[1]), int(data[2])))
				globals.LAST_STORAGE[mac] = colorArray
				logging.debug('Color sent')
			elif type == 'display':
				logging.debug('DOTTI------Sending Display')
				data = message['command']['data']
				save_pixel=0
				total_pixel=0
				temp={}
				maxint=0
				maxhex='#FFFFFF'
				if len(data) == 64:
					for pixel, value in data.iteritems():
						shex = self.rgb_to_hex((int(value[0]), int(value[1]), int(value[2])));
						if shex not in temp:
							temp[shex] = 1
						else:
							temp[shex] = temp[shex] + 1
						if temp[shex] > maxint:
							maxint = temp[shex]
							maxhex = shex
					for pixel, value in data.iteritems():
						total_pixel = total_pixel + 1
						if mac in globals.LAST_STORAGE:
							if int(pixel) in globals.LAST_STORAGE[mac] and globals.LAST_STORAGE[mac][int(pixel)].lower() == self.rgb_to_hex((int(value[0]),int(value[1]), int(value[2]))).lower():
								save_pixel = save_pixel + 1
					if  (maxint+1) > save_pixel and maxint > 2:
						logging.debug('DOTTI------I use color all screen method to improve display speed in :'+str(maxhex))
						conn.writeCharacteristic(handle,'0601'+str(maxhex).replace('#','')+'00')
						colorArray ={}
						for i in range(64): 
							colorArray[int(i) + 1] = str(maxhex)
						globals.LAST_STORAGE[mac] = colorArray
				save_pixel=0
				total_pixel=0
				colorArray ={}
				for pixel, value in data.iteritems():
					total_pixel = total_pixel + 1
					if mac in globals.LAST_STORAGE:
						if isinstance(value,(list,)):
							logging.debug('DOTTI------this is a list')
							if int(pixel) in globals.LAST_STORAGE[mac] and globals.LAST_STORAGE[mac][int(pixel)].lower() == self.rgb_to_hex((int(value[0]), int(value[1]), int(value[2]))).lower():
								save_pixel = save_pixel + 1
								colorArray[int(pixel)]=self.rgb_to_hex((int(value[0]), int(value[1]), int(value[2]))).lower()
								continue
						else:
							logging.debug('DOTTI------this is a string')
							if int(pixel) in globals.LAST_STORAGE[mac] and globals.LAST_STORAGE[mac][int(pixel)].lower() == value.lower():
								save_pixel = save_pixel + 1
								colorArray[int(pixel)]=value.lower()
								continue
					if isinstance(value,(list,)):
						logging.debug('DOTTI------writing from rgb ' + self.rgb_to_hex((int(value[0]), int(value[1]), int(value[2]))))
						conn.writeCharacteristic('0x2a','0702'+utils.twoDigitHex(int(pixel))+utils.twoDigitHex(int(value[0]))+utils.twoDigitHex(int(value[1]))+utils.twoDigitHex(int(value[2])))
						colorArray[int(pixel)] = self.rgb_to_hex((int(value[0]), int(value[1]), int(value[2])))
					else:
						logging.debug('DOTTI------writing from hex ' + str(value)[1:])
						conn.writeCharacteristic('0x2a','0702'+utils.twoDigitHex(int(pixel))+str(value)[1:])
						colorArray[int(pixel)] = value.lower()
					time.sleep(0.05)
				globals.LAST_STORAGE[mac] = colorArray
				logging.debug('DOTTI------I save '+str(save_pixel)+'/'+str(total_pixel)+' pixel to write so '+str((save_pixel*100)/total_pixel)+'%')
				logging.debug('DOTTI------Display sent')
		except Exception,e:
			logging.debug("DOTTI------Failed to finish : %s" % str(e))
		conn.disconnect()
		return
		
	def hex_to_rgb(self,value):
		value = value.lstrip('#')
		lv = len(value)
		return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

	def rgb_to_hex(self,rgb):
		return '#%02x%02x%02x' % rgb


globals.COMPATIBILITY.append(Dotti)