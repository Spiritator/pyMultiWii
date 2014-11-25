#!/usr/bin/env python

"""MSP.py: Handles Multiwii Serial Protocol."""

__author__ = "Aldo Vargas"
__copyright__ = "Copyright 2014 Aldux.net"

__license__ = "GPL"
__version__ = "1"
__maintainer__ = "Aldo Vargas"
__email__ = "alduxvm@gmail.com"
__status__ = "Development"


import serial, struct
from time import sleep

import cfg


"""Multiwii Serial Protocol message ID"""
IDENT = 100
STATUS = 101
RAW_IMU = 102
SERVO = 103
MOTOR = 104
RC = 105
RAW_GPS = 106
COMP_GPS = 107
ATTITUDE = 108
ALTITUDE = 109
ANALOG = 110
RC_TUNING = 111
PID = 112
BOX = 113
MISC = 114
MOTOR_PINS = 115
BOXNAMES = 116
PIDNAMES = 117
WP = 118
BOXIDS = 119
RC_RAW_IMU = 121
SET_RAW_RC = 200
SET_RAW_GPS = 201
SET_PID = 202
SET_BOX = 203
SET_RC_TUNING = 204
ACC_CALIBRATION = 205
MAG_CALIBRATION = 206
SET_MISC = 207
RESET_CONF = 208
SET_WP = 209
SWITCH_RC_SERIAL = 210
IS_SERIAL = 211
DEBUG = 254

"""Serial port configuration"""
ser = serial.Serial()
ser.port = cfg.port
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.timeout = 0
ser.xonxoff = False
ser.rtscts = False
ser.dsrdtr = False
ser.writeTimeout = 2
wakeup = 12

"""Global variables of data"""
rcChannels = {'roll':0,'pitch':0,'yaw':0,'throttle':0}
rawIMU = {'ax':0,'ay':0,'az':0,'gx':0,'gy':0,'gz':0}
attitude = {'angx':0,'angy':0,'heading':0}
temp = ();

"""Use a pythonic way to evaluate and process command received"""
def readRaw():
    i=0
    try:
        for value in rawIMU:
            rawIMU[value]=temp[i]
            i+=1
    except IndexError:
        pass

def readRC():
    i=0
    try:
        for value in rcChannels:
            rcChannels[value]=temp[i]
            i+=1
    except IndexError:
        pass

def readAttitude():
    i=0
    try:
        attitude['angx']=float(temp[0]/10.0)
        attitude['angy']=float(temp[1]/10.0)
        attitude['heading']=float(temp[2])
    except IndexError:
        pass

def readRCRaw():
    i=0
    try:
        for value in attitude:
            attitude[value]=temp[i]
            i+=1
    except IndexError:
        pass

evaluateCommand = {
    102 : readRaw,
    105 : readRC,
    108 : readAttitude,
    121 : readRCRaw 
}


"""Function to open the serial port"""
def startMulticopter():
    try:
        ser.open()
        if cfg.PRINT:
            print "Waking up multicopter..."
        for i in range(1,wakeup):
            if cfg.PRINT:
                print wakeup-i
                sleep(1)
            else:
                sleep(1)
    except Exception, error:
        print "\n\nError opening "+ser.port+" port.\n\n"
        quit()

"""Function to send a command with or without parameters to the Multiwii"""
def sendCMD(data_length, code, data):
    checksum = 0
    total_data = ['$', 'M', '<', data_length, code] + data
    for i in struct.pack('<2B%dh' % len(data), *total_data[3:len(total_data)]):
        checksum = checksum ^ ord(i)
    total_data.append(checksum)
    try:
        b = None
        b = ser.write(struct.pack('<3c2B%dhB' % len(data), *total_data))
    except Exception, error:
        print "\n\nError is sendCMD."
        print "("+str(error)+")\n\n"
        ser.close()
        quit()
    return b

def readData():
    global rcChannels,rawIMU,attitude,temp
    try:
        while True:
            header = ser.read(3)
            if header == '$M>':
                break
        datalength = struct.unpack('<b', ser.read())[0]
        code = struct.unpack('<b', ser.read())
        data = ser.read(datalength)
        temp = struct.unpack('<'+'h'*(datalength/2),data)
        evaluateCommand[code[0]]()
        #temp = struct.unpack('h'*(datalength/2),data)
        #i=0
        #for value in attitude:
        #    attitude[value]=temp[i]
        #    i+=1
    except Exception, error:
        print "\n\nError in readData."
        print "("+str(error)+")\n\n"
        ser.close()
        quit()





