
# Program to automate testing for GOSNR - Yankees
# Thomas Lacasse 
# 2024-02-16

# Import library for TCP/IP handling
import socket
# Import library for GPIB/Serial/USB handling
import pyvisa
# Import library to allow for time pauses
import time
# Import library for path / \\ null character handling
from pathlib import Path
# Import library for speed of light
from scipy import constants
import numpy as np

# IQS platform contains :
#   Signal VOA:         LINS0012
#   ASE VOA:            LINS0013
#   2.5 km Spool VOA:   LINS0014 

# LTB platform contains :
#   Scrambler VOA:      LINS11
#   TLS:                LINS10
#   OSA:                LINS14

class IQS:
    def __init__(self, GPIB0):
        rm = pyvisa.ResourceManager()
        self.platform = rm.open_resource("GPIB0::"+str(GPIB0)+"::INSTR")
        print("Connexion established with: "+ self.platform.query("*IDN?"))

class MPC_201:
    def __init__(self, GPIB0):
        rm = pyvisa.ResourceManager()
        self.type = "DISC"
        self.speed = 0
        self.platform = rm.open_resource("GPIB0::"+str(GPIB0)+"::INSTR")
        print("Connexion established with: "+ self.platform.query("*IDN?"))
        self.platform.write("INP:SCR:"+self.type+":RATE "+str(self.speed))


    def setDisc(self):
        self.type = "DISC"
        self.platform.write("INP:SCR:DISC:RATE 0")

    def setTri(self):
        self.type = "TRI"
        self.platform.write("INP:SCR:TRI:RATE 0")

    def setRate(self, rate):
        self.speed = rate
        self.platform.write("INP:SCR:"+self.type+":RATE "+str(self.speed))



class LTB:
    def __init__(self, add, port):
        self.platform = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.platform.connect((str(add), port))
        self.platform.sendall("*IDN?\n".encode())
        print("Connexion established with: "+ self.platform.recv(4096).decode("utf8"))

# Class establishing VOA status and operations
# 1. Set attenuation
# 2. Open/Close shutter
class VOA:
    
    # Class initialization, acquires maximum and minimum
    # attenuation values, sets the attenuation to the minimum
    # and opens the shutter
    def __init__(self, platform_name1,  platform_obj1, lins_no): #Set iqs platform as an object to pass into every class
        print("Initializing VOA")
        self.units = "DB"
        self.lins = lins_no
        self.platform_name = platform_name1
        self.platform_obj = platform_obj1
        if self.platform_name == "IQS600":
            self.min_att = float(self.platform_obj.query("LINS001"+str(self.lins)+":INP:ATT? MIN"))
            self.max_att = float(self.platform_obj.query("LINS001"+str(self.lins)+":INP:ATT? MAX"))
            self.platform_obj.write("LINS001"+str(self.lins)+":OUTP:STAT 1")
            self.platform_obj.write("LINS001"+str(self.lins)+":INP:ATT "+str(self.min_att)+" "+self.units)
        elif self.platform_name == "LTB8":
            self.platform_obj.sendall(("LINS"+str(self.lins)+":INP:ATT? MIN\n").encode())
            self.min_att = float(self.platform_obj.recv(4096).decode("utf-8"))
            self.platform_obj.sendall(("LINS"+str(self.lins)+":INP:ATT? MAX\n").encode())
            self.max_att = float(self.platform_obj.recv(4096).decode("utf-8"))
            self.platform_obj.sendall(("LINS"+str(self.lins)+":OUTP:STAT 1\n").encode())
            self.platform_obj.sendall(("LINS"+str(self.lins)+":INP:ATT "+str(self.min_att)+" "+self.units+"\n").encode())
        self.att = self.min_att
        self.shut = "Opened"
        time.sleep(2)
        print("VOA "+str(self.lins)+" initialized successfully")
    
    # Method setting the attenuation of the VOA
    def setAtt(self,  attenuation):
        self.att = attenuation
        if self.platform_name == "IQS600":
            self.platform_obj.write("LINS001"+str(self.lins)+":INP:ATT "+str(self.att)+" "+self.units)
        elif self.platform_name == "LTB8":
            self.platform_obj.sendall(("LINS"+str(self.lins)+":INP:ATT "+str(self.att)+" "+self.units+"\n").encode())

    # Method opening the shutter
    def openShut(self):
        if self.shut == "Closed":
            if self.platform_name == "IQS600":
                self.platform_obj.write("LINS001"+str(self.lins)+":OUTP:STAT 1")
            elif self.platform_name == "LTB8":
                self.platform_obj.sendall(("LINS"+str(self.lins)+":OUTP:STAT 1\n").encode())
            self.shut = "Opened"

    # Method closing the shutter
    def closeShut(self):
        if self.shut == "Opened":
            if self.platform_name == "IQS600":
                self.platform_obj.write("LINS001"+str(self.lins)+":OUTP:STAT 0")
            elif self.platform_name == "LTB8":
                self.platform_obj.sendall(("LINS"+str(self.lins)+":OUTP:STAT 0\n").encode())
            self.shut = "Closed"

