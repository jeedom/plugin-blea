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
import threading
from multiconnect import Connector
try:
	from jeedom.jeedom import *
except ImportError:
	print("Error: importing module from jeedom folder")
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
				logging.debug('SCANNER------'+str(dev.getScanData()) +' '+str(connectable) +' '+ str(addrType) +' '+ str(mac))
			findDevice=False
			for (adtype, desc, value) in dev.getScanData():
				if desc == 'Complete Local Name':
					name = value.strip()
				elif 'Service Data' in desc:
					data = value.strip()
				elif desc == 'Manufacturer':
					manuf = value.strip()
			if mac.upper() in globals.KNOWN_DEVICES:
				if 'name' in globals.KNOWN_DEVICES[mac.upper()]:
					if name == '':
						logging.debug('No name in data but i know it is : ' +globals.KNOWN_DEVICES[mac.upper()]['name'])
						name = globals.KNOWN_DEVICES[mac.upper()]['name']
			for device in globals.COMPATIBILITY:
				if device().isvalid(name,manuf,data,mac):
					findDevice=True
					if device().ignoreRepeat and mac in globals.IGNORE:
						logging.debug('Ignore repeat for this interval' +globals.KNOWN_DEVICES[mac.upper()]['name'])
						return
					globals.IGNORE.append(mac)
					logging.debug('SCANNER------This is a ' + device().name + ' device ' +str(mac))
					if mac.upper() not in globals.KNOWN_DEVICES:
						if not globals.LEARN_MODE:
							logging.debug('SCANNER------It\'s a known packet but not decoded because this device is not Included and I\'am not in learn mode ' +str(mac))
							return
					if mac.upper() in globals.KNOWN_DEVICES:
						if globals.LEARN_MODE:
							logging.debug('SCANNER------Known device and in Learn Mode ignoring ' +str(mac))
							return
						globals.KNOWN_DEVICES[mac.upper()]['localname'] = name
					try:
						action = device().parse(data,mac,name,manuf)
					except Exception as e:
						logging.debug('SCANNER------Parse failed ' +str(mac) + ' ' + str(e))
					action['id'] = mac.upper()
					action['type'] = device().name
					action['name'] = name
					action['rssi'] = rssi
					action['source'] = globals.daemonname
					action['rawdata'] = str(dev.getScanData())
					action['present'] = 1
					if globals.LEARN_MODE:
						if (globals.LEARN_TYPE == 'all' or globals.LEARN_TYPE == device().name) :
							logging.debug('SCANNER------It\'s a known packet and I don\'t known this device so I learn ' +str(mac))
							action['learn'] = 1
							if 'version' in action:
								action['type']= action['version']
							if 'bind' in action and action['bind'] == False:
								return
							logging.debug(action)
							globals.JEEDOM_COM.add_changes('devices::'+action['id'],action)
						else:
							logging.debug('SCANNER------It\'s a known packet and I don\'t known this device ' +str(mac) + ' but i only want ' + globals.LEARN_TYPE + ' and this is ' +action['type'])
						return
					if len(action) > 2:
						if action['id'] not in globals.SEEN_DEVICES:
							globals.SEEN_DEVICES[action['id']] = {}
						if 'present' not in globals.SEEN_DEVICES[action['id']]:
							globals.SEEN_DEVICES[action['id']]['lastseen'] = int(time.time())
							globals.SEEN_DEVICES[action['id']]['present'] = 1
							logging.info('First Time SEEEEEEEEEN------' + str(action['id']) + ' || ' +str(globals.SEEN_DEVICES))
						elif globals.SEEN_DEVICES[action['id']]['present'] == 0:
							globals.SEEN_DEVICES[action['id']]['lastseen'] = int(time.time())
							globals.SEEN_DEVICES[action['id']]['present'] = 1
							logging.info('RE SEEEEEEEEEN------' + str(action['id']) + ' || ' +str(globals.SEEN_DEVICES))
						elif globals.SEEN_DEVICES[action['id']]['present'] == 1:
							globals.SEEN_DEVICES[action['id']]['lastseen'] = int(time.time())
						logging.debug(action)
						globals.JEEDOM_COM.add_changes('devices::'+action['id'],action)
			if not findDevice:
				action['id'] = mac.upper()
				action['type'] = 'default'
				action['name'] = name
				action['rssi'] = rssi
				action['source'] = globals.daemonname
				action['rawdata'] = str(dev.getScanData())
				action['present'] = 1
				if mac in globals.IGNORE:
					return
				globals.IGNORE.append(mac)
				if mac.upper() not in globals.KNOWN_DEVICES:
					if not globals.LEARN_MODE:
						logging.debug('SCANNER------It\'s an unknown packet but not sent because this device is not Included and I\'am not in learn mode ' +str(mac))
						return
					else:
						if globals.LEARN_MODE_ALL == 0:
							logging.debug('SCANNER------It\'s a unknown packet and I don\'t known but i\'m configured to ignore unknow packet ' +str(mac))
							return
						if (globals.LEARN_TYPE == 'all' or globals.LEARN_TYPE == 'unknown') :
							logging.debug('SCANNER------It\'s a unknown packet and I don\'t known this device so I learn ' +str(mac))
							action['learn'] = 1
							logging.debug(action)
							globals.JEEDOM_COM.add_changes('devices::'+action['id'],action)
						else:
							logging.debug('SCANNER------It\'s a known packet and I don\'t known this device ' +str(mac) + ' but i only want ' + globals.LEARN_TYPE + ' and this is ' +action['type'])
				else:
					if len(action) > 2:
						if globals.LEARN_MODE:
							logging.debug('SCANNER------It\'s an unknown packet i know this device but i\'m in learn mode ignoring ' +str(mac))
							return
						logging.debug('SCANNER------It\'s a unknown packet and I known this device so I send ' +str(mac))
						if action['id'] not in globals.SEEN_DEVICES:
							globals.SEEN_DEVICES[action['id']] = {}
						if 'present' not in globals.SEEN_DEVICES[action['id']]:
							globals.SEEN_DEVICES[action['id']]['lastseen'] = int(time.time())
							globals.SEEN_DEVICES[action['id']]['present'] = 1
							logging.info('First Time SEEEEEEEEEN------' + str(action['id']) + ' || ' +str(globals.SEEN_DEVICES))
						elif globals.SEEN_DEVICES[action['id']]['present'] == 0:
							globals.SEEN_DEVICES[action['id']]['lastseen'] = int(time.time())
							globals.SEEN_DEVICES[action['id']]['present'] = 1
							logging.info('RE SEEEEEEEEEN------' + str(action['id']) + ' || ' +str(globals.SEEN_DEVICES))
						elif globals.SEEN_DEVICES[action['id']]['present'] == 1:
							globals.SEEN_DEVICES[action['id']]['lastseen'] = int(time.time())
						logging.debug(action)
						globals.JEEDOM_COM.add_changes('devices::'+action['id'],action)

