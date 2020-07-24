from uio.ti.icss import Icss
from ctypes import c_uint32 as uint32, c_uint8 as uint8
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
import sys # We need sys so that we can pass argv to QApplication
import cursor
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox
from number_pad import numberPopup
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

    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.ui.setupUi(self)
        self.ui.bttn_close.clicked.connect(self.CloseButton_on_click)
        self.ui.bttn_captureZero.clicked.connect(self.CaptureZeroButton_on_click)
        self.ui.bttn_setSpan.clicked.connect(self.SetSpanButton_on_click)
        self.ui.bttn_tareScale.clicked.connect(self.TareScaleButton_on_click)
        self.pruss.uart.initialize(baudrate = 9600)
        self.core_0.load('decoder.bin')
        self,core_0.run()
        self.poistion = self.pruss.dram0.map( uint32 )
        self._init_EM100()

    def _trimMessage(self,message,start,finish):
        return message[start-1:finish-1]

    def _init_EM100(self):
        # set max value
        self.pruss.uart.io.write(b'CM 1\r')
        self.pruss.uart.io.readline(newline =b'\r')
        self._openCalibration()
        self.pruss.uart.io.write(bytes('CM 1 60000\r','ascii'))
        self.pruss.uart.io.readline(newline =b'\r')

        # set min value
        self.pruss.uart.io.write(b'CI 1\r')
        self.pruss.uart.io.readline(newline =b'\r')
        self._openCalibration()
        self.pruss.uart.io.write(bytes('CI 0\r','ascii'))
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

    @pyqtSlot()
    def CloseButton_on_click(self):
        self.close()
   
    @pyqtSlot()
    def SetSpanButton_on_click(self):
        self.setEnabled(False)
        self.exPopup = numberPopup()
        self.exPopup.setGeometry(130, 320,400, 300)
        self.exPopup.show()  
        self.pruss.uart.io.write(b'CG\r')
        self.pruss.uart.io.readline(newline =b'\r')
        self._openCalibration()
        self.pruss.uart.io.write(bytes('CG ' + self.ui.tb_span.text() + '\r','ascii'))
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
    def PollSensorButton_on_click(self):
        self.pruss.uart.io.write(b'CG\r')
        response = self.pruss.uart.io.readline(newline =b'\r')
        weight = self._trimMessage(response,2,len(response))
        self.lcd_weight.display = str(weight)
        self.lcd_position.display = self.position

    @pyqtSlot() 
    def StartButton_on_click(self):
        pass

    @pyqtSlot()
    def ResetButton_on_click(self):
        pass

    @pyqtSlot()
    def StopButton_on_click(self):
        pass 

def main():
    app = QApplication(sys.argv) # A new instance of QApplicatio0n
    screen = MainWindow()
    screen.show()
    sys.exit(app.exec())
    core_0.halt()

if __name__ == '__main__':
    main()
