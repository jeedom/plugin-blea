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
from threading import Timer
import thread
from multiconnect import Connector
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
			connectable = dev.connectable
			addrType = dev.addrType
			name = ''
			data =''
			manuf =''
			action = {}
			onlypresent = False
			if mac not in globals.IGNORE:
				logging.debug(str(dev.getScanData()) +' '+str(connectable) +' '+ str(addrType) +' '+ str(mac))
			findDevice=False
			for (adtype, desc, value) in dev.getScanData():
				if desc == 'Complete Local Name':
					name = value.strip()
				elif 'Service Data' in desc:
					data = value.strip()
				elif desc == 'Manufacturer':
					manuf = value.strip()
			for device in globals.COMPATIBILITY:
				if device().isvalid(name,manuf):
					findDevice=True
					if device().ignoreRepeat and mac in globals.IGNORE:
						return
					globals.IGNORE.append(mac)
					logging.debug('This is a ' + device().name + ' device ' +str(mac))
					if mac.upper() not in globals.KNOWN_DEVICES:
						if not globals.LEARN_MODE:
							logging.debug('It\'s a known packet but not decoded because this device is not Included and I\'am not in learn mode ' +str(mac))
							return
					if mac.upper() in globals.KNOWN_DEVICES:
						if globals.LEARN_MODE:
							logging.debug('Known device and in Learn Mode ignoring ' +str(mac))
							return
					globals.PENDING_ACTION = True
					try:
						action = device().parse(data,mac,name)
					except Exception, e:
						logging.debug('Parse failed ' +str(mac) + ' ' + str(e))
					if not action:
						return
					globals.PENDING_ACTION = False
					action['id'] = mac.upper()
					action['type'] = device().name
					action['name'] = name
					action['rssi'] = rssi
					action['source'] = globals.daemonname
					action['rawdata'] = str(dev.getScanData())
					if globals.LEARN_MODE:
						logging.debug('It\'s a known packet and I don\'t known this device so I learn ' +str(mac))
						action['learn'] = 1
						if 'version' in action:
							action['type']= action['version']
						logging.debug(action)
						globals.JEEDOM_COM.add_changes('devices::'+action['id'],action)
						return
					if len(action) > 2:
						globals.JEEDOM_COM.add_changes('devices::'+action['id'],action)
			if not findDevice:
				action['id'] = mac.upper()
				action['type'] = 'default'
				action['name'] = name
				action['rssi'] = rssi
				action['source'] = globals.daemonname
				action['rawdata'] = str(dev.getScanData())
				if mac in globals.IGNORE:
					return
				globals.IGNORE.append(mac)
				if mac.upper() not in globals.KNOWN_DEVICES:
					if not globals.LEARN_MODE:
						logging.debug('It\'s an unknown packet but not sent because this device is not Included and I\'am not in learn mode ' +str(mac))
						return
					else:
						if globals.LEARN_MODE_ALL == 0:
							logging.debug('It\'s a unknown packet and I don\'t known but i\'m configured to ignore unknow packet ' +str(mac))
							return
						logging.debug('It\'s a unknown packet and I don\'t known this device so I learn ' +str(mac))
						action['learn'] = 1
						logging.debug(action)
						globals.JEEDOM_COM.add_changes('devices::'+action['id'],action)
				else:
					if len(action) > 2:
						if globals.LEARN_MODE:
							logging.debug('It\'s an unknown packet i know this device but i\'m in learn mode ignoring ' +str(mac))
							return
						logging.debug('It\'s a unknown packet and I known this device so I send ' +str(mac))
						logging.debug(action)
						globals.JEEDOM_COM.add_changes('devices::'+action['id'],action)