def listen():
	global scanner
	globals.PENDING_ACTION=False
	jeedom_socket.open()
	logging.info("GLOBAL------Start listening...")
	globals.SCANNER = Scanner(globals.IFACE_DEVICE).withDelegate(ScanDelegate())
	logging.info("GLOBAL------Preparing Scanner...")
	globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname});
	threading.Thread( target=read_socket, args=('socket',)).start()
	logging.debug('GLOBAL------Read Socket Thread Launched')
	threading.Thread( target=read_device, args=('device',)).start()
	logging.debug('GLOBAL------Read Device Thread Launched')
	threading.Thread( target=heartbeat_handler, args=(19,)).start()
	logging.debug('GLOBAL------Heartbeat Thread Launched')
	globals.JEEDOM_COM.send_change_immediate({'started' : 1,'source' : globals.daemonname,'version' : globals.DAEMON_VERSION});
	while not globals.READY:
		time.sleep(1)
	try:
		while 1:
			try:
				while globals.PENDING_ACTION:
					time.sleep(0.01)
				if globals.LEARN_MODE or (globals.LAST_CLEAR + globals.SCAN_INTERVAL)  < int(time.time()):
					logging.debug('SCANNER------Clearing seen')
					globals.SCANNER.clear()
					globals.IGNORE[:] = []
					globals.LAST_CLEAR = int(time.time())
				if globals.LEARN_MODE:
					globals.SCANNER.start(passive=False)
					globals.SCANNER.process(3)
				else:
					if globals.SCAN_MODE == 'passive':
						globals.SCANNER.start(passive=True)
					else:
						globals.SCANNER.start(passive=False)
					globals.SCANNER.process(0.3)
				globals.SCANNER.stop()
				if globals.SCAN_ERRORS > 0:
					logging.info("GLOBAL------Attempt to recover successful, reseting counter")
					globals.SCAN_ERRORS = 0
			except Exception as e:
				if not globals.PENDING_ACTION and not globals.LEARN_MODE:
					if globals.SCAN_ERRORS < 10:
						globals.SCAN_ERRORS = globals.SCAN_ERRORS+1
						globals.SCANNER = Scanner(globals.IFACE_DEVICE).withDelegate(ScanDelegate())
					elif globals.SCAN_ERRORS >=10 and globals.SCAN_ERRORS< 20:
						globals.SCAN_ERRORS = globals.SCAN_ERRORS+1
						logging.warning("GLOBAL------Exception on scanner (trying to resolve by myself " + str(globals.SCAN_ERRORS) + "): %s" % str(e))
						os.system('sudo rfkill unblock all >/dev/null 2>&1')
						os.system('sudo hciconfig ' + globals.device + ' down')
						os.system('sudo hciconfig ' + globals.device + ' up')
						globals.SCANNER = Scanner(globals.IFACE_DEVICE).withDelegate(ScanDelegate())
					else:
						logging.error("GLOBAL------Exception on scanner (didn't resolve there is an issue with bluetooth) : %s" % str(e))
						logging.info("GLOBAL------Shutting down due to errors")
						globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname});
						time.sleep(2)
						shutdown()
			time.sleep(0.02)
	except KeyboardInterrupt:
		logging.error("GLOBAL------KeyboardInterrupt, shutdown")
		shutdown()

