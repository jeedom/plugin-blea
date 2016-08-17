from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals

class Fitbit():
	def __init__(self):
		self.name = 'fitbit'

	def isvalid(self,name):
		if name.lower() == self.name:
			return True
		if name.lower() == 'charger hr':
			return True
			
	def parse(self,data):
		return {}

globals.COMPATIBILITY.append(Fitbit)