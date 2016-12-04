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
		measured = int((data[8:10] + data[6:8]), 16) * 0.01 / 2
		action['value'] = measured
		return action

globals.COMPATIBILITY.append(XiaomiScale)
