from uio.ti.icss import Icss
from uio.ti.pwmss import Pwmss
from ctypes import c_uint32 as uint32, c_uint8 as uint8, c_uint64 as uint64, c_char as char, Structure 
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSlot, QTimer
import sys # We need sys so that we can pass argv to QApplication
import cursor
import array 
from time import sleep
from random import randint
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox
from numpad_modal import NumPadPopup
import Adafruit_BBIO.GPIO as gpio
from demo_window import Ui_MainWindow # This file holds our MainWindow and all design related things
              # it also keeps events etc that we defined in Qt Designer


class TimeStamp( Structure ):
    _fields_ = [ 
            ("seconds",uint32),
            ("nano_seconds",uint32)
        ]

class ResponseMessage( Structure ):
    _fields_ = [ 
            ("spot_0",char),
            ("spot_1",char),
            ("spot_2",char),
            ("spot_3",char),
            ("spot_4",char),
            ("spot_5",char),
            ("spot_6",char),
            ("spot_7",char)
        ]



class PruVars( Structure ): 
    _fields_ = [ 
            ("time", TimeStamp),  
            ("position", uint32), # in encoder pulsest 1140 per Revo 
            ("force", uint8),  # in grams i
            ("duty_cycle", uint8), # duty cycle 0%-100%
            ("wave_shape",uint8), # wave shape input  
            ("response", ResponseMessage) 
        ]

