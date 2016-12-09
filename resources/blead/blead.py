# This file is part of Jeedom.
#
# Jeedom is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Jeedom is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Jeedom. If not, see <http://www.gnu.org/licenses/>.

import subprocess
import os,re
import logging
import sys
import time
import datetime
import signal
import json
import traceback
from bluepy.btle import Scanner, DefaultDelegate
import devices
import globals

try:
	from jeedom.jeedom import *
except ImportError:
	print "Error: importing module from jeedom folder"
	sys.exit(1)
	
try:
    import queue
except ImportError:
    import Queue as queue

class ScanDelegate(DefaultDelegate):
	import globals
	def __init__(self):
		DefaultDelegate.__init__(self)

	def handleDiscovery(self, dev, isNewDev, isNewData):
		if isNewDev or isNewData:
			mac = dev.addr
			rssi = dev.rssi
			name = ''
			data =''
			manuf =''
			logging.debug(dev.getScanData())
			findDevice=False
			for (adtype, desc, value) in dev.getScanData():
				if desc == 'Complete Local Name':
					name = value
				elif 'Service Data' in desc:
					data = value
				elif desc == 'Manufacturer':
					manuf = value
			for device in globals.COMPATIBILITY:
				if device().isvalid(name,manuf):
					findDevice=True
					logging.debug('This is a ' + device().name + ' device')
					action = device().parse(data)
					action['id'] = mac.upper()
					action['type'] = device().name
					action['name'] = name
					logging.debug(action)
					if action['id'] not in globals.KNOWN_DEVICES:
						if not globals.LEARN_MODE:
							logging.debug('It\'s a known packet but not decoded because this device is not Included and I\'am not in learn mode')
							return
						else:
							logging.debug('It\'s a known packet and I don\'t known this device so I learn')
							action['learn'] = 1
							jeedom_com.add_changes('devices::'+action['id'],action)
							jeedom_com.send_change_immediate({'learn_mode' : 0});
							globals.LEARN_MODE = False
							return
					if 'rssi' not in globals.KNOWN_DEVICES[action['id']] or (globals.KNOWN_DEVICES[action['id']]['rssi']*1.1) > rssi or (globals.KNOWN_DEVICES[action['id']]['rssi']*0.9) < rssi:
						globals.KNOWN_DEVICES[action['id']]['rssi'] = rssi
						action['rssi'] = rssi
					if len(action) > 2:
						jeedom_com.add_changes('devices::'+action['id'],action)
			if not findDevice and globals.LEARN_MODE:
				logging.debug('Unknown packet for ' + name + ' : ' + mac +  ' with rssi : ' + str(rssi) + ' and data ' + data)

def listen(_device):
	global scanner
	jeedom_socket.open()
	logging.info("Start listening...")
	scanner = Scanner(int(_device[-1:])).withDelegate(ScanDelegate())
	logging.info("Preparing Scanner...")
	jeedom_com.send_change_immediate({'learn_mode' : 0});
	lastClearTimestamp = int(time.time())
	try:
		while 1:
			try:
				read_socket()
			except Exception, e:
				logging.error("Exception on socket : %s" % str(e))
			try:
				if globals.LEARN_MODE == True or (lastClearTimestamp + 19)  < int(time.time()) :
					scanner.clear()
					lastClearTimestamp = int(time.time())
				scanner.start()
				scanner.process(0.3)
				scanner.stop()
			except queue.Empty:
				continue
			except Exception, e:
				logging.error("Exception on scanner : %s" % str(e))
			try:
				read_device()
			except Exception, e:
				logging.error("Exception on read device : %s" % str(e))
			time.sleep(0.02)
	except KeyboardInterrupt:
		logging.error("KeyboardInterrupt, shutdown")
		shutdown()

def read_socket():
	try:
		global JEEDOM_SOCKET_MESSAGE
		if not JEEDOM_SOCKET_MESSAGE.empty():
			logging.debug("Message received in socket JEEDOM_SOCKET_MESSAGE")
			message = json.loads(jeedom_utils.stripped(JEEDOM_SOCKET_MESSAGE.get()))
			if message['apikey'] != _apikey:
				logging.error("Invalid apikey from socket : " + str(message))
				return
			logging.debug('Received command from jeedom : '+str(message['cmd']))
			if message['cmd'] == 'add':
				logging.debug('Add device : '+str(message['device']))
				if 'id' in message['device']:
					globals.KNOWN_DEVICES[message['device']['id']] = message['device']
			elif message['cmd'] == 'remove':
				logging.debug('Remove device : '+str(message['device']))
				if 'id' in message['device']:
					del globals.KNOWN_DEVICES[message['device']['id']]
			elif message['cmd'] == 'learnin':
				logging.debug('Enter in learn mode')
				globals.LEARN_MODE = True
				jeedom_com.send_change_immediate({'learn_mode' : 1});
			elif message['cmd'] == 'learnout':
				logging.debug('Leave learn mode')
				globals.LEARN_MODE = False
				jeedom_com.send_change_immediate({'learn_mode' : 0});
			elif message['cmd'] == 'action' or message['cmd'] == 'refresh':
				logging.debug('Attempt an action on a device')
				action_handler(message)
			elif message['cmd'] == 'logdebug':
				logging.info('Passage du demon en mode debug force')
				log = logging.getLogger()
				for hdlr in log.handlers[:]:
					log.removeHandler(hdlr)
				jeedom_utils.set_log_level('debug')
				logging.debug('<----- La preuve ;)')
			elif message['cmd'] == 'lognormal':
				logging.info('Passage du demon en mode de log initial')
				log = logging.getLogger()
				for hdlr in log.handlers[:]:
					log.removeHandler(hdlr)
				jeedom_utils.set_log_level(globals.LOG_LEVEL)
	except Exception,e:
		logging.error(str(e))