def listen():
	global scanner
	globals.PENDING_ACTION=False
	jeedom_socket.open()
	logging.info("Start listening...")
	globals.SCANNER = Scanner(globals.IFACE_DEVICE).withDelegate(ScanDelegate())
	logging.info("Preparing Scanner...")
	globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname});
	thread.start_new_thread( read_socket, ('socket',))
	logging.debug('Read Socket Thread Launched')
	thread.start_new_thread( read_device, ('device',))
	logging.debug('Read Device Thread Launched')
	thread.start_new_thread( heartbeat_handler, (19,))
	logging.debug('Heartbeat Thread Launched')
	globals.JEEDOM_COM.send_change_immediate({'started' : 1,'source' : globals.daemonname});
	try:
		while 1:
			try:
				if globals.LEARN_MODE or (globals.LAST_CLEAR + 39)  < int(time.time()):
					globals.SCANNER.clear()
					globals.IGNORE[:] = []
					globals.LAST_CLEAR = int(time.time())
				globals.SCANNER.start()
				if globals.LEARN_MODE:
					globals.SCANNER.process(3)
				else:
					globals.SCANNER.process(0.3)
				globals.SCANNER.stop()
				if globals.SCAN_ERRORS > 0:
					logging.info("Attempt to recover successful, reseting counter")
					globals.SCAN_ERRORS = 0
				while globals.PENDING_ACTION:
					time.sleep(0.01)
			except Exception, e:
				if not globals.PENDING_ACTION and not globals.LEARN_MODE: 
					if globals.SCAN_ERRORS < 5:
						globals.SCAN_ERRORS = globals.SCAN_ERRORS+1
						globals.SCANNER = Scanner(globals.IFACE_DEVICE).withDelegate(ScanDelegate())
					elif globals.SCAN_ERRORS >=5 and globals.SCAN_ERRORS< 8:
						globals.SCAN_ERRORS = globals.SCAN_ERRORS+1
						logging.warning("Exception on scanner (trying to resolve by myself " + str(globals.SCAN_ERRORS) + "): %s" % str(e))
						os.system('hciconfig ' + globals.device + ' down')
						os.system('hciconfig ' + globals.device + ' up')
						globals.SCANNER = Scanner(globals.IFACE_DEVICE).withDelegate(ScanDelegate())
					else:
						logging.error("Exception on scanner (didn't resolve there is an issue with bluetooth) : %s" % str(e))
						logging.info("Shutting down due to errors")
						globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname});
						time.sleep(2)
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
						if message['device']['id'] in globals.KEEPED_CONNECTION:
							logging.debug("This antenna should not keep a connection with this device, disconnecting " + str(message['device']['id']))
							try:
								globals.KEEPED_CONNECTION[message['device']['id']].disconnect()
							except Exception, e:
								logging.debug(str(e))
							if message['device']['id'] in globals.KEEPED_CONNECTION:
								del globals.KEEPED_CONNECTION[message['device']['id']]
							logging.debug("Removed from keep connection list " + str(message['device']['id']))
				elif message['cmd'] == 'learnin':
					logging.debug('Enter in learn mode')
					globals.LEARN_MODE_ALL = 0
					if message['allowAll'] == '1' :
						globals.LEARN_MODE_ALL = 1
					globals.LEARN_MODE = True
					globals.LEARN_BEGIN = int(time.time())
					globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 1,'source' : globals.daemonname});
				elif message['cmd'] == 'learnout':
					logging.debug('Leave learn mode')
					globals.LEARN_MODE = False
					globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname});
				elif message['cmd'] in ['action','refresh','helper','helperrandom']:
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
					globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname});
					time.sleep(2)
					shutdown()
		except Exception,e:
			logging.error("Exception on socket : %s" % str(e))
		time.sleep(0.3)
		
def heartbeat_handler(delay):
	while 1:
		for device in globals.KNOWN_DEVICES:
			if not globals.PENDING_ACTION and globals.KNOWN_DEVICES[device]['islocked'] == 0 or globals.KNOWN_DEVICES[device]['emitterallowed'] not in [globals.daemonname,'all']:
				if device in globals.KEEPED_CONNECTION:
					logging.debug("This antenna should not keep a connection with this device, disconnecting " + str(device))
					try:
						globals.KEEPED_CONNECTION[device].disconnect()
					except Exception, e:
						logging.debug(str(e))
					if device in globals.KEEPED_CONNECTION:
						del globals.KEEPED_CONNECTION[device]
					logging.debug("Removed from keep connection list " + str(device))
		if globals.LEARN_MODE and (globals.LEARN_BEGIN + 60)  < int(time.time()):
			globals.LEARN_MODE = False
			logging.debug('Quitting learn mode (60s elapsed)')
			globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname});
		if (globals.LAST_VIRTUAL + 60)  < int(time.time()):
			for device in globals.KNOWN_DEVICES:
				action={}
				if globals.KNOWN_DEVICES[device]['islocked'] == 1 and globals.KNOWN_DEVICES[device]['emitterallowed'] == globals.daemonname:
					if device in list(globals.KEEPED_CONNECTION):
						logging.debug("Virtually send rssi to device connected as they are not seen anymore " + str(device))
						action['id'] = device
						action['rssi'] = 'same'
						action['present'] = 1
						action['source'] = globals.daemonname
						globals.JEEDOM_COM.add_changes('devices::'+device,action)
						globals.LAST_VIRTUAL = int(time.time())
		if (globals.LAST_BEAT + 55)  < int(time.time()):
			globals.JEEDOM_COM.send_change_immediate({'heartbeat' : 1,'source' : globals.daemonname});
			globals.LAST_BEAT = int(time.time())
		time.sleep(1)

