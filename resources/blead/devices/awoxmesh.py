from bluepy import btle
import time
import logging
import globals
import binascii
from multiconnect import Connector
from notification import Notification
import struct
try:
	from Crypto.Cipher import AES
except:
	logging.debug('No crypto ignoring it')
from os import urandom
import os.path
import copy

# partially based on : https://github.com/Leiaz/python-awox-mesh-light

# Commands :

#: Set mesh groups.
#: First byte : 1 to add group, 0 to remove group
#: Second an third bytes : 2 bytes in little endian order. Group ids are in the form 0x80xx.
#: Data : 3 bytes
C_MESH_GROUP = 0xd7

#: Set the mesh id. The light will still answer to the 0 mesh id. Calling the
#: command again replaces the previous mesh id.
#: Data : the new mesh id, 2 bytes in little endian order
C_MESH_ADDRESS = 0xe0

#:
C_MESH_RESET = 0xe3

#: On/Off command. Data : one byte 0, 1
C_POWER = 0xd0

#: Data : one byte
C_LIGHT_MODE = 0x33

#: Data : one byte 0 to 6
C_PRESET = 0xc8

#: White temperature. one byte 0 to 0x7f
C_WHITE_TEMPERATURE = 0xf0

#: one byte 1 to 0x7f
C_WHITE_BRIGHTNESS = 0xf1

#: 4 bytes : 0x4 red green blue
C_COLOR = 0xe2

#: one byte : 0xa to 0x64 ....
C_COLOR_BRIGHTNESS = 0xf2

#: Data 4 bytes : How long a color is displayed in a sequence in milliseconds as
#:   an integer in little endian order
C_SEQUENCE_COLOR_DURATION = 0xf5

#: Data 4 bytes : Duration of the fading between colors in a sequence, in
#:   milliseconds, as an integer in little endian order
C_SEQUENCE_FADE_DURATION = 0xf6

#: 7 bytes
C_TIME = 0xe4

#: 10 bytes
C_ALARMS = 0xe5


PAIR_CHAR_UUID = '001b'
COMMAND_CHAR_UUID = '0015'
STATUS_CHAR_UUID = '0012'
OTA_CHAR_UUID = '0018'
MODEL_UUID = '0003'

# default data when not paired
P_DEFAULTNAME = 'unpaired'
P_DEFAULTPASSWORD = '1234'
P_DEFAULTGROUP = 1	# 1 to 255

P_JEEDOM_MESHNAME = "JEEDOMMESH"
P_JEEDOM_MESHPASSWORD = "4AhAVLPwGp2Mu9VT"
P_JEEDOM_LONGTERMKEY = "4556572782865925"

NOTIF_TIMEOUT = 4