def action_handler(message):
	manuf =''
	if manuf in message['command']:
		manuf = message['command']['manuf']
	name = message['command']['name']
	result = {}
	if message['cmd'] == 'refresh':
		for compatible in globals.COMPATIBILITY:
			classname = message['command']['device']['name']
			if compatible().name.lower() == classname.lower():
				logging.debug('Attempt to refresh values')
				result = compatible().read(message['device']['id'])
				break
		if result :
			if message['device']['id'] in globals.LAST_STATE and result == globals.LAST_STATE[message['device']['id']]:
				return
			else:
				globals.LAST_STATE[message['device']['id']] = result
				jeedom_com.add_changes('devices::'+message['device']['id'],result)
	for device in globals.COMPATIBILITY:
		if device().isvalid(name,manuf):
			result = device().action(message)
			return
	return

def read_device():
	now = datetime.datetime.utcnow()
	result = {}
	try:
		for device in globals.KNOWN_DEVICES:
			mac = globals.KNOWN_DEVICES[device]['id']
			if not 'needsrefresh' in globals.KNOWN_DEVICES[device]:
				continue
			if globals.KNOWN_DEVICES[device]['needsrefresh'] <> 1:
				continue
			if mac in globals.LAST_TIME_READ and now < (globals.LAST_TIME_READ[mac]+datetime.timedelta(milliseconds=int(globals.KNOWN_DEVICES[device]['delay'])*1000)):
				continue
			else :
				globals.LAST_TIME_READ[mac] = now
				for compatible in globals.COMPATIBILITY:
					if compatible().name.lower() == str(globals.KNOWN_DEVICES[device]['name']).lower():
						result = compatible().read(mac)
						break
				if result :
					if mac in globals.LAST_STATE and result == globals.LAST_STATE[mac]:
						continue
					else:
						globals.LAST_STATE[mac] = result
						jeedom_com.add_changes('devices::'+mac,result)
	except Exception,e:
		logging.error(str(e))

def handler(signum=None, frame=None):
	logging.debug("Signal %i caught, exiting..." % int(signum))
	shutdown()
	
def shutdown():
	logging.debug("Shutdown")
	logging.debug("Removing PID file " + str(_pidfile))
	try:
		os.remove(_pidfile)
	except:
		pass
	try:
		jeedom_socket.close()
	except:
		pass
	logging.debug("Exit 0")
	sys.stdout.flush()
	os._exit(0)
	
_log_level = "error"
_socket_port = '55008'
_socket_host = 'localhost'
_pidfile = '/tmp/blead.pid'
_device = 'auto'
_apikey = ''
_callback = ''
_cycle = 0.3;

for arg in sys.argv:
	if arg.startswith("--loglevel="):
		temp, _log_level = arg.split("=")
	elif arg.startswith("--socketport="):
		temp, _socket_port = arg.split("=")
	elif arg.startswith("--sockethost="):
		temp, _socket_host = arg.split("=")
	elif arg.startswith("--device="):
		temp, _device = arg.split("=")
	elif arg.startswith("--pidfile="):
		temp, _pidfile = arg.split("=")
	elif arg.startswith("--apikey="):
		temp, _apikey = arg.split("=")
	elif arg.startswith("--callback="):
		temp, _callback = arg.split("=")
	elif arg.startswith("--cycle="):
		temp, _cycle = arg.split("=")

_socket_port = int(_socket_port)
_cycle = float(_cycle)

jeedom_utils.set_log_level(_log_level)
globals.LOG_LEVEL = _log_level
logging.info('Start blead')
logging.info('Log level : '+str(_log_level))
logging.info('Socket port : '+str(_socket_port))
logging.info('Socket host : '+str(_socket_host))
logging.info('Device : '+str(_device))
logging.info('PID file : '+str(_pidfile))
logging.info('Apikey : '+str(_apikey))
logging.info('Callback : '+str(_callback))
logging.info('Cycle : '+str(_cycle))

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)
globals.IFACE_DEVICE = int(_device[-1:])
try:
	jeedom_utils.write_pid(str(_pidfile))
	jeedom_com = jeedom_com(apikey = _apikey,url = _callback,cycle=_cycle)
	if not jeedom_com.test():
		logging.error('Network communication issues. Please fix your Jeedom network configuration.')
		shutdown()
	jeedom_socket = jeedom_socket(port=_socket_port,address=_socket_host)
	listen(_device)
except Exception,e:
	logging.error('Fatal error : '+str(e))
	logging.debug(traceback.format_exc())
	shutdown()
