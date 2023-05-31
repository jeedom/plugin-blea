# coding: utf-8
import logging
import time

import globals
import utils
from bluepy.btle import BTLEDisconnectError, BTLEInternalError
from notification import Notification

# Doc: https://github.com/madhead/saberlight/blob/master/protocols/Triones/protocol.md

RGB_CHARACTERISTIC_UUID = '0000ffd9-0000-1000-8000-00805f9b34fb'
NOTIF_TIMEOUT = 5

class Triones():
	def __init__(self):
		self.name = 'triones'
		self.ignoreRepeat = True

	def _write_data(self, conn, data):
		characteristic = conn.conn.getCharacteristics(uuid=RGB_CHARACTERISTIC_UUID)[0]
		conn.writeCharacteristic(str(characteristic.getHandle()), data)

	def isvalid(self,name,manuf='',data='',mac=''):
		if name.lower().startswith('triones:') or name == self.name:
			return True

	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		return action
	
	def action(self,message, retry=False):
		try:
			type =''
			mac = message['device']['id']
			value = message['command']['value']
			if 'type' in message['command']:
				type = message['command']['type']
			logging.debug('Action received for Triones: ' + type)

			conn,_ = utils.getConnection(mac)
			if not conn:
				return

			if type == 'switch':
				logging.debug('Switch the Triones {}'.format('ON' if value == '1' else 'OFF'))
				self._write_data(conn, 'CC2333' if value == '1' else 'CC2433')

			if type == 'color':
				logging.debug(f'Set the Triones color to {value}')
				self._write_data(conn, f'56{value}00f0aa')

			if type == 'brightness':
				logging.debug(f'Set the Triones brightness to {value}')
				current_state = globals.LAST_STORAGE[mac] if globals.LAST_STORAGE else {}
				color = current_state["color"] if "color" in current_state else '#ffffff'
				colors = list(map(lambda c: int(c, 16), [color[1:3], color[3:5], color[5:7]]))
				current_brightness = max(colors) * 100 / 255
				colors = map(lambda c: format(round(c * int(value) / current_brightness), 'x').zfill(2), colors)
				color = ''.join(colors)
				logging.debug(f'Set the Triones color to: {color}')
				self._write_data(conn, f'56{color}00f0aa')    
        
			# Trigger the status notification
			self._write_data(conn, 'ef0177')
			notification = Notification(conn,Triones)
			notification.subscribe(NOTIF_TIMEOUT)

			conn.disconnect()
			return
		except (BTLEDisconnectError, BTLEInternalError):
			logging.debug(f'Device disconnected, remove the connection')
			conn.disconnect(True)
			if mac in globals.KEEPED_CONNECTION:
				del globals.KEEPED_CONNECTION[mac]
			if not retry:
				time.sleep(1)
				self.action(message, True)
	
	def read(self,mac,connection=''):
		logging.debug('Read data for Triones')
		result = {}
		try:
			conn = utils.getConnection(mac)
			if not conn:
				return
                  
			# Trigger the status notification
			self._write_data(conn, 'ef0177')
			notification = Notification(conn,Triones)
			notification.subscribe(NOTIF_TIMEOUT)

		except Exception as e:
			logging.debug(str(e))
			conn.disconnect()
			return
		logging.debug(str(result))
		conn.disconnect()
		result['id'] = mac
		return result

	def handlenotification(self,conn,handle,data,action={}):
		logging.debug("Receive notification for Triones, handle " + hex(handle))
		try:
			if hex(handle) == '0xc' and len(data) == 12:
				result = {
					"id": conn.mac,
					"on": '1' if utils.twoDigitHex(data[2]) == '23' else '0',
					"mode": utils.twoDigitHex(data[3]),
					"speed": utils.twoDigitHex(data[5]),
					"color": '#' + data[6:9].hex(),
					"brightness": round(max(data[6:9]) * 100 / 255)
				}
				
				logging.debug(str(result))
				globals.LAST_STORAGE[conn.mac] = result
				globals.JEEDOM_COM.add_changes('devices::'+conn.mac,result)

		except Exception as e:
			logging.debug("Error while receiving Triones notification : " + str(e))

globals.COMPATIBILITY.append(Triones)