# coding: utf-8
from bluepy import btle
import time
import logging
import globals

class Miband4():
	def __init__(self):
		self.name = 'miband4'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if name.lower() in ['mi smart band 4',self.name]:
			return True
			
	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		return action

globals.COMPATIBILITY.append(Miband4)
