# -*- coding: latin-1 -*-
"""Provides class TimeBox that encapsulates the TimeBox communication."""

import select
from bluetooth import BluetoothSocket, RFCOMM
from . messages import TimeBoxMessages
from . import divoom_image
import datetime
from . divoom_image import build_img, draw_multiple_to_image, horizontal_slices
import time
import os
import globals
from PIL import ImageColor
import PIL
import logging

class TimeBox:

    def __init__(self):
        self.messages = TimeBoxMessages()
        self.isconnected = False
        self.mac = ''
        self.socket = ''

    def show_text(self, txt, speed=10, font=None):
        """
          Display text & scroll, call is blocking
        """
        if (type(txt) is not list) or (len(txt)==0) or (type(txt[0]) is not tuple):
            raise Exception("a list of tuple is expected")
        im = draw_multiple_to_image(txt, font)
        slices = horizontal_slices(im)
        speed = 20-speed
        speed = int(50 + round(speed*10))
        logging.debug('CALLLLLLCULAAAAATED SPEED ' +str(speed))
        slices[0].save('/tmp/pixoo_text_temp.gif', format='GIF', append_images=slices[1:], save_all=True, duration=speed, loop=0)
        f = PIL.Image.open('/tmp/pixoo_text_temp.gif')
        f.info['duration'] = speed
        f.save('/tmp/pixoo_text.gif', save_all=True)
        self.show_animated_image('/tmp/pixoo_text.gif')
        self.show_animated_image('/tmp/pixoo_text.gif')

    def show_static_image(self, path):
      logging.debug('DIVOOM------Show static image')
      self.send_raw('44000A0A04AA2D00000000'+divoom_image.load_image(path))

    def show_animated_image(self, path):
      logging.debug('DIVOOM------Show animated image')
      messages = divoom_image.build_animation(path)
      logging.debug(str(messages))
      self.show_static_image(os.path.join(os.path.dirname(__file__),'images/noir.png'))
      for message in messages:
          self.send_raw(message)

    def connect(self, host=None, port=4):
        """Open a connection to the TimeBox."""
        # Create the client socket
        for i in range(5):
            try:
                globals.PENDING_ACTION = True
                globals.PENDING_TIME = int(time.time())
                time.sleep(3)
                self.socket = BluetoothSocket(RFCOMM)
                self.socket.connect((host, port))
                self.socket.setblocking(0)
                self.isconnected = True
                self.mac = host
            except Exception as e:
                logging.error("Got exception while attempting to connect to timebox : %s"%e)
                time.sleep(2)
            break
        globals.PENDING_ACTION = False
        globals.PENDING_TIME = int(time.time())

    def close(self):
        """Closes the connection to the TimeBox."""
        self.socket.close()
        self.isconnected = False
        if self.mac in globals.KEEPED_CONNECTION:
            del globals.KEEPED_CONNECTION[self.mac]

    def set_time(self, time=None):
      if not time:
        time=datetime.datetime.now()
      args = []
      args.append(int(str(time.year)[2:]))
      args.append(int(str(time.year)[0:2]))
      args.append(int(time.month))
      args.append(int(time.day))
      args.append(int(time.hour))
      args.append(int(time.minute))
      args.append(int(time.second))
      args.append(0)
      self.send_command("set date time", args)

    def send_command(self, command, args=None):
        """Send command with optional arguments"""
        logging.debug('DIVOOM------Send command')
        if args is None:
            args = []
        if isinstance(command, str):
            command = self.COMMANDS[command]
        length = len(args)+3
        length_lsb = length & 0xff
        length_msb = length >> 8
        payload = [length_lsb, length_msb, command] + args
        self.send_payload(payload)

    def set_static_image(self, image):
        """Set the image on the TimeBox"""
        msg = self.messages.static_image_message(image)
        self.socket.send(bytes(bytearray(msg)))

    def set_dynamic_images(self, images, frame_delay=1):
        """Set the image on the TimeBox"""
        fnum = 0
        for img in images:
            msg = self.messages.dynamic_image_message(img, fnum, frame_delay)
            fnum = fnum + 1
            self.socket.send(bytes(bytearray(msg)))

    def set_luminosity(self, slider=None):
        """Set Luminoity on Pixoo"""
        if slider == None:
            slider = '100'
        slider  = hex(int(slider))[2:].zfill(2)
        self.send_raw('74'+slider)

    def set_temperature(self, temperature=None, icon=None):
        """Set Temperature and weather image on Pixoo"""
        if temperature == None:
            temperature = '25'
        temperature  = hex(int(temperature))[2:].zfill(2)
        if icon == None:
            icon = '1'
        icon  = hex(int(icon))[2:].zfill(2)
        self.send_raw('5F'+temperature+icon)

    def set_visual(self, type=None, visual=None):
        """Set type and visual effect on Pixoo"""
        if type == None:
            type = '3'
        type  = hex(int(type))[2:].zfill(2)
        if visual == None:
            visual = '1'
        visual  = hex(int(visual))[2:].zfill(2)
        self.send_raw('45'+type+visual)

    def set_notifs(self,icon=None):
        """Set notifs on Pixoo"""
        if icon == None:
            icon = '1'
        icon  = hex(int(icon))[2:].zfill(2)
        self.send_raw('50'+icon)

    def set_clock(self,mode=0,clock=0,weather=0,temp=0,date=0,color=None):
        """Set clock and modes on Pixoo"""
        mode  = hex(int(mode))[2:].zfill(2)
        clock  = hex(int(clock))[2:].zfill(2)
        weather  = hex(int(weather))[2:].zfill(2)
        temp  = hex(int(temp))[2:].zfill(2)
        date  = hex(int(date))[2:].zfill(2)
        if color == None:
            color = '#0000FF'
        color = color[1:]
        self.send_raw('450000'+mode+clock+weather+temp+date+color)

    def send_raw(self, data):
        """Send raw data to the TimeBox."""
        logging.debug('DIVOOM------Send raw command ' + str(data))
        args = [int(x) for x in bytearray.fromhex(data)]
        logging.debug('DIVOOM------ ' +str(args))
        length = len(args)+2
        length_lsb = length & 0xff
        length_msb = length >> 8
        payload = [length_lsb, length_msb] + args
        self.send_payload(payload)

    def send_payload(self, payload):
        """Send raw payload to the TimeBox. (Will be escaped, checksumed and
        messaged between 0x01 and 0x02."""
        logging.debug('DIVOOM------Send payload')
        logging.debug(str(payload))
        msg = self.messages.make_message(payload)
        logging.debug(str(msg))
        logging.debug('MEEEEEEEEEEESSSSAAAAGE    ' + str(bytes(bytearray(msg)).hex()))
        return self.socket.send(bytes(bytearray(msg)))
