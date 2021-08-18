from time import sleep
from uio.ti.icss import Icss
from ctypes import c_uint32 as uint32, c_uint8 as uint8
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QTimer
import sys # We need sys so that we can pass argv to QApplication
import cursor
from random import randint
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox
from numpad_modal import NumPadPopup
import Adafruit_BBIO.GPIO as gpio
from demo_window import Ui_MainWindow # This file holds our MainWindow and all design related things
              # it also keeps events etc that we defined in Qt Designe
            
from uio.ti.pwmss import Pwmss

pruss = Icss( "/dev/uio/pruss/module" )
core_0 = pruss.core0
position = pruss.core0.shared_dram.map( uint32 )
core_0.load('decoder.dbg')
core_0.run()


ehrpwm0 = Pwmss("/dev/uio/pwmss0").pwm

period = 10000
max_duty = period


ehrpwm0.initialize(period,1)
ehrpwm0.ld_compare_a = int(max_duty/4)
ehrpwm0.ld_compare_b = 0
counter = 0 

while(1):
    angle = position.value % 1440
    print("position {} angle {}".format(position,angle))
    counter+= 1
    if (counter > 30000):
        break


ehrpwm0.ld_compare_a = 0

core_0.halt()
