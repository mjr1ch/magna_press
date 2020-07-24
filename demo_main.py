from uio.ti.icss import Icss
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
import sys # We need sys so that we can pass argv to QApplication
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox

from demo_window import Ui_MainWindow # This file holds our MainWindow and all design related things
              # it also keeps events etc that we defined in Qt Designer


class MainWindow(QtWidgets.QMainWindow):
    
    pruss = Icss( "/dev/uio/pruss/module" )
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        ui = Ui_MainWindow()
        ui.setupUi(self)
        ui.bttn_close.clicked.connect(self.CloseButton_on_click)
        ui.bttn_captureZero.clicked.connect(self.CaptureZeroButton_on_click)
        self.pruss.uart.initialize(baudrate = 9600)
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
        self.pruss.uart.io.write(b'CG\r')
        self.pruss.uart.io.readline(newline =b'\r')
        self._openCalibration()
        self.pruss.uart.io.write(bytes('CG ' + self.tb_span.value + '\r','ascii'))
        self.pruss.uart.io.readline(newline =b'\r')

    @pyqtSlot()
    def TareButton_on_click(self):
        self.pruss.uart.io.write(b'ST\r')
        self.pruss.uart.io.readline(newline =b'\r')

    @pyqtSlot()
    def CaptureZeroButton_on_click(self):
        self._openCalibration()
        pass

    @pyqtSlot()
    def PollSensorButton_on_click(self):
        self.pruss.uart.io.write(b'CG\r')
        response = self.pruss.uart.io.readline(newline =b'\r')
        weight = self._trimMessage(response,2,len(response))
        self.lcd_weight.value = str(weight)

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

if __name__ == '__main__':
    main()
