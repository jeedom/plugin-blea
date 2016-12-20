import logging
import globals
import re
import struct

def tuple_to_hex(value):
	result=''
	logging.debug('Converting to hex ' + str(value))
	for x in value:
		iterresult = "%x" % x
		result = result + iterresult.zfill(2)
	logging.debug('Result is ' + str(result))
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
	