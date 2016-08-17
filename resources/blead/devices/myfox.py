from bluepy.btle import Scanner, DefaultDelegate
import time
import logging
import globals

class Myfox():
	def __init__(self):
		self.name = 'myfox'

	def isvalid(self,name):
		if name.lower() == self.name:
			return True
		if name.lower().find("myfox") != -1:
			return True
			
	def parse(self,data):
		return {}

globals.COMPATIBILITY.append(Myfox)