def read_socket(name):
	while 1:
		try:
			global JEEDOM_SOCKET_MESSAGE
			if not JEEDOM_SOCKET_MESSAGE.empty():
				logging.debug("SOCKET-READ------Message received in socket JEEDOM_SOCKET_MESSAGE")
				message = JEEDOM_SOCKET_MESSAGE.get().decode('utf-8')
				message =json.loads(message)
				if message['apikey'] != globals.apikey:
					logging.error("SOCKET-READ------Invalid apikey from socket : " + str(message))
					return
				logging.debug('SOCKET-READ------Received command from jeedom : '+str(message['cmd']))
				if message['cmd'] == 'add':
					logging.debug('SOCKET-READ------Add device : '+str(message['device']))
					if 'id' in message['device']:
						globals.KNOWN_DEVICES[message['device']['id']] = message['device']
				elif message['cmd'] == 'remove':
					logging.debug('SOCKET-READ------Remove device : '+str(message['device']))
					if 'id' in message['device']:
						del globals.KNOWN_DEVICES[message['device']['id']]
						if message['device']['id'] in globals.KEEPED_CONNECTION:
							logging.debug("SOCKET-READ------This antenna should not keep a connection with this device, disconnecting " + str(message['device']['id']))
							try:
								globals.KEEPED_CONNECTION[message['device']['id']].disconnect()
							except Exception as e:
								logging.debug(str(e))
							if message['device']['id'] in globals.KEEPED_CONNECTION:
								del globals.KEEPED_CONNECTION[message['device']['id']]
							logging.debug("SOCKET-READ------Removed from keep connection list " + str(message['device']['id']))
				elif message['cmd'] == 'learnin':
					logging.debug('SOCKET-READ------Enter in learn mode')
					globals.LEARN_MODE_ALL = 0
					if message['allowAll'] == '1' :
						globals.LEARN_MODE_ALL = 1
					globals.LEARN_TYPE = message['type']
					globals.LEARN_MODE = True
					globals.LEARN_BEGIN = int(time.time())
					globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 1,'source' : globals.daemonname});
				elif message['cmd'] == 'learnout':
					logging.debug('SOCKET-READ------Leave learn mode')
					globals.LEARN_MODE = False
					globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname});
				elif message['cmd'] in ['action','refresh','helper','helperrandom']:
					logging.debug('SOCKET-READ------Attempt an action on a device')
					threading.Thread( target=action_handler, args=(message,)).start()
					logging.debug('SOCKET-READ------Action Thread Launched')
				elif message['cmd'] == 'logdebug':
					logging.info('SOCKET-READ------Passage du demon en mode debug force')
					log = logging.getLogger()
					for hdlr in log.handlers[:]:
						log.removeHandler(hdlr)
					jeedom_utils.set_log_level('debug')
					logging.debug('SOCKET-READ------<----- La preuve ;)')
				elif message['cmd'] == 'lognormal':
					logging.info('SOCKET-READ------Passage du demon en mode de log initial')
					log = logging.getLogger()
					for hdlr in log.handlers[:]:
						log.removeHandler(hdlr)
					jeedom_utils.set_log_level(globals.log_level)
				elif message['cmd'] == 'stop':
					logging.info('SOCKET-READ------Arret du demon sur demande socket')
					globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname});
					time.sleep(2)
					shutdown()
				elif message['cmd'] == 'ready':
					logging.debug('Daemon is ready')
					globals.READY = True
		except Exception as e:
			logging.error("SOCKET-READ------Exception on socket : %s" % str(e))
		time.sleep(0.3)

