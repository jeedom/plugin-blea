from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals

class Fitbit():
	def __init__(self):
		self.name = 'fitbit'

	def isvalid(self,name,manuf=''):
		if name.lower() == self.name:
			return True
		if name.lower() == 'charge hr':
			return True
			
	def parse(self,data,mac,name):
		action={}
		action['present'] = 1
		return action

globals.COMPATIBILITY.append(Fitbit)