class Awoxmesh():
	def __init__(self):
		self.name = 'awoxmesh'
		self.ignoreRepeat = False
		self.auto_pairing = False
		self.mesh_id = 0
		self.session_key = None
		self.mesh_name = P_JEEDOM_MESHNAME
		self.mesh_password = P_JEEDOM_MESHPASSWORD
		self.mesh_longtermkey = P_JEEDOM_LONGTERMKEY


	def isvalid(self,name,manuf='',data='',mac=''):
		if name.lower() == P_DEFAULTNAME:
			logging.info('Detected unpaired device')

		if manuf.lower().startswith("6001") or name.lower() == self.name:
			return True

		return False

	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1

		action['version'] = 'awox'
		if mac.upper() not in globals.KNOWN_DEVICES and globals.LEARN_MODE:
			if name.lower() == P_DEFAULTNAME and self.auto_pairing:
				self.setMeshPairing (mac, name, self.mesh_name, self.mesh_password, self.mesh_longtermkey)

			if mac in globals.KEEPED_CONNECTION:
				conn = globals.KEEPED_CONNECTION[mac]
			else:
				conn = Connector(mac)
			conn.connect()
			char = conn.readCharacteristic(MODEL_UUID)
			conn.disconnect()
			logging.debug('Version is ' + char)
			if char.lower().startswith('EF'):
				action['version'] = 'awox'
			if char.lower().startswith('ERCUm'):
				action['version'] = 'awoxremote'
			if char.lower().startswith('ESMLm'):  # ESMLm_c9 and ESMLm_c13
				action['version'] = 'awox'

		return action


	def auth(self,conn):
		logging.debug('Authenticating...')

		try:
			self.session_random = urandom(8)
			message = make_pair_packet (self.mesh_name, self.mesh_password, self.session_random)

			# send pairing message
			conn.writeCharacteristic(PAIR_CHAR_UUID,message)
			# set status char to 1 (for notification?)
			conn.writeCharacteristic(STATUS_CHAR_UUID,'01')

			# get Pairing reply
			reply = bytearray (conn.readCharacteristic(PAIR_CHAR_UUID))
			if reply[0] == 0xd :
				logging.debug("Connected (Auth OK).")
				self.session_key = make_session_key (self.mesh_name, self.mesh_password, self.session_random, reply[1:9])
			else :
				if reply[0] == 0xe :
					logging.debug("Auth error : check name and password.")
				else :
					#logging.debug("Unexpected pair value : %s", repr (reply))
					logging.debug('Error while trying to auth..')
				return False

		except Exception as e:
			logging.debug("Exception found while authenticating : " + str(e))
			return False

		return True


	def sendAction(self,conn,subhandle,data,sendNotif=True):
		try:
			packet = make_command_packet (self.session_key, conn.mac, self.mesh_id, subhandle, data)
			globals.PENDING_ACTION = True
			if sendNotif == True:
				notification = Notification(conn, Awoxmesh, {'mac': conn.mac, 'session':self.session_key})
				notification.subscribe(timer=NOTIF_TIMEOUT,disconnect=False)

			logging.debug("Sending packet for "+ conn.mac + " : " + packet + " with session key : "+ "".join("%02x" % b for b in self.session_key))
			return conn.writeCharacteristic(COMMAND_CHAR_UUID, packet)
		except Exception as e:
			logging.debug("Exception found while sending action")
			logging.debug(str(e))
			return False


	def action(self,message):
		#logging.debug('Doing Awox action')
		result = {}
		ret = True

		mac = message['device']['id']
		result['id'] = mac
		globals.PENDING_ACTION = True

		localname=''
		if 'localname' in message['device']:
			localname = message['device']['localname']
			# Make it works directly with devices paired by remote control (for testing)
			if localname.startswith("R-"):
				self.mesh_name = localname
				self.mesh_password = P_DEFAULTPASSWORD

		handle = ''
		value = '0'
		cmd = ''
		if 'handle' in message['command']:
			handle = message['command']['handle']
		if 'value' in message['command']:
			value = message['command']['value']
			if '$' in value:   # manage injection of cmd/group in value (ex : gp$value or cmd$gp$value)
				s = value.split('$')
				if len(s)==2:	# only group
					message['command']['gp'] = s[0]
					value = s[1]
				elif len(s)==3:	# command and group
					message['command']['cmd'] = s[0]
					message['command']['gp'] = s[1]
					value = s[2]
				else:
					logging.info('Incorrect parameter (' + message['command']['value'] + '). Format: [[cmd$]gp$]value')
		if 'cmd' in message['command']:
			cmd = message['command']['cmd']
		if 'gp' in message['command']:
			self.mesh_id = int(message['command']['gp'])+32768
		if 'target' in message['command']:
			self.mesh_id = int(message['command']['target'])

		if cmd!='':
			logging.debug('Running action ' + cmd)

		# case of new pairing will work only if unpaired
		if cmd == 'setNewPairing' or cmd == 'firstInit':
			self.mesh_name = P_JEEDOM_MESHNAME
			self.mesh_password = P_JEEDOM_MESHPASSWORD
			ret = self.setMeshPairing (mac, localname, self.mesh_name, self.mesh_password, self.mesh_longtermkey)
			time.sleep(3)
			message['command']['cmd'] = "status"
			self.action(message)
			return

		if mac in globals.KEEPED_CONNECTION:
			logging.debug('Already a connection for ' + mac + ' use it')
			conn = globals.KEEPED_CONNECTION[mac]
		else:
			logging.debug('Creating a new connection for ' + mac)
			conn = Connector(mac)
			globals.KEEPED_CONNECTION[mac]=conn

		i=1
		authresult = False
		while i <= 3:
			i = i + 1
			if not conn.isconnected:
				try:
					conn.connect(retry=1)
				except:
					pass
			if conn.isconnected:
				authresult = self.auth(conn)
			if authresult:
				break
			else:
				time.sleep(0.5)

		if not authresult:
			logging.debug('Ending action due to authentication error on device')
			globals.PENDING_ACTION = False
			return

		if cmd == 'power':
			data = struct.pack('B', int(value))
			self.sendAction(conn,C_POWER,data)
		elif cmd == 'resetMesh':
			self.resetMesh(conn)
		elif cmd == 'setMeshId':
			self.setMeshId(conn, int(value))
		elif cmd == 'addMeshGroup':
			self.setGroupId(conn, int(value),delete=False)
		elif cmd == 'delMeshGroup':
			self.setGroupId(conn, int(value),delete=True)
		elif cmd == 'setWhiteHex':
			# temperature + brightness (hex)
			data = bytearray.fromhex(value[:2])
			self.sendAction(conn,C_WHITE_TEMPERATURE,data, False)
			data = bytearray.fromhex(value[-2:])
			self.sendAction(conn,C_WHITE_BRIGHTNESS,data)
		elif cmd == 'setWhite':
			# temperature-brightness (value 0 to 100)
			data = value.split('-')
			result['whitetemperature'] = data[0]
			result['whitebrightness'] = data[1]
			temp = struct.pack('B', int(int(data[0])*127/100))
			brightness = struct.pack('B', int(int(data[1])*127/100))
			self.sendAction(conn,C_WHITE_TEMPERATURE, temp, False)
			self.sendAction(conn,C_WHITE_BRIGHTNESS, brightness)
		elif cmd == 'setWhiteTemperature':
			# temperature from 1 to 100)
			result['whitetemperature'] = value
			data = struct.pack('B', int(int(value)*127/100))
			self.sendAction(conn,C_WHITE_TEMPERATURE,data)
		elif cmd == 'setWhiteBrightness':
			# brightness (hex)
			#data = value.decode("hex")
			result['whitebrightness'] = value
			data = struct.pack('B', int(int(value)*127/100))
			self.sendAction(conn,C_WHITE_BRIGHTNESS,data)
		elif cmd == 'setColor':
			# red + green + blue (hex)
			result['color'] = value
			value = '04' + value.replace("#", "")
			data = bytearray.fromhex(value)
			self.sendAction(conn,C_COLOR,data)
		elif cmd == 'setColorLight':
			# color(#hex)-brightness(0-100)
			data = value.split('-')
			result['color'] = data[0]
			result['colorbrightness'] = data[1]
			color = '04' + data[0].replace("#", "")
			brightness = struct.pack('B', int(int(data[1])*64/100))
			self.sendAction(conn,C_COLOR, bytearray.fromhex(color), False)
			self.sendAction(conn,C_COLOR_BRIGHTNESS, brightness)
		elif cmd == 'setColorBrightness':
			# a value between 0xa and 0x64
			result['colorbrightness'] = value
			data = struct.pack('B', int(int(value)*64/100))
			self.sendAction(conn,C_COLOR_BRIGHTNESS,data)
		elif cmd == 'setSequence':
			# number between 0 and 6
			data = struct.pack('B', int(value))
			ret = self.sendAction(conn,C_PRESET,data)
		elif cmd == 'setSequenceColorDuration':
			# duration: in milliseconds.
			data = struct.pack ("<I", int(value))
			ret = self.sendAction(conn,C_SEQUENCE_COLOR_DURATION,data)
		elif cmd == 'setSequenceFadeDuration':
			# duration: in milliseconds.
			data = struct.pack ("<I", int(value))
			ret = self.sendAction(conn,C_SEQUENCE_FADE_DURATION,data)
		elif cmd == 'playScenario':
			# color/white/power&duration|color/white/power&duration|...|X (number of iteration for last value)
			# ex: #DF0101-100&5|100-100&7|50-50&10|0&5|1&0|3
			self.playScenario(conn, value)
		elif cmd == 'setLightMode':		# does nothing
			# duration: in milliseconds.
			data = struct.pack ("B", int(value))
			ret = self.sendAction(conn,C_LIGHT_MODE,data)
		elif cmd == 'status':
			notification = Notification(conn, Awoxmesh, {'mac': conn.mac, 'session':self.session_key})
			notification.subscribe(timer=NOTIF_TIMEOUT,disconnect=False)
			conn.readCharacteristic(STATUS_CHAR_UUID)
		else:
			data = bytearray.fromhex(value)
			handle = int(handle,16)
			self.sendAction(conn,handle,data)

		logging.info('Value ' + value + ' sent to controller')

		globals.PENDING_ACTION = False

		# prepare results
		if ret:
			if cmd == 'power':
				result['status'] = int(value)
			elif cmd == 'setWhite' or cmd == 'setWhiteHex' or cmd == 'setWhiteTemperature' or cmd == 'setWhiteBrightness':
				result['mode'] = 1
				result['modestring'] = "Blanc"
				result['status'] = 1
			elif cmd == 'setColor' or cmd == 'setColorLight' or cmd == 'setColorBrightness':
				result['mode'] = 3
				result['modestring'] = "Couleur"
				result['status'] = 1
			elif cmd == 'setSequence':
				result['mode'] = 7
				result['modestring'] = "Sequence"
				result['status'] = 1
			else:	# other command for which we are unsure of the result
				return
			logging.debug('Action returned status before notification')
		else:	# request somehow failed
			return

		return result

	def read(self,mac,connection=''):
		if 'localname' in globals.KNOWN_DEVICES[mac.upper()]:
			# Make it works directly with devices paired by remote control (for testing)
			if globals.KNOWN_DEVICES[mac.upper()]['localname'].startswith("R-"):
				self.mesh_name = globals.KNOWN_DEVICES[mac.upper()]['localname']
				self.mesh_password = P_DEFAULTPASSWORD

		if mac in globals.KEEPED_CONNECTION:
			logging.debug('Already a connection for ' + mac + ' use it')
			conn = globals.KEEPED_CONNECTION[mac]
		else:
			logging.debug('Creating a new connection for ' + mac)
			conn = Connector(mac)
			globals.KEEPED_CONNECTION[mac]=conn

		i=1
		authresult = False
		while i <= 2:
			i = i + 1
			if not conn.isconnected:
				try:
					conn.connect(retry=1)
				except:
					pass
			if conn.isconnected:
				authresult = self.auth(conn)
			if authresult:
				break
			else:
				time.sleep(1)

		if not authresult:
			logging.debug('Ending action due to authentication error on device')
			globals.PENDING_ACTION = False
			return result

		# send message
		notification = Notification(conn, Awoxmesh, {'mac': conn.mac, 'session':self.session_key})
		notification.subscribe(timer=NOTIF_TIMEOUT,disconnect=False)
		conn.readCharacteristic(STATUS_CHAR_UUID)

		return {}

	def handlenotification(self,conn,handle,data,action={}):
		result  = {}
		try:
			if hex(handle) == '0x12':
				message = decrypt_packet (action['session'], action['mac'], data)
				if not isinstance(message,str):
					return

				result = self.parseResult(message, action['mac'])
				if result['messagetype'] == 220:  # only status broadcast device notification
					for device in globals.KNOWN_DEVICES:
						if int(device[-2:], 16) == result['targetmeshid']:  # compare mesh id with last mac 2 last digit
							#logging.debug('Sending for destination ' + device)
							result['id'] = device
							globals.JEEDOM_COM.add_changes('devices::'+device,result)
							break
				logging.debug('Notif content : ' + result['debug'] + '   (raw: '+message+ ')')

			#self.unlock(action['mac'])
		except Exception as e:
			logging.debug("Exception found while receiving notification : " + str(e))


	def parseResult(self, message, mac):
		result  = {}
		result['id'] = mac
		result['source'] = globals.daemonname
		result['rawdebug'] = message
		result['debug'] = message[6:10] +'-'+ message[14:16] +'-'+ message[20:22] +'-'+ message[22:24] +'-'+ message[24:26] +'-'+ message[26:30] +'-'+ message[30:-2]
		meshid = int(mac[-2:], 16)  # last hex of mac address
		result['meshid'] = meshid

		filter = int(message[6:8], 16)
		filter2 = int(message[14:16], 16)   # status msg is 220 (DC in hexa), others are for some commands
		result['messagetype'] = int(message[14:16], 16)   # status msg is 220 (DC in hexa), others are for some commands

		msgmeshid = int(message[20:22], 16)
		is_remote = True if int(message[22:24], 16)==1 else False
		mode = int(message[24:26], 16)
		msgtype = int(message[14:16], 16)

		result['targetmeshid'] = msgmeshid
		if filter > 0 and filter2 != 220:
			result['targetmeshid'] = filter

		if not is_remote and filter2 == 220:
			result['status'] = mode%2

			modestring = ''
			if mode==1 or mode==5:
				modestring = 'Blanc'
				mode=1
			elif mode==3:
				modestring = 'Couleur'
			elif mode==7:
				modestring = 'Sequence'

			if mode%2 == 1:
				result['mode'] = mode
				result['modestring'] = modestring

			result['whitetemperature'] = int(int(message[28:30], 16)*100/127)  # convert to value from 0 to 100
			result['whitebrightness'] = int(int(message[26:28], 16)*100/127)  # convert to value from 0 to 100
			result['color'] = "#" + message[32:38]
			result['colorbrightness'] = int(int(message[30:32], 16)*100/64)  # convert to value from 0 to 100

		if is_remote:
			result['battery'] = int(int(message[26:28], 16)*100/255)  # convert to value from 0 to 100

		return result


	def setMeshPairing (self, mac, localname, new_mesh_name, new_mesh_password, new_mesh_long_term_key):
		if mac in globals.KEEPED_CONNECTION:
			conn = globals.KEEPED_CONNECTION[mac]
		else:
				conn = Connector(mac)
		conn.connect()

		defaultmeshname = localname.encode()
		is_a_remote = False
		char = conn.readCharacteristic(MODEL_UUID)
		if char.lower() == 'ERCUm':  #if this is a remote
			is_a_remote = True
			logging.info("[Unpaired device] Remote detected, trying with name "+defaultmeshname)

		if defaultmeshname == self.mesh_name:
			logging.info("Device already paired to Jeedom. Do a reset of the device beforehand")
		else:
			session_random = urandom(8)
			message = make_pair_packet (defaultmeshname.decode(), P_DEFAULTPASSWORD, session_random)
			conn.writeCharacteristic(PAIR_CHAR_UUID,message)
			conn.writeCharacteristic(STATUS_CHAR_UUID,'01')
			reply = bytearray (conn.readCharacteristic(PAIR_CHAR_UUID))
			if reply[0] == 0xd :
				logging.info("[Unpaired device] Connected (Auth OK with default password).")
				session_key = make_session_key (defaultmeshname.decode(), P_DEFAULTPASSWORD, session_random, reply[1:9])
			else :
				if reply[0] == 0xe :
					logging.info("[Unpaired device] Auth error : check name and password or make sure device is unpaired.")
				else :
					logging.info('[Unpaired device] Error while trying to auth..')
				return False

			logging.info('Step 1 - Mesh Name : ' + new_mesh_name)
			message = encrypt (session_key, new_mesh_name.encode())
			message.insert (0, 0x4)
			conn.writeCharacteristic(PAIR_CHAR_UUID, "".join("%02x" % b for b in message))
			logging.info('Step 2 - Mesh Password : ' + new_mesh_password)
			message = encrypt (session_key, new_mesh_password.encode())
			message.insert (0, 0x5)
			conn.writeCharacteristic(PAIR_CHAR_UUID, "".join("%02x" % b for b in message))
			logging.info('Step 3 - LongtermKey : ' + new_mesh_long_term_key)
			message = encrypt (session_key, new_mesh_long_term_key.encode())
			message.insert (0, 0x6)
			conn.writeCharacteristic(PAIR_CHAR_UUID, "".join("%02x" % b for b in message))

			time.sleep (2)
			logging.info('Step 4 - Get Confirmation')
			reply = bytearray (conn.readCharacteristic(PAIR_CHAR_UUID))
			if reply[0] == 0x7 :
				self.mesh_name = new_mesh_name.encode ()
				self.mesh_password = new_mesh_password.encode ()
				logging.info ("Mesh network settings accepted.")
			else:
				logging.info ("Mesh network settings change failed : %s", repr(reply))

			time.sleep (2)

		if not is_a_remote and self.auth(conn):
			logging.info('Step 5 - Set a default group')
			self.setGroupId (conn, P_DEFAULTGROUP, delete=False)
			time.sleep (1)
			value = '0407ed3c'  # green
			data = bytearray.fromhex(value)
			self.sendAction(conn,C_COLOR,data)

		conn.disconnect()
		return True

	def playScenario (self, conn, scenario):
		# ex: #DF0101-100&5|100-100&7|50-50&10|0&5|1&2|3
		steps = scenario.split("|")
		if len(steps)<3:	# must have at least 3 steps
			return
		try:
			lastStep = False
			loopTotal = int(steps[len(steps)-1])
			del steps[len(steps)-1]
			for x in xrange(loopTotal):
				for i in xrange(len(steps)):
					if i == len(steps)-1 and x == loopTotal-1 :
						lastStep = True
					slices = steps[i].split("&")
					cmd = slices[0]
					if len(slices) < 2:
						timer = 5	# default
					else:
						timer = float(slices[1])
					if cmd.startswith('#'):	# color
						data = cmd.split('-')
						if len(data) != 2:
							continue
						color = '04' + data[0].replace("#", "")
						brightness = struct.pack('B', int(int(data[1])*64/100))
						self.sendAction(conn,C_COLOR, bytearray.fromhex(color), False)
						self.sendAction(conn,C_COLOR_BRIGHTNESS, brightness, lastStep)
					elif '-' in cmd:		# white
						data = cmd.split('-')
						if len(data) != 2:
							continue
						temp = struct.pack('B', int(int(data[0])*127/100))
						brightness = struct.pack('B', int(int(data[1])*127/100))
						self.sendAction(conn,C_WHITE_TEMPERATURE, temp, False)
						self.sendAction(conn,C_WHITE_BRIGHTNESS, brightness, lastStep)
					else:	# power
						data = struct.pack('B', int(cmd))
						self.sendAction(conn, C_POWER, data, lastStep)

					if not lastStep:
						time.sleep(timer)

		except Exception as e:
			logging.debug("Something wrong with the scenario : " + str(e))

		return

	def setMeshId (self, conn, mesh_id):
		data = struct.pack ("<H", mesh_id)
		self.sendAction(conn,C_MESH_ADDRESS,data, False)
		self.mesh_id = mesh_id

	def setGroupId (self, conn, group_id, delete=False):
		data = struct.pack ("<H", group_id+32768)  # 32768 to get first hex byte to 80
		if delete:
			data = b'\x00' + data
		else:
			data = b'\x01' + data
		self.sendAction(conn,C_MESH_GROUP,data, True)
		logging.debug('Device added to group ' + str(group_id))

	def resetMesh (self, conn):
		self.sendAction(conn,C_MESH_RESET,b'\x00', False)

