from bluepy import btle
import time
import logging
import globals
import struct
<<<<<<< HEAD
import datetime
from multiconnect import Connector
from notification import Notification
import binascii

        
=======
from multiconnect import Connector
from notification import Notification
>>>>>>> 8581cb04e3734102b8f2335f57aee295867b14a0
class BeeWiSmartDoor():
    def __init__(self):
        self.name = 'beewi smart door'
        self.ignoreRepeat = False

    def isvalid(self,name,manuf='',data=''):
        if name.lower() == self.name:
            return True
            
    def parse(self,data,mac,name,manuf):
        action={}
        action['present'] = 1       
        logging.debug('PARSE: manuf[4:9]= ' + manuf[4:9] )
        if manuf[4:8] == '080c':              
            status = manuf[9:10]
            if manuf[4:8] == '080c':
                status = manuf[9:10]
                if status == '1':
                    status = '0'
                elif status == '0':
                    status = '1'
            battery = manuf[12:14]
            action['status'] = status
            action['battery'] = int(battery,16)
            logging.debug('BeeWi PARSE: status = ' + status )
        else:
            logging.debug('BeeWi PARSE: wrong frame ')      
        return action
    
<<<<<<< HEAD
          
=======
>>>>>>> 8581cb04e3734102b8f2335f57aee295867b14a0
    def read(self,mac):
        result={}
        try:
            conn = Connector(mac)
            conn.connect()
            if not conn.isconnected:
                conn.connect()
                if not conn.isconnected:
                    return
<<<<<<< HEAD
                    
            #check pairing state first
            pairing = conn.readCharacteristic('0x3a') # check pairing state 
            if pairing:
                #initiate pairing sequence
                conn.writeCharacteristic('0x3a','00',response=True)   # set pairing state to 0
                conn.writeCharacteristic('0x33','0100',response=True) # tbd??
                conn.writeCharacteristic('0x32','00',response=True)   # reset history days
                firmw = str(conn.readCharacteristic('0x18'))          # get fw version 
                name = str(conn.readCharacteristic('0x28'))           # get name 
                conn.writeCharacteristic('0x42','0100',response=True) # tbd??
                curdate = datetime.datetime.today().strftime('%y%m%d%H%M%S')
                conn.writeCharacteristic('0x2b',  binascii.hexlify(curdate),response=True) #set current time ascii: aammddhhmmss
                conn.writeCharacteristic('0x41','00000000',response=True)
                conn.writeCharacteristic('0x42','0000',response=True) # tbd??
                notification = Notification(conn,BeeWiSmartDoor)
                logging.debug('BeeWi read firmw=' + str(firmw) + ' Name: ' + str(name))
                notification.subscribe(2)
            else:
                battery = ord(conn.readCharacteristic('0x25'))
                logging.debug('BeeWi read Battery=' + str(battery))           
=======
            battery = bytearray(conn.readCharacteristic('0x25'))
            notification = Notification(conn,BeeWiSmartDoor)
            conn.writeCharacteristic('0x3A','00',response=True)
            conn.writeCharacteristic('0x33','0100',response=True)
            conn.writeCharacteristic('0x32','00',response=True)
            conn.writeCharacteristic('0x42','0100',response=True)           
            conn.writeCharacteristic('0x2b','313930323034313535393033',response=True)
            conn.writeCharacteristic('0x41','00000000',response=True)
            #notification.subscribe(2)
            result['battery'] = int(battery,16)
>>>>>>> 8581cb04e3734102b8f2335f57aee295867b14a0
            result['id'] = mac
            return result
        except Exception,e:
            logging.error(str(e))
        return result
        
    def handlenotification(self,conn,handle,data,action={}):
        result={}
<<<<<<< HEAD
        logging.debug('BeeWiiSmartDoor--Handle: '+str(ord(handle)))
=======
        logging.debug('BeeWiiSmartDoor--Handle: '+str(hex(handle)))
>>>>>>> 8581cb04e3734102b8f2335f57aee295867b14a0


globals.COMPATIBILITY.append(BeeWiSmartDoor)