import time
import logging
import globals
from multiconnect import Connector
from devices.timebox import timebox
import utils
import logging
import PIL
from PIL import ImageFont
import os
import base64
from io import BytesIO,StringIO
import numpy as np

class DivoomTimeboxMini():
	def __init__(self):
		self.name = 'divoomtimeboxmini'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if self.name in name.lower() or name.lower() in ['timebox-mini-light']:
			return True

	def parse(self,data,mac,name,manuf):
		action={}
		action['present'] = 1
		return action

	def action(self,message):
		mac = message['device']['id']
		if mac not in globals.LAST_STORAGE:
			globals.LAST_STORAGE[mac]={}
		if mac in globals.KEEPED_CONNECTION:
			logging.debug('DIVOOM------Already a connection for ' + mac + ' use it')
			conn = globals.KEEPED_CONNECTION[mac]
		else:
			logging.debug('DIVOOM------Creating a new connection for ' + mac)
			conn = timebox.TimeBox()
			globals.KEEPED_CONNECTION[mac]=conn
			try:
				conn.close()
			except Exception as e:
				pass
			conn.connect(mac)
		if not conn.isconnected:
			conn.connect(mac)
			if not conn.isconnected:
				return
		try:
			result = conn.socket.getpeername()
		except:
			conn.isconnected = False
			if not conn.isconnected:
				conn.connect(mac)
				if not conn.isconnected:
					return
		try:
			globals.CURRENT_DIVOOM_TEXT[mac] = False
			timeout = time.time() + 3
			if mac in globals.CURRENT_DIVOOM_SCROLL:
				while globals.CURRENT_DIVOOM_SCROLL[mac]==True:
					if time.time()>timeout:
						break
					time.sleep(0.1)
			if message['command']['type']=="show_clock":
				conn.show_clock(message['command']['color'])
			elif message['command']['type']=="show_temp":
				conn.show_temperature(message['command']['color'])
			elif message['command']['type']=='display':
				if 'path' in message['command']:
					path = os.path.normpath(message['command']['path'])
					if not path.split(".")[-1].lower() in ['png', 'bmp']:
						raise Exception("Unsupported file extension")
					if not os.path.exists(path):
						raise Exception("path %s does not exists"%path)
					conn.show_static_image(path)
					if 'blink' in message['command'] and int(message['command']['blink']) == 1:
						logging.debug('Blinking detected')
						globals.CURRENT_DIVOOM_SCROLL[mac] = True
						globals.CURRENT_DIVOOM_TEXT[mac] = True
						while globals.CURRENT_DIVOOM_TEXT[mac] == True:
							time.sleep(0.5)
							conn.show_static_image(os.path.join(os.path.dirname(__file__),'timebox/images/black.bmp'))
							time.sleep(0.5)
							conn.show_static_image(path)
						globals.CURRENT_DIVOOM_SCROLL[mac] = False
				elif 'data' in message['command']:
					total_pixel=0
					colorArray =[]
					line =[]
					for pixel, value in message['command']['data'].items():
						if total_pixel == 11:
							line =[]
							total_pixel =0
						total_pixel += 1
						line.append(value)
						if total_pixel == 11:
							colorArray.append(line)
					img =PIL.Image.fromarray(np.array(colorArray).astype(np.uint8))
					img.save('/tmp/out.png', format="PNG")
					conn.show_static_image('/tmp/out.png')
					if 'blink' in message['command'] and int(message['command']['blink']) == 1:
						logging.debug('Blinking detected')
						globals.CURRENT_DIVOOM_SCROLL[mac] = True
						globals.CURRENT_DIVOOM_TEXT[mac] = True
						while globals.CURRENT_DIVOOM_TEXT[mac] == True:
							time.sleep(0.5)
							conn.show_static_image(os.path.join(os.path.dirname(__file__),'timebox/images/black.bmp'))
							time.sleep(0.5)
							conn.show_static_image('/tmp/out.png')
						globals.CURRENT_DIVOOM_SCROLL[mac] = False
			elif message['command']['type']=='displaydynamic':
				if 'path' in message['command']:
					path = os.path.normpath(message['command']['path'])
					if not path.split(".")[-1].lower() in ['gif']:
						raise Exception("Unsupported file extension")
					if not os.path.exists(path):
						raise Exception("path %s does not exists"%path)
					conn.show_animated_image(path)
				elif 'data' in message['command']:
					total_pixel=0
					colorArray =[]
					line =[]
					for pixel, value in message['command']['data'].items():
						if total_pixel == 11:
							line =[]
							total_pixel =0
						total_pixel += 1
						line.append(value)
						if total_pixel == 11:
							colorArray.append(line)
					img =PIL.Image.fromarray(np.array(colorArray).astype(np.uint8))
					img.save('/tmp/out.png', format="PNG")
					conn.show_animated_image('/tmp/out.png')
			elif message['command']['type']=="connect":
				conn.connect(mac)
			elif message['command']['type']=="disconnect":
				conn.close()
			elif message['command']['type']=='show_text':
				text = []
				for txt in message['command']['text']:
					text.append((txt, message['command']['text'][txt]))
				font = ImageFont.load(os.path.join(os.path.dirname(__file__),'timebox/fonts/slkscr.pil'))
				globals.CURRENT_DIVOOM_TEXT[mac] = True
				while globals.CURRENT_DIVOOM_TEXT[mac] == True:
					conn.show_text(text,speed =int(message['command']['speed']), font=font)
			elif message['command']['type']=='show_text_test':
				text = []
				text.append(('TEST', '#ff0000'))
				text.append(('TEST', '#00ff00'))
				text.append(('TEST', '#0000ff'))
				font = ImageFont.load(os.path.join(os.path.dirname(__file__),'timebox/fonts/slkscr.pil'))
				conn.show_text(text, font=font)
		except Exception as e:
			logging.debug("DIVOOM------Failed to finish : %s" % str(e))
		#conn.disconnect()
		return

	def hex_to_rgb(self,value):
		value = value.lstrip('#')
		lv = len(value)
		return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

	def rgb_to_hex(self,rgb):
		return '#%02x%02x%02x' % rgb

globals.COMPATIBILITY.append(DivoomTimeboxMini)
