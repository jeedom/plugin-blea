# coding: utf-8
from bluepy import btle
import time
import logging
import globals

class AmazfitGtr():
	def __init__(self):
		self.name = 'amazfitgtr'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if name.lower() in ['amazfit gtr',self.name]:
			return True

	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		return action

globals.COMPATIBILITY.append(AmazfitGtr)
