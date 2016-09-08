from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals

class Playbulb():
	def __init__(self):
		self.name = 'playbulb'

	def isvalid(self,name,manuf=''):
		if manuf == '4d49504f57':
			return True
			
	def parse(self,data):
		action={}
		action['present'] = 1
		return action

globals.COMPATIBILITY.append(Playbulb)