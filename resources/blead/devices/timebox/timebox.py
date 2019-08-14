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
import logging

"""
    Color name : http://pillow.readthedocs.io/en/3.1.x/reference/ImageColor.html#module-PIL.ImageColor
        Hexadecimal color specifiers, given as #rgb or #rrggbb. For example, #ff0000 specifies pure red.
        Common HTML color names
        4 LSB bits are dropped for each color channel
"""
os.path.join(os.path.dirname(__file__),'fonts/Electronic scale.ttf')
class TimeBox:
    """Class TimeBox encapsulates the TimeBox communication."""

    COMMANDS = {
        "switch radio": 0x05,
        "set volume": 0x08,
        "get volume": 0x09,
        "set mute": 0x0a,
        "get mute": 0x0b,
        "set date time": 0x18,
        "set image": 0x44,
        "set view": 0x45,
        "set animation frame": 0x49,
        "get temperature": 0x59,
        "get radio frequency": 0x60,
        "set radio frequency": 0x61
    }

    socket = None
    messages = None
    message_buf = []

    def __init__(self):
        self.messages = TimeBoxMessages()
        self.isconnected = False
        self.mac = ''

    def show_text(self, txt, speed=10, font=None):
        """
          Display text & scroll, call is blocking
        """
        if (type(txt) is not list) or (len(txt)==0) or (type(txt[0]) is not tuple):
            raise Exception("a list of tuple is expected")
        im = draw_multiple_to_image(txt, font)
        slices = horizontal_slices(im)
        for i, s in enumerate(slices):
            globals.CURRENT_DIVOOM_SCROLL[self.mac] = True
            #s.save("./debug/%s.bmp"%i)
            self.set_static_image(build_img(s))
            if (globals.CURRENT_DIVOOM_TEXT[self.mac]) == True:
                time.sleep(1.0/speed)
            else:
                globals.CURRENT_DIVOOM_SCROLL[self.mac] = False
                break

    def show_text2(self, txt, font=None):
        """
        Use dynamic_image_message to display scolling text
        Cannot go faster than 1fps
        """
        if (type(txt) is not list) or (len(txt)==0) or (type(txt[0]) is not tuple):
            raise Exception("a list of tuple is expected")
        imgs = []
        im = divoom_image.draw_multiple_to_image(txt, font)
        slices = horizontal_slices(im)
        for i, s in enumerate(slices):
            # s.save("./debug/%s.bmp"%i)
            imgs.append(build_img(s))
        self.set_dynamic_images(imgs)

    def show_static_image(self, path):
      logging.debug('DIVOOM------Show static image')
      self.set_static_image(divoom_image.load_image(path))

    def show_animated_image(self, path):
      logging.debug('DIVOOM------Show animated image')
      self.set_dynamic_images(divoom_image.load_gif_frames(path))

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

    def receive(self, num_bytes=1024):
        """Receive n bytes of data from the TimeBox and put it in the input buffer."""
        ready = select.select([self.socket], [], [], 0.1)
        if ready[0]:
            self.message_buf += self.socket.recv(num_bytes)

    def send_raw(self, data):
        """Send raw data to the TimeBox."""
        return self.socket.send(data)

    def send_payload(self, payload):
        """Send raw payload to the TimeBox. (Will be escaped, checksumed and
        messaged between 0x01 and 0x02."""
        logging.debug('DIVOOM------Send payload')
        msg = self.messages.make_message(payload)
        logging.debug('MEEEEEEEEEEESSSSAAAAGE    ' + str(bytes(bytearray(msg)).hex()))
        return self.socket.send(bytes(bytearray(msg)))

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

    def decode(self, msg):
        """remove leading 1, trailing 2 and checksum and un-escape"""
        return self.messages.decode(msg)

    def has_message(self):
        """Check if there is a complete message *or leading garbage data* in the input buffer."""
        if len(self.message_buf) == 0:
            return False
        if self.message_buf[0] != 0x01:
            return True
        endmarks = [x for x in self.message_buf if x == 0x02]
        return  len(endmarks) > 0

    def buffer_starts_with_garbage(self):
        """Check if the input buffer starts with data other than a message."""
        if len(self.message_buf) == 0:
            return False
        return self.message_buf[0] != 0x01

    def remove_garbage(self):
        """Remove data from the input buffer that is nof the start of a message."""
        if not 0x01 in self.message_buf:
            pos = len(self.message_buf)
        else:
            pos = self.message_buf.index(0x01)
        res = self.message_buf[0:pos]
        self.message_buf = self.message_buf[pos:len(self.message_buf)]
        return res

    def remove_message(self):
        """Remove a message from the input buffer and return it. Assumes it has been checked that
        there is a complete message without leading garbage data"""
        if not 0x02 in self.message_buf:
            raise Exception('There is no message')
        pos = self.message_buf.index(0x02)+1
        res = self.message_buf[0:pos]
        self.message_buf = self.message_buf[pos:len(self.message_buf)]
        return res

    def set_static_image(self, image):
        """Set the image on the TimeBox"""
        msg = self.messages.static_image_message(image)
        logging.debug('MEEEEEEEEEEESSSSAAAAGE    ' + str(bytes(bytearray(msg)).hex()))
        self.socket.send(bytes(bytearray(msg)))

    def set_dynamic_images(self, images, frame_delay=1):
        """Set the image on the TimeBox"""
        fnum = 0
        for img in images:
            msg = self.messages.dynamic_image_message(img, fnum, frame_delay)
            fnum = fnum + 1
            logging.debug('MEEEEEEEEEEESSSSAAAAGE    ' + str(bytes(bytearray(msg)).hex()))
            self.socket.send(bytes(bytearray(msg)))

    def show_temperature(self, color=None):
        """Show temperature on the TimeBox in Celsius"""
        args = [0x01, 0x00]
        if color:
            color = ImageColor.getrgb(color)
            args += list(color)
        self.send_command("set view", args)

    def show_clock(self, color=None):
        """Show clock on the TimeBox in the color"""
        args = [0x00, 0x01]
        if color:
            color = ImageColor.getrgb(color)
            args += list(color)
        self.send_command("set view", args)