globals.COMPATIBILITY.append(Awoxmesh)


# LIBRARY (credits to https://github.com/Leiaz/python-awox-mesh-light)

def encrypt (key, value):
	assert (len(key) == 16)
	k = bytearray (key)
	if type(value) is str:
		val = bytearray(value.ljust (16, '\u0000'))
	else:
		val = bytearray(value.ljust (16, b'\x00'))
	#logging.debug('after val assign')
	k.reverse ()
	val.reverse ()
	cipher = AES.new(bytes(k), AES.MODE_ECB)
	val = bytearray (cipher.encrypt (bytes(val)))
	val.reverse ()
	return val

def make_checksum (key, nonce, payload):
	"""
	Args :
		key: Encryption key, 16 bytes
		nonce:
		payload: The unencrypted payload.
	"""
	base = nonce + bytearray ([len(payload)])
	base = base.ljust (16, b'\x00')
	check = encrypt (key, base)

	for i in range (0, len (payload), 16):
		check_payload = bytearray (payload[i:i+16].ljust (16, b'\x00'))
		check = bytearray([ a ^ b for (a,b) in zip(check, check_payload) ])
		check = encrypt (key, check)

	return check

def crypt_payload (key, nonce, payload):
	"""
	Used for both encrypting and decrypting.
	"""
	base = bytearray(b'\x00' + nonce)
	base = base.ljust (16, b'\x00')
	result = bytearray ()

	for i in range (0, len (payload), 16):
		enc_base = encrypt (key, base)
		result += bytearray ([ a ^ b for (a,b) in zip (enc_base, bytearray (payload[i:i+16]))])
		base[0] += 1

	return result

