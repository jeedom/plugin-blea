import time
import logging
import globals
from multiconnect import Connector
from devices.pixoo import timebox
import utils
import logging
import PIL
import os
import base64
from io import BytesIO,StringIO
import numpy as np

class DivoomPixoo():
	def __init__(self):
		self.name = 'divoompixoo'
		self.ignoreRepeat = False

	def isvalid(self,name,manuf='',data='',mac=''):
		if self.name in name.lower() or name.lower() in ['pixoo']:
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
			logging.debug('PIXOO------Already a connection for ' + mac + ' use it')
			conn = globals.KEEPED_CONNECTION[mac]
		else:
			logging.debug('PIXOO------Creating a new connection for ' + mac)
			conn = timebox.TimeBox()
			globals.KEEPED_CONNECTION[mac]=conn
			try:
				conn.close()
			except Exception as e:
				pass
			conn.connect(mac,1)
		if not conn.isconnected:
			conn.connect(mac,1)
			if not conn.isconnected:
				if mac in globals.KEEPED_CONNECTION:
					del globals.KEEPED_CONNECTION[mac]
				return
		try:
			result = conn.socket.getpeername()
		except:
			conn.isconnected = False
			if not conn.isconnected:
				conn.connect(mac,1)
				if not conn.isconnected:
					if mac in globals.KEEPED_CONNECTION:
						del globals.KEEPED_CONNECTION[mac]
					return
		try:
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
				elif 'data' in message['command']:
					total_pixel=0
					colorArray =[]
					line =[]
					for pixel, value in message['command']['data'].items():
						if total_pixel == 16:
							line =[]
							total_pixel =0
						total_pixel += 1
						line.append(value)
						if total_pixel == 16:
							colorArray.append(line)
					img =PIL.Image.fromarray(np.array(colorArray).astype(np.uint8))
					img.save('/tmp/outpixoo.png', format="PNG")
					path = '/tmp/outpixoo.png'
				if 'blink' in message['command'] and int(message['command']['blink']) == 1:
					images = []
					images.append(PIL.Image.open(path))
					images.append(PIL.Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'pixoo/images/black.bmp')).resize((16, 16)))
					images[0].save('/tmp/pixoo_blink.gif', format='GIF', append_images=images[1:], save_all=True, duration=500, loop=0)
					conn.show_animated_image('/tmp/pixoo_blink.gif')
				else:
					conn.show_static_image(path)
			elif message['command']['type']=='displaydynamic':
				if 'path' in message['command']:
					path = os.path.normpath(message['command']['path'])
					if not path.split(".")[-1].lower() in ['gif']:
						raise Exception("Unsupported file extension")
					if not os.path.exists(path):
						raise Exception("path %s does not exists"%path)
					conn.show_animated_image(path)
			elif message['command']['type']=="connect":
				conn.connect(mac)
			elif message['command']['type']=="disconnect":
				conn.close()
			elif message['command']['type']=="raw":
				conn.send_raw(message['command']['raw'])
			elif message['command']['type']=='show_text':
				text = []
				for txt in message['command']['text']:
					text.append((txt, message['command']['text'][txt]))
				conn.show_text(text,speed =int(message['command']['speed']))
			elif message['command']['type']=='luminosity':
				conn.set_luminosity(message['command']['slider'])
			elif message['command']['type']=='temperature':
				conn.set_temperature(message['command']['temperature'],message['command']['icon'])
			elif message['command']['type']=='visual':
				conn.set_visual(message['command']['effectype'],message['command']['visual'])
			elif message['command']['type']=='notifs':
				conn.set_notifs(message['command']['icon'])
			elif message['command']['type']=='offtotal':
				conn.send_raw('4100')
			elif message['command']['type']=='blackscreen':
				conn.send_raw('4501000000640000')
			elif message['command']['type']=='clock':
				mode = '0'
				clock = '0'
				weather = '0'
				temp = '0'
				date = '0'
				color = None
				if 'mode' in message['command']:
					mode = message['command']['mode']
				if 'clock' in message['command']:
					clock = message['command']['clock']
				if 'weather' in message['command']:
					weather = message['command']['weather']
				if 'temp' in message['command']:
					temp = message['command']['temp']
				if 'date' in message['command']:
					date = message['command']['date']
				if 'color' in message['command']:
					color = message['command']['color']
				conn.set_clock(mode,clock,weather,temp,date,color)
		except Exception as e:
			logging.debug("PIXOO------Failed to finish : %s" % str(e))
			if mac in globals.KEEPED_CONNECTION:
				del globals.KEEPED_CONNECTION[mac]
		#conn.disconnect()
		return

	def hex_to_rgb(self,value):
		value = value.lstrip('#')
		lv = len(value)
		return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

	def rgb_to_hex(self,rgb):
		return '#%02x%02x%02x' % rgb

globals.COMPATIBILITY.append(DivoomPixoo)
