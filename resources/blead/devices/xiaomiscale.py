from bluepy.btle import Scanner, DefaultDelegate, Peripheral
import time
import logging
import globals
import struct

class XiaomiScale():
	def __init__(self):
		self.name = 'xiaomiscale'

	def isvalid(self,name,manuf=''):
		if name == 'MI_SCALE':
			return True
			
	def parse(self,data):
		action={}
		action['present'] = 1
		measunit = data[22:24]
		measured = int((data[26:28] + data[24:26]), 16) * 0.01
		unit = ''
		if measunit.startswith(('03', 'b3')): unit = 'lbs'
		if measunit.startswith(('12', 'b2')): unit = 'jin'
		if measunit.startswith(('22', 'a2')): unit = 'Kg' ; measured = measured / 2
		action['unit'] = unit
		action['value'] = measured
		return action

globals.COMPATIBILITY.append(XiaomiScale)
