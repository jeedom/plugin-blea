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
import argparse
import time
import datetime
import signal
import json
import traceback
from bluepy.btle import Scanner, DefaultDelegate
import globals
from threading import Thread
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
					action = device().parse(data,mac)
					action['id'] = mac.upper()
					action['type'] = device().name
					action['name'] = name
					action['rssi'] = rssi
					logging.debug(action)
					if action['id'] not in globals.KNOWN_DEVICES:
						if not globals.LEARN_MODE:
							logging.debug('It\'s a known packet but not decoded because this device is not Included and I\'am not in learn mode')
							return
						else:
							logging.debug('It\'s a known packet and I don\'t known this device so I learn')
							action['learn'] = 1
							if 'version' in action:
								action['type']= action['version']
							jeedom_com.add_changes('devices::'+action['id'],action)
							jeedom_com.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname});
							globals.LEARN_MODE = False
							return
					if len(action) > 2:
						action['source'] = globals.daemonname
						jeedom_com.add_changes('devices::'+action['id'],action)
			if not findDevice and globals.LEARN_MODE:
				logging.debug('Unknown packet for ' + name + ' : ' + mac +  ' with rssi : ' + str(rssi) + ' and data ' + data)

def listen():
	global scanner
	jeedom_socket.open()
	logging.info("Start listening...")
	globals.SCANNER = Scanner(globals.IFACE_DEVICE).withDelegate(ScanDelegate())
	logging.info("Preparing Scanner...")
	jeedom_com.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname});
	lastClearTimestamp = int(time.time())
	thread.start_new_thread( read_socket, ('socket',))
	logging.debug('Read Socket Thread Launched')
	thread.start_new_thread( read_device, ('device',))
	logging.debug('Read Device Thread Launched')
	jeedom_com.send_change_immediate({'started' : 1,'source' : globals.daemonname});
	try:
		while 1:
			try:
				if globals.LEARN_MODE == True or (lastClearTimestamp + 19)  < int(time.time()) :
					globals.SCANNER.clear()
					lastClearTimestamp = int(time.time())
				globals.SCANNER.start()
				if globals.LEARN_MODE == True:
					globals.SCANNER.process(3)
				else:
					globals.SCANNER.process(0.3)
				globals.SCANNER.stop()
				if globals.SCAN_ERRORS > 0:
					logging.info("Attempt to recover successful, reseting counter")
					globals.SCAN_ERRORS = 0
			except queue.Empty:
				continue
			except Exception, e:
				if not globals.PENDING_ACTION: 
					if globals.SCAN_ERRORS < 5:
						globals.SCAN_ERRORS = globals.SCAN_ERRORS+1
						logging.warning("Exception on scanner (trying to resolve by myself attempt " + str(globals.SCAN_ERRORS) + "): %s" % str(e))
						os.system('hciconfig ' + globals.device + ' down')
						os.system('hciconfig ' + globals.device + ' up')
						globals.SCANNER = Scanner(globals.IFACE_DEVICE).withDelegate(ScanDelegate())
					else:
						logging.error("Exception on scanner (didn't resolve there is an issue with bluetooth) : %s" % str(e))
						logging.info("Shutting down due to errors")
						shutdown()
				time.sleep(0.02)
	except KeyboardInterrupt:
		logging.error("KeyboardInterrupt, shutdown")
		shutdown()

def read_socket(name):
	while 1:
		try:
			global JEEDOM_SOCKET_MESSAGE
			if not JEEDOM_SOCKET_MESSAGE.empty():
				logging.debug("Message received in socket JEEDOM_SOCKET_MESSAGE")
				message = json.loads(jeedom_utils.stripped(JEEDOM_SOCKET_MESSAGE.get()))
				if message['apikey'] != globals.apikey:
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
					jeedom_com.send_change_immediate({'learn_mode' : 1,'source' : globals.daemonname});
				elif message['cmd'] == 'learnout':
					logging.debug('Leave learn mode')
					globals.LEARN_MODE = False
					jeedom_com.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname});
				elif message['cmd'] == 'action' or message['cmd'] == 'refresh':
					logging.debug('Attempt an action on a device')
					thread.start_new_thread( action_handler, (message,))
					logging.debug('Thread Launched')
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
					jeedom_utils.set_log_level(globals.log_level)
				elif message['cmd'] == 'stop':
					logging.info('Arret du demon sur demande socket')
					shutdown()
		except Exception,e:
			logging.error("Exception on socket : %s" % str(e))
		time.sleep(0.3)

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
				globals.PENDING_ACTION = True
				result = compatible().read(message['device']['id'])
				globals.PENDING_ACTION = False
				break
		if result :
			if message['device']['id'] in globals.LAST_STATE and result == globals.LAST_STATE[message['device']['id']]:
				return
			else:
				globals.LAST_STATE[message['device']['id']] = result
				result['source'] = globals.daemonname
				jeedom_com.add_changes('devices::'+message['device']['id'],result)
				return
	for device in globals.COMPATIBILITY:
		if device().isvalid(name,manuf):
			globals.PENDING_ACTION = True
			result = device().action(message)
			globals.PENDING_ACTION = False
			if result :
				if message['device']['id'] in globals.LAST_STATE and result == globals.LAST_STATE[message['device']['id']]:
					return
				else:
					globals.LAST_STATE[message['device']['id']] = result
					result['source'] = globals.daemonname
					jeedom_com.add_changes('devices::'+message['device']['id'],result)
					return
			return
	return

