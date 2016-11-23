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
					if globals.EXCLUDE_MODE:
						globals.EXCLUDE_MODE = False
						logging.debug('It\'s a known packet and I am in exclude mode, i delete the device')
						jeedom_com.send_change_immediate({'exclude_mode' : 0, 'deviceId' : mac });
						return
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
				pass
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
					globals.KNOWN_DEVICES[message['device']['id']] = {}
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
			elif message['cmd'] == 'excludein':
				logging.debug('Enter exclude mode')
				globals.EXCLUDE_MODE = True
				jeedom_com.send_change_immediate({'exclude_mode' : 1});
			elif message['cmd'] == 'excludeout':
				logging.debug('Leave exclude mode')
				globals.EXCLUDE_MODE = False
				jeedom_com.send_change_immediate({'exclude_mode' : 0});
	except Exception,e:
		logging.error(str(e))

def handler(signum=None, frame=None):
	logging.debug("Signal %i caught, exiting..." % int(signum))
	shutdown()
	
def shutdown():
	logging.debug("Shutdown")
	logging.debug("Removing PID file " + str(_pidfile))
	try:
		toggle_dongle()
	except:
		pass
	try:
		os.remove(_pidfile)
	except:
		pass
	try:
		jeedom_socket.close()
	except:
		pass
	os.system("sudo pkill -f 'hcidump -R'")
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
