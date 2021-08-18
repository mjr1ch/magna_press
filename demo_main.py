from uio.ti.icss import Icss
from uio.ti.pwmss import Pwmss
from ctypes import c_uint32 as uint32, c_uint8 as uint8, c_uint64 as uint64, c_char as char, c_int32 as int32, Structure 
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QTimer, QThread, QObject
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


class PruVars( Structure ): 
    _fields_ = [ 
            ("position", uint32), # in encoder pulsest 1140 per Revo 
            ("force", int32),  # in grams i
            ("duty_cycle", uint8), # duty cycle 0%-100%
            ("wave_shape",uint8), # wave shape input  
        ]


class Communicate(QObject):

    newdata = pyqtSignal(int, int)


class PollPRUThread(QThread):
    
    def __init__(self,core,pruvars):
        QThread.__init__(self)
        self.pru_core = core
        self.vars = pruvars
        self.c = Communicate()

    def run(self):
        _running = True
        self.pru_core.run()
        while(1):
            weight = self.vars.force
            position = self.vars.position
            self.c.newdata.emit(weight,position)
            sleep(0.1)
            if (self.pru_core.halted):
                break

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
    _last_timestamp_cycles = 0
    pru_thread = 0
    zero_offset = 0

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
        self.ui.bttn_resetTare.clicked.connect(self.ResetTareButton_on_click)
        self.ui.bttn_systemZero.clicked.connect(self.SystemZeroButton_on_click)
        self.ui.bttn_stopRun.clicked.connect(self.StopRunButton_on_click)
        self.ui.bttn_setTopBottom.clicked.connect(self.SetTopBottom_on_click)
        self.ui.hs_motorControl.valueChanged.connect(self.MotorControlSlider_on_valuechange)
        self.ui.rb_forward.toggled.connect(lambda:self.FwdRadioButton_on_click(self.motor.ld_compare_a,self.motor.ld_compare_b))
        self.ui.rb_reverse.toggled.connect(lambda:self.RevRadioButton_on_click(self.motor.ld_compare_a,self.motor.ld_compare_b))
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
        self.pruvars = self.pruss.dram2.map( PruVars )
        self._Init_EM100()
        self.motor.initialize(self.period,1) 

    def timestamp_cycles(self):
        """Returns the current timestamp in PRU cycles (integer)"""
        self._last_timestamp_cycles += ( self.pruss.ecap.counter - self._last_timestamp_cycles ) & 0xffffffff
        return self._last_timestamp_cycles

    def timestamp_ns(self):
        """Returns the current timestamp in nanoseconds (integer)"""
        return self.timestamp_cycles() * 5

    def timestamp_seconds(self):
        """Returns the current timestamp in seconds (floating-point)"""
        return self.timestamp_cycles() / 200e6

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

    def _ChangeDirection(self):
        if (self.ui.rb_forward.isChecked()):
            self.ui.rb_reverse.setChecked(True)
            #self.RevRadioButton_on_click(self.motor.ld_compare_a,self.motor.ld_compare_b)
        else:
            self.ui.rb_forward.setChecked(True)
            #self.FwdRadioButton_on_click(self.motor.ld_compare_a,self.motor.ld_compare_b)
    
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

    def _UpdateGui(self,weight,position):
        time_point = self.timestamp_seconds()
        mm = int(self.timestamp_seconds()/60)
        ss = int(time_point % 60 )
        ms = int((time_point % 1)*1000) 
        time = '{}:{}:{}'.format(mm,ss,ms)
        angle = self._ConvertToAngle(position)
        if (angle >= 180): 
            angle = 360 - angle
        self._UpdatePlot(time_point,weight,angle)
        print("{} {} {}".format(time,angle,weight))
        self.ui.lcd_timer.display(time)
        self.ui.lcd_weight.display(weight)
        self.ui.lcd_position.display(angle)

    def _ConvertToAngle(self,pos):
        p = float((pos + 1) % 1440)
        a = float(p*360/1440)
        return a 

    def _MotorGoToAngle(self,target):
        
        current_angle = self._ConvertToAngle(self.position.value)
        
        if (abs(target - current_angle)  >= 180 ):
            self.motor.ld_compare_a = int(self.period/8)
            self.motor.ld_compare_b = 0 
        else:
            self.motor.ld_compare_a = 0 
            self.motor.ld_compare_b = int(self.period/8)
        
        while (abs(current_angle - target) > 0.001):
            sleep(0.001)
            togo = abs(target- current_angle)
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
        max_weight = 0 
        max_position = 0
        prev_weight = 0 
        max_counter = 0
        desc_counter = 0 
        while(1):
            angle = self._ConvertToAngle(self.pruvars.position) 
            weight = self.pruvars.force
            print("Counter {} Max_Counter {} Descreasing Counter {}".format(counter,max_counter,desc_counter))
            if (weight >= prev_weight):
                desc_counter = 0 
                print("weight increaseing new max weight set")
                if (weight > max_weight):
                    max_weight = weight
                    max_position = angle
                    max_counter = 0
                else:
                    print("weight increasing but below max weight")
                    max_counter = max_counter + 1
            else: 
                max_counter = max_counter + 1
                if (desc_counter > 3):
                    print("Weight dscresing for too long changing direction")
                    self._ChangeDirection()
                    desc_counter = 0 
                else: 
                    print("Weight descrsing but not long enough to give up this way")
                    desc_counter = desc_counter + 1
            if (max_counter > 30 or counter > 500):
                break
            counter = counter + 1
            prev_weight = weight
            sleep(0.25)
            
        self.pruss.uart.io.write( b'FFV\r', discard=True, flush=True )  # interrupt continuous transmission
        sleep( 0.1 )  # make sure that response has been received
        self.pruss.uart.io.discard()  # discard response
        self.StopMotorButton_on_click()
        self.core_1.halt()
        self.ui.lcd_weight.display(self.pruvars.force)
        angle = self._ConvertToAngle(self.pruvars.position) 
        self.maxloadposition = max_position
        self.minloadposition = abs(max_position - 180)
        self.GoBottomButton_on_click()
        self.zero_offset = self.position.value
        #self.ui.lcd_position.display(angle)
    
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
    def ResetTareButton_on_click(self):
        self.pruss.uart.io.write(b'RT\r')
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        QMessageBox.about(self, "Response", response)
    
    @pyqtSlot()
    def SystemZeroButton_on_click(self):
        self.pruss.uart.io.write(b'SZ\r')
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        QMessageBox.about(self, "Response", response)
    
    @pyqtSlot()
    def CaptureZeroButton_on_click(self):
        self._OpenCalibration()
        self.pruss.uart.io.write(b'CZ\r')
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')

    @pyqtSlot()
    def PollSensorsButton_on_click(self):
        self.pruss.uart.io.write(b'GN\r')
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        print(response)
        weight = int(self._TrimMessage(response,2,len(response)))
        self.ui.lcd_weight.display(weight)
        position = (self.position.value + 1) % 1440
        angle = float(position*360/1440)
        self.ui.lcd_position.display(angle)

    @pyqtSlot() 
    def StartButton_on_click(self):
        self.c = Communicate()
        self.core_1.load('record_run.out')
        self.last_timestamp_cycles = 0
        self.pruss.ecap.pwm.initialize( 2**32 )
        self.pru_thread = PollPRUThread(self.core_1,self.pruvars)
        self.pru_thread.c.newdata.connect(self._UpdateGui)
        self.pru_thread.start()

    @pyqtSlot()
    def StopMotorButton_on_click(self):
        self.motor.ld_compare_a = 0
        self.motor.ld_compare_b = 0
        self.ui.hs_motorControl.setValue(0)
        self.ui.tb_dutyCycle.setText("0%")

    @pyqtSlot()
    def FwdRadioButton_on_click(self,a,b):
        if (b > 0):
            self.motor.ld_compare_a = b
            self.motor.ld_compare_b = 0
        else:
            pass


    @pyqtSlot()
    def RevRadioButton_on_click(self,a,b):
        if (a > 0):
            self.motor.ld_compare_a = 0
            self.motor.ld_compare_b = a
        else:
            pass


    @pyqtSlot()
    def MotorControlSlider_on_valuechange(self):
        newSpeed = self.ui.hs_motorControl.value()
        if (self.ui.rb_forward.isChecked()):
            self.motor.ld_compare_a = newSpeed
            self.motor.ld_compare_b = 0
        else:
            self.motor.ld_compare_a = 0
            self.motor.ld_compare_b = newSpeed
        duty_cycle = int(newSpeed/self.period*100)
        self.ui.tb_dutyCycle.setText("{}%".format(duty_cycle))

    @pyqtSlot()
    def ResetButton_on_click(self):
        self.ui.graph.clear()

    @pyqtSlot()
    def StopRunButton_on_click(self):
        self.pruss.uart.io.write( b'FFV\r', discard=True, flush=True )  # interrupt continuous transmission
        sleep( 0.1 )  # make sure that response has been received
        self.pruss.uart.io.discard()  # discard response
        print("stopping")
        self.pru_thread.quit()
        self.core_1.halt()

def main():
    app = QApplication(sys.argv) # A new instance of QApplicatio0n
    screen = MainWindow()
    screen.show()
    sys.exit(app.exec())
    core_0.halt()

if __name__ == '__main__':
    main()
