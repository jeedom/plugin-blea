from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals

class Tile():
	def __init__(self):
		self.name = 'tile'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if name.lower() == self.name:
			return True
			
	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		return action

globals.COMPATIBILITY.append(Tile)