def make_command_packet (key, address, dest_id, command, data):
	"""
	Args :
		key: The encryption key, 16 bytes.
		address: The mac address as a string.
		dest_id: The mesh id of the command destination as a number.
		command: The command as a number.
		data: The parameters for the command as bytes.
	"""
	# Sequence number, just need to be different, idea from https://github.com/nkaminski/csrmesh
	s = urandom (3)
	# Build nonce
	a = bytearray.fromhex(address.replace (":",""))
	a.reverse()
	nonce = bytes(a[0:4] + b'\x01' + s)

	# Build payload
	dest = struct.pack ("<H", dest_id)
	payload = (dest + struct.pack('B', command) + b'\x60\x01' + data).ljust(15, b'\x00')

	# Compute checksum
	check = make_checksum (key, nonce, payload)

	# Encrypt payload
	payload = crypt_payload (key, nonce, payload)

	# Make packet
	packet = s + check[0:2] + payload
	#return packet
	return "".join("%02x" % b for b in packet)

def decrypt_packet (key, address, packet):
	"""
	Args :
		address: The mac address as a string.
		packet : The 20 bytes packet read on the characteristic.
	Returns :
		The packet with the payload part decrypted, or None if the checksum
		didn't match.

	"""
	# Build nonce
	a = bytearray.fromhex(address.replace (":",""))
	a.reverse()
	nonce = bytes(a[0:3] + packet[0:5])

	# Decrypt Payload
	payload = crypt_payload (key, nonce, packet[7:])

	# Compute checksum
	check = make_checksum (key, nonce, payload)

	# Check bytes
	if check[0:2] != packet [5:7] :
		return None

	# Decrypted packet
	dec_packet = packet [0:7] + payload
	#return dec_packet
	return "".join("%02x" % b for b in dec_packet)

def make_pair_packet (mesh_name, mesh_password, session_random):
	m_n = bytearray (mesh_name.ljust (16, '\u0000'), 'ascii')
	m_p = bytearray (mesh_password.ljust (16, '\u0000'), 'ascii')
	s_r = session_random.ljust (16, b'\x00')
	name_pass = bytearray ([ a ^ b for (a,b) in zip(m_n, m_p) ])
	enc = encrypt (s_r ,name_pass)
	packet = bytearray(b'\x0c' + session_random) # 8bytes session_random
	packet += enc[0:8]

	return "".join("%02x" % b for b in packet)

def make_session_key (mesh_name, mesh_password, session_random, response_random):
	random = session_random + response_random
	m_n = bytearray (mesh_name.ljust (16, '\u0000'), 'ascii')
	m_p = bytearray (mesh_password.ljust (16, '\u0000'), 'ascii')
	name_pass = bytearray([ a ^ b for (a,b) in zip(m_n, m_p) ])
	key = encrypt (name_pass, random)
	return key