def heartbeat_handler(delay):
	while not globals.READY:
		time.sleep(1)
	while 1:
		for device in globals.KNOWN_DEVICES:
			noseeninterval = globals.SCAN_INTERVAL*globals.NOSEEN_NUMBER
			action = {}
			if 'absent' in globals.KNOWN_DEVICES[device] and globals.KNOWN_DEVICES[device]['absent'] != '':
				noseeninterval = globals.SCAN_INTERVAL*int(globals.KNOWN_DEVICES[device]['absent'])
			if device in globals.SEEN_DEVICES and 'present' in globals.SEEN_DEVICES[device]:
				if globals.SEEN_DEVICES[device]['present'] == 1:
					if (globals.SEEN_DEVICES[device]['lastseen'] + noseeninterval) < int(time.time()):
						logging.info('Not SEEEEEEEEEN------ since ' +str(noseeninterval) +'s '+ str(device))
						action['present']=0
						action['id']=device
						action['rssi'] = -200
						action['source'] = globals.daemonname
			else:
				if (globals.START_TIME + noseeninterval) < int(time.time()):
					logging.info('Not SEEEEEEEEEN------ since ' +str(noseeninterval) +'s '+ str(device))
					globals.SEEN_DEVICES[device]={'present':0}
					action['present']=0
					action['id']=device
					action['rssi'] = -200
					action['source'] = globals.daemonname
			if len(action)>2 :
				if globals.PENDING_ACTION == False and (globals.PENDING_TIME + 6) <int(time.time()):
					if 'present' in globals.SEEN_DEVICES[device]:
						globals.SEEN_DEVICES[device]['present'] = 0
					else:
						globals.SEEN_DEVICES[device]={'present':0}
					globals.JEEDOM_COM.add_changes('devices::'+device,action)
				else:
					logging.info('Not SEEEEEEEEEN------ since ' +str(noseeninterval) +'s '+ str(device) + ' but not sendig because last connection was too soon')
			if not globals.PENDING_ACTION and globals.KNOWN_DEVICES[device]['islocked'] == 0 or globals.KNOWN_DEVICES[device]['emitterallowed'] not in [globals.daemonname,'all']:
				if device in globals.KEEPED_CONNECTION:
					logging.debug("HEARTBEAT------This antenna should not keep a connection with this device, disconnecting " + str(device))
					try:
						globals.KEEPED_CONNECTION[device].disconnect()
					except Exception as e:
						logging.debug(str(e))
					if device in globals.KEEPED_CONNECTION:
						del globals.KEEPED_CONNECTION[device]
					logging.debug("HEARTBEAT------Removed from keep connection list " + str(device))
		if globals.LEARN_MODE and (globals.LEARN_BEGIN + 60)  < int(time.time()):
			globals.LEARN_MODE = False
			logging.debug('HEARTBEAT------Quitting learn mode (60s elapsed)')
			globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname});
		if globals.KNOWN_DEVICES[device]['islocked'] == 1 and globals.KNOWN_DEVICES[device]['emitterallowed'] == globals.daemonname:
			if device in list(globals.KEEPED_CONNECTION):
				if device not in globals.SEEN_DEVICES:
					globals.SEEN_DEVICES[device] = {}
				globals.SEEN_DEVICES[device]['lastseen'] = int(time.time())
				globals.SEEN_DEVICES[device]['present'] = 1
		if (globals.LAST_BEAT + 55) < int(time.time()):
			globals.JEEDOM_COM.send_change_immediate({'heartbeat' : 1,'source' : globals.daemonname,'version' : globals.DAEMON_VERSION});
			globals.LAST_BEAT = int(time.time())
		time.sleep(1)