# Class establishing TLS status and operations
# 1. Get power and wl min/max
# 2. Turn on/off the source
# 3. Set power and wl
class TLS:
    # Class initialization, acquires maximum and minimum
    # power and wl values, Turns on the source at maximum power and 1550 nm
    # Everything done with source 1 out of 4 (See SOUR1 in SCPI commands)
    def __init__(self, platform_name1, platform_obj1, lins_no):
        self.lins = lins_no
        self.platform_name = platform_name1
        self.platform_obj = platform_obj1
        self.units = "DBM"
        self.wl = 1.55e-6 # in m
        if self.platform_name == "LTB8":
            self.platform_obj.sendall(("LINS"+str(self.lins)+":SOUR:POW:WAV? MIN\n").encode())
            self.min_wl = float(self.platform_obj.recv(4096).decode("utf-8").strip("\n")[1:-1])
            self.platform_obj.sendall(("LINS"+str(self.lins)+":SOUR:POW:WAV? MAX\n").encode())
            self.max_wl = float(self.platform_obj.recv(4096).decode("utf-8").strip("\n")[1:-1])
            self.platform_obj.sendall(("LINS"+str(self.lins)+":SOUR:POW? MIN\n").encode())
            self.min_pow = float(self.platform_obj.recv(4096).decode("utf-8").strip("\n")[1:-1])
            self.platform_obj.sendall(("LINS"+str(self.lins)+":SOUR:POW? MAX\n").encode())
            self.max_pow = float(self.platform_obj.recv(4096).decode("utf-8").strip("\n")[1:-1])
            self.platform_obj.sendall(("LINS"+str(self.lins)+":SOUR1:POW "+ str(self.max_pow) +" "+ self.units+"\n").encode())
            self.pow = self.max_pow
            self.platform_obj.sendall(("LINS"+str(self.lins)+":SOUR1:POW:STAT 1\n").encode())
            self.platform_obj.sendall(("LINS"+str(self.lins)+":SOUR:COUN?\n").encode())
            self.ch_count = float(self.platform_obj.recv(4096).decode("utf-8").strip("\n"))
            self.platform_obj.sendall(("LINS"+str(self.lins)+":SOUR1:POW:FREQ "+str(constants.c*10**(-14)/self.wl)+"e+14 HZ\n").encode())
            self.status = "On"
        print("TLS "+str(self.lins)+" initialized successfully")

    # Method setting the source power
    def setPower(self, p):
        if self.platform_name == "LTB8":
            self.pow = p
            self.platform_obj.sendall(("LINS"+str(self.lins)+":SOUR1:POW "+str(p)+" DBM\n").encode())

    # Method setting the source wl (m)
    def setWL(self, wl1):
        if self.platform_name == "LTB8":
            if wl1 != self.wl:
                self.wl = wl1
                self.platform_obj.sendall(("LINS"+str(self.lins)+":SOUR1:POW:FREQ "+str(constants.c*10**(-14)/self.wl)+"e+14 HZ\n").encode())
    
    # Method turning off laser emission
    def turnOff(self):
        if self.platform_name == "LTB8":
            if self.status == "On":
                self.platform_obj.sendall(("LINS"+str(self.lins)+":SOUR1:POW:STAT 0\n").encode())
                self.status = "Off"

    # Method turning on laser emission
    def turnOn(self):
        if self.platform_name == "LTB8":
            if self.status == "Off":
                self.platform_obj.sendall(("LINS"+str(self.lins)+":SOUR1:POW:STAT 1\n").encode())
                self.status = "On"

