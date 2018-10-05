from bluepy import btle
import time
import logging
import globals
from multiconnect import Connector
from notification import Notification

class Noke():
	def __init__(self):
		self.name = 'noke'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data=''):
		if 'noke' in name.lower():
			return True
			
	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		return action

globals.COMPATIBILITY.append(Noke)