def action_handler(message):
	manuf =''
	if manuf in message['command']:
		manuf = message['command']['manuf']
	name = message['command']['name']
	result = {}
	if message['cmd'] == 'helper' or message['cmd'] == 'helperrandom':
		type ='public'
		if message['cmd'] == 'helperrandom':
			type = 'random'
		try:
			globals.PENDING_ACTION = True
			mac = message['device']['id']
			if mac in globals.KEEPED_CONNECTION:
				logging.debug('Already a connection for ' + mac + ' use it')
				conn = globals.KEEPED_CONNECTION[mac]
			else:
				logging.debug('Creating a new connection for ' + mac)
				conn = Connector(mac)
				globals.KEEPED_CONNECTION[mac]=conn
				conn.connect(type=type)
			if not conn.isconnected:
				conn.connect(type=type)
				if not conn.isconnected:
					globals.PENDING_ACTION = False
					return
			try:
				conn.helper()
			except Exception,e:
				logging.debug("Helper failed : %s" % str(e))
				globals.PENDING_ACTION = False
			conn.disconnect()
			globals.PENDING_ACTION = False
			return
		except Exception,e:
				logging.debug("Helper failed : %s" % str(e))
				globals.PENDING_ACTION = False
	elif message['cmd'] == 'refresh':
		for compatible in globals.COMPATIBILITY:
			classname = message['command']['device']['name']
			if compatible().name.lower() == classname.lower():
				logging.debug('Attempt to refresh values')
				globals.PENDING_ACTION = True
				try:
					result = compatible().read(message['device']['id'])
				except Exception,e:
					logging.debug("Refresh failed : %s" % str(e))
				globals.PENDING_ACTION = False
				break
		if result and len(result) > 2 :
			if message['device']['id'] in globals.LAST_STATE and result == globals.LAST_STATE[message['device']['id']]:
				return
			else:
				globals.LAST_STATE[message['device']['id']] = result
				result['source'] = globals.daemonname
				globals.JEEDOM_COM.add_changes('devices::'+message['device']['id'],result)
				return
	else:
		for device in globals.COMPATIBILITY:
			if device().isvalid(name,manuf):
				globals.PENDING_ACTION = True
				try:
					result = device().action(message)
				except Exception,e:
						logging.debug("Action failed : %s" % str(e))
				globals.PENDING_ACTION = False
				if result :
					if message['device']['id'] in globals.LAST_STATE and result == globals.LAST_STATE[message['device']['id']]:
						return
					else:
						globals.LAST_STATE[message['device']['id']] = result
						result['source'] = globals.daemonname
						globals.JEEDOM_COM.add_changes('devices::'+message['device']['id'],result)
						return
				return
	return

def read_device(name):
	time.sleep(120)
	while 1:
		now = datetime.datetime.utcnow()
		result = {}
		try:
			for device in list(globals.KNOWN_DEVICES):
				mac = globals.KNOWN_DEVICES[device]['id']
				if globals.KNOWN_DEVICES[mac]['refresherallowed'] not in [globals.daemonname,'all']:
					continue
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
							try:
								result = compatible().read(mac)
							except Exception,e:
								try:
									result = compatible().read(mac)
								except Exception,e:
									try:
										result = compatible().read(mac)
									except Exception,e:
										logging.debug("Refresh failed : %s" % str(e))
							globals.PENDING_ACTION = False
							break
					if result :
						if mac in globals.LAST_STATE and result == globals.LAST_STATE[mac]:
							continue
						else:
							globals.LAST_STATE[mac] = result
							result['source'] = globals.daemonname
							globals.JEEDOM_COM.add_changes('devices::'+mac,result)
		except Exception,e:
			logging.error("Exception on read device : %s" % str(e))
		time.sleep(5)

def handler(signum=None, frame=None):
	logging.debug("Signal %i caught, exiting..." % int(signum))
	shutdown()
	
def shutdown():
	logging.debug("Shutdown")
	logging.debug("Removing PID file " + str(globals.pidfile))
	logging.debug("Closing all potential bluetooth connection")
	for device in list(globals.KEEPED_CONNECTION):
		logging.debug("This antenna should not keep a connection with this device, disconnecting " + str(device))
		try:
			globals.KEEPED_CONNECTION[device].disconnect(True)
			logging.debug("Connection closed for " + str(device))
		except Exception, e:
			logging.debug(str(e))
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
try:
	jeedom_utils.write_pid(str(globals.pidfile))
	globals.JEEDOM_COM = jeedom_com(apikey = globals.apikey,url = globals.callback,cycle=globals.cycle)
	if not globals.JEEDOM_COM.test():
		logging.error('Network communication issues. Please fix your Jeedom network configuration.')
		shutdown()
	jeedom_socket = jeedom_socket(port=globals.socketport,address=globals.sockethost)
	listen()
except Exception,e:
	logging.error('Fatal error : '+str(e))
	logging.debug(traceback.format_exc())
	shutdown()