class DFB:
    # Class initialization, acquires maximum and minimum
    # power and wl values, Turns on the source at maximum power and 1550 nm
    # Everything done with source 1 out of 4 (See SOUR1 in SCPI commands)
    def __init__(self, platform_name1, platform_obj1, lins_no):
        self.lins = lins_no
        self.platform_name = platform_name1
        self.platform_obj = platform_obj1
        self.units = "DBM"
        self.status = "On"
        if self.platform_name == "LTB8":
            self.platform_obj.sendall(("LINS"+str(self.lins)+":SOUR1:POW:STAT 1\n").encode())
    
    def turnOn(self):
        self.status = "On"
        self.platform_obj.sendall(("LINS"+str(self.lins)+":SOUR1:POW:STAT 1\n").encode())

    def turnOff(self):
            self.status = "Off"
            self.platform_obj.sendall(("LINS"+str(self.lins)+":SOUR1:POW:STAT 0\n").encode())

# Class establishing OSA status and operations
# 1. Get power and wl min/max
# 2. Start and Inband averaging and saving the traces
class OSA:
    # Class initialization, Establishes the wl range to default 1525-1565
    def __init__(self, platform_name1, platform_obj1, lins_no):
        self.lins = lins_no
        self.platform_name = platform_name1
        self.platform_obj = platform_obj1
        self.wl_span = [1525e-9, 1565e-9]
        self.nSOP = 300
        print("OSA "+str(self.lins)+" initialized successfully")

    def inband_Analysis(self, wl_range, n_states, filepath):
        self.wl_span = wl_range
        self.nSOP = n_states
        self.platform_obj.sendall(("LINS"+str(self.lins)+":SENS:CORR:OFFS:MAGN 0.0 DB\n").encode())
        self.platform_obj.sendall(("LINS"+str(self.lins)+":SENS:WAV:OFFS 0 NM\n").encode())
        self.platform_obj.sendall(("LINS"+str(self.lins)+":SENS:WAV:STAR "+str(self.wl_span[0])+" M\n").encode())
        self.platform_obj.sendall(("LINS"+str(self.lins)+":SENS:WAV:STOP "+str(self.wl_span[1])+" M\n").encode())
        self.platform_obj.sendall(("LINS"+str(self.lins)+":SENS:AVER:STAT ON\n").encode())
        self.platform_obj.sendall(("LINS"+str(self.lins)+":SENS:AVER:TYPE:PMMH\n").encode())
        self.platform_obj.sendall(("LINS"+str(self.lins)+":SENS:AVER:COUN "+str(self.nSOP)+"\n").encode())
        self.platform_obj.sendall(("LINS"+str(self.lins)+":TRIG:SEQ:SOUR IMM\n").encode())
        while True:
            self.platform_obj.sendall(("LINS"+str(self.lins)+":STAT?\n").encode())
            stat = self.platform_obj.recv(4096).decode("utf-8")
            if "READY" in stat:
                break
        self.platform_obj.sendall(("LINS"+str(self.lins)+":INIT:IMM\n").encode())
        while True:
            self.platform_obj.sendall(("LINS"+str(self.lins)+":STAT:OPER:BIT8:COND?\n").encode())
            end = self.platform_obj.recv(4096).decode("utf-8")
            if int(end) == 0:
                break
        self.platform_obj.sendall(("LINS"+str(self.lins)+":MMEM:STOR:MEAS:WDM "+str(filepath)+"\n").encode())
        print("Trace saved in: "+str(filepath))

"""
# Declaring platforms
ltb8 = LTB('169.254.244.64', 5025).platform
iqs600 = IQS(12).platform
mpc_201 = MPC_201(5)

# Declaring modules
voa_sig = VOA("IQS600", iqs600, 2)
voa_2km = VOA("IQS600", iqs600, 4)
voa_ase = VOA("IQS600", iqs600, 3)
voa_scr = VOA("LTB8", ltb8, 1)
tls = TLS("LTB8", ltb8, 0)
osa = OSA("LTB8", ltb8, 4)
"""



















