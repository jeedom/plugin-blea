from bluepy import btle
import time
import logging
import globals
import thread
import struct

class Notification():
	def __init__(self,conn,classname):
		self.name = 'notification'
		self.conn = conn
		self.classname = classname

	def subscribe(self,timer=0):
		try:
			logging.debug('Subscribing to notification : '+str(self.conn.mac))
			delegate = NotificationDelegate(self.conn,self.classname)
			self.conn.conn.setDelegate(delegate)
			logging.debug('Delegated')
			thread.start_new_thread( self.waiter, (timer,))
		except Exception,e:
			logging.debug(str(e))
			
	def waiter(self,timer=0):
		try:
			if timer!=0:
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
			self.conn.disconnect()
			logging.debug(str(e))

class NotificationDelegate(btle.DefaultDelegate):
	def __init__(self,conn,classname):
		btle.DefaultDelegate.__init__(self)
		self.conn = conn
		self.classname = classname

	def handleNotification(self, cHandle, data):
		logging.debug('Received Notification for ' + (self.conn.mac) + ' ' + self.classname().name +' from handle ' +hex(cHandle) )
		self.classname().handlenotification(self.conn,cHandle,data)