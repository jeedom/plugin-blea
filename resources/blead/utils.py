import logging
import globals
import re
import struct
import math
from bluepy import btle
from multiconnect import Connector

def tuple_to_hex(value):
	result=''
	logging.debug('UTILS------Converting to hex ' + str(value))
	for x in value:
		iterresult = "%x" % x
		result = result + iterresult.zfill(2)
	logging.debug('UTILS------Result is ' + str(result))
	return result
	
def twoDigitHex(number):
	return '%02x' % number

def getTintedColor(color,lum):
	initColor = color
	color = color.replace('#','')
	lum = float(lum)/100
	if lum == 1:
		return initColor
	logging.debug(str(color) + ' ' + str(lum))
	rgb = "";
	for i in range(0,4):
		c = int(color[i*2:i*2+2], 16)
		c = int(min(max(0,(c * lum)), 255))
		rgb = rgb + hex(c)[2:].zfill(2)
	return rgb
	
def getConnection(mac,type='public'):
	isold=False
	try:
		if mac in globals.KEEPED_CONNECTION:
			logging.debug('UTILS------Already a connection for ' + mac + ' use it')
			conn = globals.KEEPED_CONNECTION[mac]
			isold=True
		else:
			logging.debug('UTILS------Creating a new connection for ' + mac)
			conn = Connector(mac)
			globals.KEEPED_CONNECTION[mac]=conn
			conn.connect(type=type)
			if not conn.isconnected:
				conn.connect(type=type)
				if not conn.isconnected:
					return False,False
		return conn,isold
	except Exception,e:
		logging.error(str(e))
		if mac in globals.KEEPED_CONNECTION:
			del globals.KEEPED_CONNECTION[mac]
		return False,False
		
def get_handle_from_uuid(service_uuid, char_uuid, conn):
	conn.getServices()
	svc = conn.getServiceByUUID( service_uuid )
	ch = svc.getCharacteristics(char_uuid)[0]
	return str(ch.getHandle())

def twos_complement(value, bits):
	if (value & (1 << (bits - 1))) != 0:
		value = value - (1 << bits)
	return value