def action_handler(message):
	manuf =''
	if manuf in message['command']:
		manuf = message['command']['manuf']
	name = message['command']['name']
	if 'localname' in globals.KNOWN_DEVICES[message['device']['id']]:
		message['device']['localname'] = globals.KNOWN_DEVICES[message['device']['id']]['localname']
	result = {}
	if message['cmd'] == 'helper' or message['cmd'] == 'helperrandom':
		type ='public'
		if message['cmd'] == 'helperrandom':
			type = 'random'
		try:
			mac = message['device']['id']
			if mac in globals.KEEPED_CONNECTION:
				logging.debug('ACTION------Already a connection for ' + mac + ' use it')
				conn = globals.KEEPED_CONNECTION[mac]
			else:
				logging.debug('ACTION------Creating a new connection for ' + mac)
				conn = Connector(mac)
				globals.KEEPED_CONNECTION[mac]=conn
				conn.connect(type=type)
			if not conn.isconnected:
				conn.connect(type=type)
				if not conn.isconnected:
					return
			try:
				conn.helper()
			except Exception as e:
				logging.debug("ACTION------Helper failed : %s" % str(e))
			conn.disconnect()
			return
		except Exception as e:
				logging.debug("ACTION------Helper failed : %s" % str(e))
	elif message['cmd'] == 'refresh':
		for compatible in globals.COMPATIBILITY:
			classname = message['command']['device']['name']
			if compatible().name.lower() == classname.lower():
				logging.debug('ACTION------Attempt to refresh values')
				try:
					result = compatible().read(message['device']['id'])
				except Exception as e:
					logging.debug("ACTION------Refresh failed : %s" % str(e))
				break
		if result and len(result) >= 2 :
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
				try:
					result = device().action(message)
				except Exception as e:
						logging.debug("ACTION------Action failed :" + str(e))
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
	time.sleep(60)
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
				if globals.KNOWN_DEVICES[device]['needsrefresh'] != 1:
					continue
				if mac in globals.LAST_TIME_READ and now < (globals.LAST_TIME_READ[mac]+datetime.timedelta(milliseconds=int(globals.KNOWN_DEVICES[device]['delay'])*1000)):
					continue
				else :
					globals.LAST_TIME_READ[mac] = now
					for compatible in globals.COMPATIBILITY:
						if compatible().name.lower() == str(globals.KNOWN_DEVICES[device]['name']).lower():
							try:
								result = compatible().read(mac)
							except Exception as e:
								try:
									result = compatible().read(mac)
								except Exception as e:
									try:
										result = compatible().read(mac)
									except Exception as e:
										logging.debug("READER------Refresh failed : %s" % str(e))
							break
					if result :
						if mac in globals.LAST_STATE and result == globals.LAST_STATE[mac]:
							continue
						else:
							globals.LAST_STATE[mac] = result
							result['source'] = globals.daemonname
							globals.JEEDOM_COM.add_changes('devices::'+mac,result)
							break
		except Exception as e:
			logging.error("READER------Exception on read device : %s" % str(e))
		time.sleep(10)