def read_device(name):
	while 1:
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
							globals.PENDING_ACTION = True
							result = compatible().read(mac)
							globals.PENDING_ACTION = False
							break
					if result :
						if mac in globals.LAST_STATE and result == globals.LAST_STATE[mac]:
							continue
						else:
							globals.LAST_STATE[mac] = result
							result['source'] = globals.daemonname
							jeedom_com.add_changes('devices::'+mac,result)
		except Exception,e:
			logging.error("Exception on read device : %s" % str(e))
		time.sleep(1)

def handler(signum=None, frame=None):
	logging.debug("Signal %i caught, exiting..." % int(signum))
	shutdown()
	
def shutdown():
	logging.debug("Shutdown")
	logging.debug("Removing PID file " + str(globals.pidfile))
	try:
		os.remove(globals.pidfile)
	except:
		pass
	try:
		jeedom_socket.close()
	except:
		pass
	logging.debug("Exit 0")
	sys.stdout.flush()
	os._exit(0)

parser = argparse.ArgumentParser(description='Blead Daemon for Jeedom plugin')
parser.add_argument("--device", help="Device", type=str)
parser.add_argument("--loglevel", help="Log Level for the daemon", type=str)
parser.add_argument("--pidfile", help="Value to write", type=str)
parser.add_argument("--callback", help="Value to write", type=str)
parser.add_argument("--apikey", help="Value to write", type=str)
parser.add_argument("--socketport", help="Socket Port", type=str)
parser.add_argument("--sockethost", help="Socket Host", type=str)
parser.add_argument("--daemonname", help="Daemon Name", type=str)
parser.add_argument("--cycle", help="Cycle to send event", type=str)
args = parser.parse_args()

if args.device:
	globals.device = args.device
if args.loglevel:
	globals.log_level = args.loglevel
if args.pidfile:
	globals.pidfile = args.pidfile
if args.callback:
	globals.callback = args.callback
if args.apikey:
	globals.apikey = args.apikey
if args.cycle:
	globals.cycle = float(args.cycle)
if args.socketport:
	globals.socketport = args.socketport
if args.sockethost:
	globals.sockethost = args.sockethost
if args.daemonname:
	globals.daemonname = args.daemonname

globals.socketport = int(globals.socketport)
globals.cycle = float(globals.cycle)

jeedom_utils.set_log_level(globals.log_level)
logging.info('Start blead')
logging.info('Log level : '+str(globals.log_level))
logging.info('Socket port : '+str(globals.socketport))
logging.info('Socket host : '+str(globals.sockethost))
logging.info('Device : '+str(globals.device))
logging.info('PID file : '+str(globals.pidfile))
logging.info('Apikey : '+str(globals.apikey))
logging.info('Callback : '+str(globals.callback))
logging.info('Cycle : '+str(globals.cycle))
import devices
signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)
globals.IFACE_DEVICE = int(globals.device[-1:])
os.system('hciconfig ' + globals.device + ' down')
os.system('hciconfig ' + globals.device + ' up')
try:
	jeedom_utils.write_pid(str(globals.pidfile))
	jeedom_com = jeedom_com(apikey = globals.apikey,url = globals.callback,cycle=globals.cycle)
	if not jeedom_com.test():
		logging.error('Network communication issues. Please fix your Jeedom network configuration.')
		shutdown()
	jeedom_socket = jeedom_socket(port=globals.socketport,address=globals.sockethost)
	listen()
except Exception,e:
	logging.error('Fatal error : '+str(e))
	logging.debug(traceback.format_exc())
	shutdown()
