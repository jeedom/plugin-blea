from bluepy import btle
import time
import logging
import globals
import thread
import struct

class Notification():
	def __init__(self,conn,classname,action={}):
		self.name = 'notification'
		self.conn = conn
		self.classname = classname
		self.action = action

	def subscribe(self,timer=0,disconnect=True):
		try:
			logging.debug('Subscribing to notification : '+str(self.conn.mac))
			delegate = NotificationDelegate(self.conn,self.classname,self.action)
			self.conn.conn.withDelegate(delegate)
			logging.debug('Delegated')
			thread.start_new_thread( self.waiter, (timer,disconnect,))
		except Exception,e:
			logging.debug(str(e))
			self.conn.disconnect(True)
			
	def waiter(self,timer=0,disconnect=True):
		try:
			if timer!=0:
				logging.debug('Subscribing for ' +str(timer))
				timeout = time.time() + timer
				while time.time()<timeout:
					self.conn.conn.waitForNotifications(0.5)
					time.sleep(0.03)
				self.conn.disconnect()
			else:
				while True:
					self.conn.conn.waitForNotifications(0.5)
					time.sleep(0.03)
		except Exception,e:
			self.conn.disconnect(True)
			logging.debug(str(e))

class NotificationDelegate(btle.DefaultDelegate):
	def __init__(self,conn,classname,action={}):
		btle.DefaultDelegate.__init__(self)
		self.conn = conn
		self.classname = classname
		self.action = action

	def handleNotification(self, cHandle, data):
		logging.debug('Received Notification for ' + (self.conn.mac) + ' ' + self.classname().name +' from handle ' +hex(cHandle) )
		self.classname().handlenotification(self.conn,cHandle,data,self.action)