class MainWindow(QtWidgets.QMainWindow):
    
    pruss = Icss( "/dev/uio/pruss/module" )
    ui = Ui_MainWindow()
    core_0 = pruss.core0
    core_1 = pruss.core1
    period = 10000
    position = None 
    weight = None 
    pen_weight = None 
    pen_position = None
    timer = QTimer()
    position_line = None  
    pruvars = None 
    weight_line = None 
    time_array = [0]
    position_array = [0]
    weight_array = [0]
    motor = Pwmss("/dev/uio/pwmss0").pwm
    maxloadposition = None
    minloadposition = None 
    _running = None
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.ui.setupUi(self)
        self.ui.bttn_close.clicked.connect(self.CloseButton_on_click)
        self.ui.bttn_captureZero.clicked.connect(self.CaptureZeroButton_on_click)
        self.ui.bttn_setSpan.clicked.connect(self.SetSpanButton_on_click)
        self.ui.bttn_tareScale.clicked.connect(self.TareScaleButton_on_click)
        self.ui.bttn_pollSensors.clicked.connect(self.PollSensorsButton_on_click) 
        self.ui.bttn_start.clicked.connect(self.StartButton_on_click)
        self.ui.bttn_reset.clicked.connect(self.ResetButton_on_click)
        self.ui.bttn_stopRun.clicked.connect(self.StopRunButton_on_click)
        self.ui.bttn_setTopBottom.clicked.connect(self.SetTopBottom_on_click)
        self.ui.hs_motorControl.valueChanged.connect(self.MotorControlSlider_on_valuechange)
        self.ui.rb_forward.toggled.connect(lambda:self.RadioButton_on_click(self.ui.rb_forward))
        self.ui.rb_reverse.toggled.connect(lambda:self.RadioButton_on_click(self.ui.rb_reverse))
        self.ui.bttn_stopMotor.clicked.connect(self.StopMotorButton_on_click)
        self.ui.bttn_goTop.clicked.connect(self.GoTopButton_on_click)
        self.ui.bttn_goBottom.clicked.connect(self.GoBottomButton_on_click)
        self.ui.rb_forward.setChecked(True)
        self.ui.hs_motorControl.setMaximum(self.period)
        self.ui.hs_motorControl.setMinimum(0)
        self.ui.hs_motorControl.setSingleStep(1)
        self.ui.hs_motorControl.setValue(1)
        self.ui.tb_dutyCycle.setText("0%")
        self.ui.lcd_timer.setDigitCount(9)

       # setup plot
        pen_weight = pg.mkPen(color=(255,255,0), width=5)
        pen_position = pg.mkPen(color=(0, 0, 255), width=5)
        styles = {'color':'y', 'font-size':'25px'}
        self.ui.graph.setLabel('left', 'Weight (g)', **styles)
        self.ui.graph.setLabel('bottom', 'Time (s)', **styles)
        self.position_line = self.ui.graph.plot([0], [0], pen = pen_position)
        self.weight_line = self.ui.graph.plot([0], [0], pen = pen_weight)
        
        #setup_pruss
        self.pruss.uart.initialize(baudrate = 460800)
        self.core_0.load('decoder.bin')
        self.core_0.run()
        self.position = self.pruss.dram0.map( uint32 )
        self.pruvars = self.pruss.dram1.map( PruVars )
        self._Init_EM100()
        self.motor.initialize(self.period,1) 

    def _TrimMessage(self,message,start,finish):
        return message[start-1:finish-1]

    def _Init_EM100(self):
        # set max value
        #self.pruss.uart.io.write(b'CM 1\r')
        #self.pruss.uart.io.readline(newline =b'\r')
        #self._OpenCalibration()
        #self.pruss.uart.io.write(bytes('CM 1 999999\r','ascii'))
        #self.pruss.uart.io.readline(newline =b'\r')

        # set min value
        #self.pruss.uart.io.write(b'CI 1\r')
        #self.pruss.uart.io.readline(newline =b'\r')
        #self._OpenCalibration()
        #self.pruss.uart.io.write(bytes('CI -999999\r','ascii'))
        #self.pruss.uart.io.readline(newline =b'\r')

        # set output to grams
        #self.pruss.uart.io.write(b'DP\r')
        #self.pruss.uart.io.readline(newline =b'\r')
        #self._OpenCalibration()
        #self.pruss.uart.io.write(bytes('DP 0\r','ascii'))
        #self.pruss.uart.io.readline(newline =b'\r')
        pass

    
    def _ConvertTime(self,seconds,nano_seconds):
        milli = float(nano_seconds/1E3)
        sec =  float(nano_seconds/1E9)
        return float(seconds+sec+milli*1E-3)
    
    
    def _OpenCalibration(self):
        self.pruss.uart.io.write(b'CE\r')
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        calib_num = int(self._TrimMessage(response,3,len(response)))
        self.pruss.uart.io.write(bytes('CE ' + str(calib_num) + '\r','ascii'))
        response = self.pruss.uart.io.readline(newline =b'\r').decode("ascii")
        #QMessageBox.about(self, "Response", response)

    def _UpdatePlot(self,time,weight,position):    
        
        if len(self.time_array) > 100:
            self.time_array = self.time_array[1:]  # Remove the first y element.
            self.position_array = self.position_array[1:]   
            self.weight_array = self.weight_array[1:] 
        
        self.time_array.append( time )  # Add a new value 1 higher than the last.
        self.position_array.append( position )  # Add a new random value.
        self.weight_array.append ( weight )
        
        self.position_line.setData(self.time_array, self.position_array) 
        self.weight_line.setData(self.time_array, self.weight_array) 

    def _DecodeCharString(self,response):
        value = response.spot_0.decode('ascii') + response.spot_1.decode('ascii') + response.spot_2.decode('ascii') + \
                response.spot_3.decode('ascii') + response.spot_4.decode('ascii') + response.spot_5.decode('ascii') + \
                response.spot_6.decode('ascii') + response.spot_7.decode('ascii') 
        return value 
            
    
    
    def _ConvertToAngle(self,pos):
        p = float((pos + 1) % 1440)
        a = float(p*360/1440)
        return a 

    def _MotorGoToAngle(self,target):
        
        current_angle = self._ConvertToAngle(self.position.value)
        print(current_angle)
        
        if (abs(target - current_angle)  >= 180 ):
            self.motor.ld_compare_a = int(self.period/8)
            self.motor.ld_compare_b = 0 
        else:
            self.motor.ld_compare_a = 0 
            self.motor.ld_compare_b = int(self.period/8)
        
        while (abs(current_angle - target) > 0.001):
            sleep(0.001)
            togo = abs(target- current_angle)
            print("Target angle is {} and Current Angle is {} the difference is {}".format(target,current_angle,togo))
            current_angle = self._ConvertToAngle(self.position.value)
        
        self.motor.ld_compare_a = 0 
        self.motor.ld_compare_b = 0 

    @pyqtSlot()
    def CloseButton_on_click(self):
        self.close()
   
    @pyqtSlot()
    def SetSpanButton_on_click(self):
        self.setEnabled(False)
        self.spanvalue = NumPadPopup()
        self.spanvalue.show()
        self.spanvalue.exec_()
        self.ui.tb_span.setText(str(self.spanvalue.result))
        self.setEnabled(True)
        span = int(self.ui.tb_span.text())
        self.pruss.uart.io.write(b'CG\r')
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        self._OpenCalibration()
        self.pruss.uart.io.write(bytes('CG ' + str(span) + '\r','ascii'))
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        self._OpenCalibration()
        self.pruss.uart.io.write(b'CS\r')
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        QMessageBox.about(self, "Response", response)

    @pyqtSlot()
    def SetTopBottom_on_click(self):
        self.motor.ld_compare_a = int(self.period/8)
        self.motor.ld_compare_b = 0
        self.core_1.load('find_max.out')
        self.core_1.run()
        counter = 0
        while(1):
            angle = self._ConvertToAngle(self.pruvars.position) 
            weight = self.pruvars.force
            print("Angle = {}, Force = {}".format(angle,weight))
            counter = counter + 1
            sleep(0.5)
            if (counter > 50):
                break
        self.pruss.uart.io.write( b'FFV\r', discard=True, flush=True )  # interrupt continuous transmission
        sleep( 0.1 )  # make sure that response has been received
        self.pruss.uart.io.discard()  # discard response
        self.StopMotorButton_on_click()
        self.core_1.halt()
        self.ui.lcd_weight.display(self.pruvars.force)
        angle = self._ConvertToAngle(self.pruvars.position) 
        self._MotorGoToAngle(angle)    
        self.maxloadposition = angle
        self.minloadposition = float((angle + 180) % 360)
        self.ui.lcd_position.display(angle)
        time = self.pruvars.time.seconds
        self.ui.lcd_timer.display(time)
        self.GoBottomButton_on_click()
        self.position.value = 0

    @pyqtSlot()
    def GoTopButton_on_click(self):
        target_angle = self.maxloadposition
        self._MotorGoToAngle(target_angle)


    @pyqtSlot()
    def GoBottomButton_on_click(self):
        target_angle = self.minloadposition
        self._MotorGoToAngle(target_angle)

    @pyqtSlot()
    def TareScaleButton_on_click(self):
        self.pruss.uart.io.write(b'ST\r')
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        QMessageBox.about(self, "Response", response)

    @pyqtSlot()
    def CaptureZeroButton_on_click(self):
        self._OpenCalibration()
        self.pruss.uart.io.write(b'CZ\r')
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        #QMessageBox.about(self, "Response", response)

    @pyqtSlot()
    def PollSensorsButton_on_click(self):
        self.pruss.uart.io.write(b'GN\r')
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        print(response)
        weight = self._TrimMessage(response,3,len(response))
        self.ui.lcd_weight.display(weight)
        position = (self.position.value + 1) % 1440
        angle = float(position*360/1440)
        self.ui.lcd_position.display(angle)

    @pyqtSlot() 
    def StartButton_on_click(self):
        self._running = True
        self.core_1.load('record_run.out')
        self.core_1.run()
        counter = 0 
        cs = 0
        ss = 0
        mm = 0
        plot_time = 0
        self.pruss.ecap.pwm.initialize( 200000000 )
        second_passed = False
        while(self._running):
            ms = self.pruvars.time.nano_seconds//1000000
            ss = self.pruvars.time.seconds % 60
            if (self.pruvars.time.nano_seconds > 9.90E8):
                second_passed = True 
            if (ss == 0) and (second_passed):
                mm = mm + 1 
                second_passed = False 
            plot_time = float(60*mm + ss + ms/1000) 
            time = '{}:{}:{:03d}'.format(mm,ss,ms)
            weight = self.pruvars.force
            msg = self._DecodeCharString(self.pruvars.response)
            print(msg)
            #msg = int(self._TrimMessage(msg,3,9))
            msg = msg.lstrip("N+-")
            msg = msg.replace('\x00','')
            #weight = int(msg.lstrip("N+"))
            weight = int(msg)
            
            angle = self._ConvertToAngle(self.pruvars.position)


            if (angle >= 180): 
                angle = 360 - angle
            self._UpdatePlot(plot_time,weight,angle)
            QtGui.QApplication.processEvents()
            self.ui.lcd_timer.display(time)
            counter = counter + 1
            sleep(0.001)
            self.ui.lcd_weight.display(self.pruvars.force)
            self.ui.lcd_position.display(angle)
    
        self.pruss.uart.io.write( b'FFV\r', discard=True, flush=True )  # interrupt continuous transmission
        sleep( 0.1 )  # make sure that response has been received
        self.pruss.uart.io.discard()  # discard response

    @pyqtSlot()
    def StopMotorButton_on_click(self):
        self.motor.ld_compare_a = 0
        self.motor.ld_compare_b = 0
        self.ui.hs_motorControl.setValue(0)
        self.ui.tb_dutyCycle.setText("0%")

    @pyqtSlot()
    def RadioButton_on_click(self,b):
        if b.isChecked():
            b.setChecked(False)
        else:
            b.setChecked(True)

    @pyqtSlot()
    def MotorControlSlider_on_valuechange(self):
        newSpeed = self.ui.hs_motorControl.value()
        if (self.ui.rb_forward.isChecked()):
            self.motor.ld_compare_a = newSpeed
            self.motor.ld_compare_b = 0
        else:
            self.motor.ld_compare_a = 0
            self.motor.ld_compare_b = newSpeedi
        duty_cycle = int(newSpeed/self.period*100)
        self.ui.tb_dutyCycle.setText("{}%".format(duty_cycle))

    @pyqtSlot()
    def ResetButton_on_click(self):
        self.ui.graph.clear()

    @pyqtSlot()
    def StopRunButton_on_click(self):
        print("stopping")
        self.core_1.halt()
        self._running = False 

def main():
    app = QApplication(sys.argv) # A new instance of QApplicatio0n
    screen = MainWindow()
    screen.show()
    sys.exit(app.exec())
    core_0.halt()

if __name__ == '__main__':
    main()
