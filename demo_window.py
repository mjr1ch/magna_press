# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'demoui.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 480)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.graph = PlotWidget(self.centralwidget)
        self.graph.setGeometry(QtCore.QRect(360, 70, 411, 251))
        self.graph.setObjectName("graph")
        self.bttn_start = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_start.setGeometry(QtCore.QRect(360, 340, 131, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.bttn_start.setFont(font)
        self.bttn_start.setObjectName("bttn_start")
        self.bttn_stop = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_stop.setGeometry(QtCore.QRect(640, 340, 131, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.bttn_stop.setFont(font)
        self.bttn_stop.setObjectName("bttn_stop")
        self.bttn_reset = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_reset.setGeometry(QtCore.QRect(500, 340, 131, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.bttn_reset.setFont(font)
        self.bttn_reset.setObjectName("bttn_reset")
        self.tb_span = QtWidgets.QLineEdit(self.centralwidget)
        self.tb_span.setGeometry(QtCore.QRect(160, 50, 113, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.tb_span.setFont(font)
        self.tb_span.setObjectName("tb_span")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 50, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setItalic(False)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 180, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setItalic(False)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.bttn_captureZero = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_captureZero.setGeometry(QtCore.QRect(20, 10, 251, 28))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setItalic(False)
        self.bttn_captureZero.setFont(font)
        self.bttn_captureZero.setObjectName("bttn_captureZero")
        self.bttn_tareScale = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_tareScale.setGeometry(QtCore.QRect(20, 130, 251, 28))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setItalic(False)
        self.bttn_tareScale.setFont(font)
        self.bttn_tareScale.setObjectName("bttn_tareScale")
        self.bttn_setSpan = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_setSpan.setGeometry(QtCore.QRect(20, 90, 251, 28))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setItalic(False)
        self.bttn_setSpan.setFont(font)
        self.bttn_setSpan.setObjectName("bttn_setSpan")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(10, 220, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setItalic(False)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.tb_dutyCycle = QtWidgets.QLineEdit(self.centralwidget)
        self.tb_dutyCycle.setGeometry(QtCore.QRect(150, 180, 113, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.tb_dutyCycle.setFont(font)
        self.tb_dutyCycle.setObjectName("tb_dutyCycle")
        self.tb_delay = QtWidgets.QLineEdit(self.centralwidget)
        self.tb_delay.setGeometry(QtCore.QRect(150, 220, 113, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.tb_delay.setFont(font)
        self.tb_delay.setObjectName("tb_delay")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(380, 20, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setItalic(False)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(0, 320, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setItalic(False)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(10, 370, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setItalic(False)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.lcd_timer = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcd_timer.setGeometry(QtCore.QRect(583, 12, 181, 41))
        self.lcd_timer.setObjectName("lcd_timer")
        self.lcd_weight = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcd_weight.setGeometry(QtCore.QRect(140, 370, 131, 41))
        self.lcd_weight.setObjectName("lcd_weight")
        self.lcd_position = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcd_position.setGeometry(QtCore.QRect(140, 320, 131, 41))
        self.lcd_position.setObjectName("lcd_position")
        self.bttn_close = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_close.setGeometry(QtCore.QRect(640, 410, 131, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.bttn_close.setFont(font)
        self.bttn_close.setObjectName("bttn_close")
        self.bttn_pollSensors = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_pollSensors.setGeometry(QtCore.QRect(40, 420, 211, 28))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setItalic(False)
        self.bttn_pollSensors.setFont(font)
        self.bttn_pollSensors.setObjectName("bttn_pollSensors")
        self.bttn_setMotorSpeed = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_setMotorSpeed.setGeometry(QtCore.QRect(29, 260, 231, 28))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.bttn_setMotorSpeed.setFont(font)
        self.bttn_setMotorSpeed.setObjectName("bttn_setMotorSpeed")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.bttn_close.clicked.connect(MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.bttn_start.setText(_translate("MainWindow", "Start"))
        self.bttn_stop.setText(_translate("MainWindow", "Stop"))
        self.bttn_reset.setText(_translate("MainWindow", "Reset"))
        self.label.setText(_translate("MainWindow", "Span"))
        self.label_2.setText(_translate("MainWindow", "Duty Cycle"))
        self.bttn_captureZero.setText(_translate("MainWindow", "Capture Zero"))
        self.bttn_tareScale.setText(_translate("MainWindow", "Tare Scale"))
        self.bttn_setSpan.setText(_translate("MainWindow", "Set Span"))
        self.label_3.setText(_translate("MainWindow", "Delay"))
        self.label_4.setText(_translate("MainWindow", "Time Elasped:"))
        self.label_5.setText(_translate("MainWindow", "Position"))
        self.label_6.setText(_translate("MainWindow", "Weight"))
        self.bttn_close.setText(_translate("MainWindow", "Close"))
        self.bttn_pollSensors.setText(_translate("MainWindow", "Poll Sensors"))
        self.bttn_setMotorSpeed.setText(_translate("MainWindow", "Set Motor Speed"))

from pyqtgraph import PlotWidget