def handler(signum=None, frame=None):
	logging.debug("GLOBAL------Signal %i caught, exiting..." % int(signum))
	shutdown()

def shutdown():
	logging.debug("GLOBAL------Shutdown")
	logging.debug("GLOBAL------Removing PID file " + str(globals.pidfile))
	logging.debug("GLOBAL------Closing all potential bluetooth connection")
	for device in list(globals.KEEPED_CONNECTION):
		logging.debug("GLOBAL------This antenna should not keep a connection with this device, disconnecting " + str(device))
		try:
			globals.KEEPED_CONNECTION[device].disconnect(True)
			logging.debug("Connection closed for " + str(device))
		except Exception as e:
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
parser.add_argument("--noseeninterval", help="No seen interval", type=str)
parser.add_argument("--scaninterval", help="Scan interval", type=str)
parser.add_argument("--scanmode", help="Scan mode", type=str)
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
if args.noseeninterval:
	globals.NOSEEN_NUMBER = int(args.noseeninterval)
if args.scaninterval:
	globals.SCAN_INTERVAL = int(args.scaninterval)
if args.scanmode:
	globals.SCAN_MODE = args.scanmode

globals.socketport = int(globals.socketport)
globals.cycle = float(globals.cycle)

if globals.device == '':
	globals.device = 'hci0'

jeedom_utils.set_log_level(globals.log_level)
logging.info('GLOBAL------Start blead')
logging.info('GLOBAL------Log level : '+str(globals.log_level))
logging.info('GLOBAL------Socket port : '+str(globals.socketport))
logging.info('GLOBAL------Socket host : '+str(globals.sockethost))
logging.info('GLOBAL------Device : '+str(globals.device))
logging.info('GLOBAL------PID file : '+str(globals.pidfile))
logging.info('GLOBAL------Apikey : '+str(globals.apikey))
logging.info('GLOBAL------Callback : '+str(globals.callback))
logging.info('GLOBAL------Cycle : '+str(globals.cycle))
logging.info('GLOBAL------Scan interval  : '+str(globals.SCAN_INTERVAL))
logging.info('GLOBAL------Number for no seen : '+str(globals.NOSEEN_NUMBER))
logging.info('GLOBAL------Scan Mode : '+str(globals.SCAN_MODE))
import devices
signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)
os.system('sudo rfkill unblock all >/dev/null 2>&1')
os.system('sudo hciconfig ' + globals.device + ' up')
globals.IFACE_DEVICE = int(globals.device[-1:])
try:
	jeedom_utils.write_pid(str(globals.pidfile))
	globals.JEEDOM_COM = jeedom_com(apikey = globals.apikey,url = globals.callback,cycle=globals.cycle)
	if not globals.JEEDOM_COM.test():
		logging.error('GLOBAL------Network communication issues. Please fix your Jeedom network configuration.')
		shutdown()
	jeedom_socket = jeedom_socket(port=globals.socketport,address=globals.sockethost)
	listen()
except Exception as e:
	logging.error('GLOBAL------Fatal error : '+str(e))
	logging.debug(traceback.format_exc())
	shutdown()
