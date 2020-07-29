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
#from numpad_popup import numpadPopup
from demo_window import Ui_MainWindow # This file holds our MainWindow and all design related things
              # it also keeps events etc that we defined in Qt Designer


class MainWindow(QtWidgets.QMainWindow):
    
    pruss = Icss( "/dev/uio/pruss/module" )
    ui = Ui_MainWindow()
    core_0 = pruss.core0
    core_1 = pruss.core1
    position = None 
    weight = None 
    pen_weight = None 
    pen_position = None
    timer = QTimer()
    position_line = None  
    weight_line = None 
    time_array = [0]
    position_array = [0]
    weight_array = [0] 

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
        self.ui.bttn_stop.clicked.connect(self.StopButton_on_click)
        
        pen_weight = pg.mkPen(color=(255,255,0), width=5)
        pen_position = pg.mkPen(color=(0, 0, 255), width=5)
        styles = {'color':'y', 'font-size':'25px'}
        self.ui.graph.setLabel('left', 'Weight (g)', **styles)
        self.ui.graph.setLabel('bottom', 'Time (s)', **styles)
        self.position_line = self.ui.graph.plot([0], [0], pen = pen_position)
        self.weight_line = self.ui.graph.plot([0], [0], pen = pen_weight)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self._updatePlot)
        self.pruss.uart.initialize(baudrate = 9600)
        self.core_0.load('decoder.bin')
        self.core_0.run()
        self.position = self.pruss.dram0.map( uint32 )
        self._init_EM100()

    def _trimMessage(self,message,start,finish):
        return message[start-1:finish-1]

    def _init_EM100(self):
        # set max value
        self.pruss.uart.io.write(b'CM 1\r')
        self.pruss.uart.io.readline(newline =b'\r')
        self._openCalibration()
        self.pruss.uart.io.write(bytes('CM 1 999999\r','ascii'))
        self.pruss.uart.io.readline(newline =b'\r')

        # set min value
        self.pruss.uart.io.write(b'CI 1\r')
        self.pruss.uart.io.readline(newline =b'\r')
        self._openCalibration()
        self.pruss.uart.io.write(bytes('CI -999999\r','ascii'))
        self.pruss.uart.io.readline(newline =b'\r')

        # set output to grams
        self.pruss.uart.io.write(b'DP\r')
        self.pruss.uart.io.readline(newline =b'\r')
        self._openCalibration()
        self.pruss.uart.io.write(bytes('DP 0\r','ascii'))
        self.pruss.uart.io.readline(newline =b'\r')

        # set filter mode
        self.pruss.uart.io.write(b'FM\r')
        self.pruss.uart.io.readline(newline =b'\r')
        self.pruss.uart.io.write(b'FM 1\r')
        self.pruss.uart.io.readline(newline =b'\r')
        self.pruss.uart.io.write(b'WP\r')
        self.pruss.uart.io.readline(newline =b'\r')

        # set filter level
        self.pruss.uart.io.write(b'FL\r')
        self.pruss.uart.io.readline(newline =b'\r')
        self.pruss.uart.io.write(b'FL 6\r')
        self.pruss.uart.io.readline(newline =b'\r')
        self.pruss.uart.io.write(b'WP\r')
        self.pruss.uart.io.readline(newline =b'\r')

    def _openCalibration(self):
        self.pruss.uart.io.write(b'CE\r')
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        calib_num = int(self._trimMessage(response,3,len(response)))
        self.pruss.uart.io.write(bytes('CE ' + str(calib_num) + '\r','ascii'))
        response = self.pruss.uart.io.readline(newline =b'\r').decode("ascii")
        #QMessageBox.about(self, "Response", response)

    def _updatePlot(self):    
        self.pruss.uart.io.write(b'GN\r')
        val = self.pruss.uart.io.readline(newline =b'\r').decode("ascii")
        val = self._trimMessage(val,3,len(val))
        if val.isdigit():
            val = int(val)
        else:
            val = 0 
        
        
        if len(self.time_array) > 100:
            self.time_array = self.time_array[1:]  # Remove the first y element.
            self.position_array = self.position_array[1:]   
            self.weight_array = self.weight_array[1:] 
        
        self.time_array.append(self.time_array[-1] + 1)  # Add a new value 1 higher than the last.
        self.position_array.append(0 )  # Add a new random value.
        self.weight_array.append ( val)
        
        self.position_line.setData(self.time_array, self.position_array) 
        self.weight_line.setData(self.time_array, self.weight_array) 
        self.ui.lcd_timer.display(self.time_array[-1])

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
        self._openCalibration()
        self.pruss.uart.io.write(bytes('CG ' + str(span) + '\r','ascii'))
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        QMessageBox.about(self, "Response", response)


    @pyqtSlot()
    def TareScaleButton_on_click(self):
        self.pruss.uart.io.write(b'ST\r')
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        QMessageBox.about(self, "Response", response)

    @pyqtSlot()
    def CaptureZeroButton_on_click(self):
        self._openCalibration()
        self.pruss.uart.io.write(b'CZ\r')
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        QMessageBox.about(self, "Response", response)

    @pyqtSlot()
    def PollSensorsButton_on_click(self):
        self.pruss.uart.io.write(b'GN\r')
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        weight = self._trimMessage(response,3,len(response))
        self.ui.lcd_weight.display = str(int(weight))
        self.ui.lcd_position.display = self.position

    @pyqtSlot() 
    def StartButton_on_click(self):
        #self.pruss.uart.io.write(b'SN\r')
        self.timer.start()

    @pyqtSlot()
    def ResetButton_on_click(self):
        self.ui.graph.clear()

    @pyqtSlot()
    def StopButton_on_click(self):
        self.pruss.uart.io.write(b'FPN\r')
        self.timer.stop()

def main():
    app = QApplication(sys.argv) # A new instance of QApplicatio0n
    screen = MainWindow()
    screen.show()
    sys.exit(app.exec())
    core_0.halt()

if __name__ == '__main__':
    main()
