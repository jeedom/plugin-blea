from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals

class Wistiki():
	def __init__(self):
		self.name = 'wistiki'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data=''):
		if name.lower() == self.name:
			return True
			
	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		return action

globals.COMPATIBILITY.append(Wistiki)