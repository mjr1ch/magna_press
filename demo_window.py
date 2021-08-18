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
        self.graph.setGeometry(QtCore.QRect(310, 40, 481, 261))
        self.graph.setObjectName("graph")
        self.bttn_start = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_start.setGeometry(QtCore.QRect(310, 310, 101, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.bttn_start.setFont(font)
        self.bttn_start.setObjectName("bttn_start")
        self.bttn_stopRun = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_stopRun.setGeometry(QtCore.QRect(550, 310, 101, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.bttn_stopRun.setFont(font)
        self.bttn_stopRun.setObjectName("bttn_stopRun")
        self.bttn_reset = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_reset.setGeometry(QtCore.QRect(430, 310, 101, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.bttn_reset.setFont(font)
        self.bttn_reset.setObjectName("bttn_reset")
        self.tb_span = QtWidgets.QLineEdit(self.centralwidget)
        self.tb_span.setGeometry(QtCore.QRect(160, 80, 113, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.tb_span.setFont(font)
        self.tb_span.setObjectName("tb_span")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 80, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.bttn_captureZero = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_captureZero.setGeometry(QtCore.QRect(160, 0, 111, 28))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setItalic(False)
        self.bttn_captureZero.setFont(font)
        self.bttn_captureZero.setObjectName("bttn_captureZero")
        self.bttn_tareScale = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_tareScale.setGeometry(QtCore.QRect(20, 40, 111, 28))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setItalic(False)
        self.bttn_tareScale.setFont(font)
        self.bttn_tareScale.setObjectName("bttn_tareScale")
        self.bttn_setSpan = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_setSpan.setGeometry(QtCore.QRect(20, 120, 251, 28))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setItalic(False)
        self.bttn_setSpan.setFont(font)
        self.bttn_setSpan.setObjectName("bttn_setSpan")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(20, 160, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.tb_dutyCycle = QtWidgets.QLineEdit(self.centralwidget)
        self.tb_dutyCycle.setGeometry(QtCore.QRect(160, 170, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.tb_dutyCycle.setFont(font)
        self.tb_dutyCycle.setObjectName("tb_dutyCycle")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(380, 10, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setItalic(False)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(320, 370, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(560, 370, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.lcd_timer = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcd_timer.setGeometry(QtCore.QRect(560, 0, 181, 41))
        self.lcd_timer.setObjectName("lcd_timer")
        self.lcd_weight = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcd_weight.setGeometry(QtCore.QRect(660, 370, 131, 41))
        self.lcd_weight.setObjectName("lcd_weight")
        self.lcd_position = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcd_position.setGeometry(QtCore.QRect(420, 370, 131, 41))
        self.lcd_position.setObjectName("lcd_position")
        self.bttn_close = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_close.setGeometry(QtCore.QRect(680, 310, 101, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.bttn_close.setFont(font)
        self.bttn_close.setObjectName("bttn_close")
        self.bttn_pollSensors = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_pollSensors.setGeometry(QtCore.QRect(320, 420, 471, 28))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.bttn_pollSensors.setFont(font)
        self.bttn_pollSensors.setObjectName("bttn_pollSensors")
        self.bttn_setTopBottom = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_setTopBottom.setGeometry(QtCore.QRect(0, 340, 271, 28))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.bttn_setTopBottom.setFont(font)
        self.bttn_setTopBottom.setObjectName("bttn_setTopBottom")
        self.lb_topSet = QtWidgets.QLabel(self.centralwidget)
        self.lb_topSet.setGeometry(QtCore.QRect(0, 380, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.lb_topSet.setFont(font)
        self.lb_topSet.setAlignment(QtCore.Qt.AlignCenter)
        self.lb_topSet.setObjectName("lb_topSet")
        self.lb_bottomSet = QtWidgets.QLabel(self.centralwidget)
        self.lb_bottomSet.setGeometry(QtCore.QRect(150, 380, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.lb_bottomSet.setFont(font)
        self.lb_bottomSet.setAlignment(QtCore.Qt.AlignCenter)
        self.lb_bottomSet.setObjectName("lb_bottomSet")
        self.bttn_setDutyCycle = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_setDutyCycle.setGeometry(QtCore.QRect(20, 210, 251, 28))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.bttn_setDutyCycle.setFont(font)
        self.bttn_setDutyCycle.setObjectName("bttn_setDutyCycle")
        self.bttn_goTop = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_goTop.setGeometry(QtCore.QRect(0, 410, 151, 28))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.bttn_goTop.setFont(font)
        self.bttn_goTop.setObjectName("bttn_goTop")
        self.bttn_goBottom = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_goBottom.setGeometry(QtCore.QRect(150, 410, 151, 28))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.bttn_goBottom.setFont(font)
        self.bttn_goBottom.setObjectName("bttn_goBottom")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(10, 250, 271, 24))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.label_8 = QtWidgets.QLabel(self.splitter)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.hs_motorControl = QtWidgets.QSlider(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hs_motorControl.sizePolicy().hasHeightForWidth())
        self.hs_motorControl.setSizePolicy(sizePolicy)
        self.hs_motorControl.setMaximum(100)
        self.hs_motorControl.setProperty("value", 0)
        self.hs_motorControl.setSliderPosition(0)
        self.hs_motorControl.setOrientation(QtCore.Qt.Horizontal)
        self.hs_motorControl.setObjectName("hs_motorControl")
        self.label_7 = QtWidgets.QLabel(self.splitter)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.splitter_2 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_2.setGeometry(QtCore.QRect(10, 280, 261, 36))
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.rb_forward = QtWidgets.QRadioButton(self.splitter_2)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.rb_forward.setFont(font)
        self.rb_forward.setObjectName("rb_forward")
        self.rb_reverse = QtWidgets.QRadioButton(self.splitter_2)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.rb_reverse.setFont(font)
        self.rb_reverse.setObjectName("rb_reverse")
        self.bttn_stopMotor = QtWidgets.QPushButton(self.splitter_2)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.bttn_stopMotor.setFont(font)
        self.bttn_stopMotor.setObjectName("bttn_stopMotor")
        self.bttn_resetTare = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_resetTare.setGeometry(QtCore.QRect(160, 40, 111, 28))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setItalic(False)
        self.bttn_resetTare.setFont(font)
        self.bttn_resetTare.setObjectName("bttn_resetTare")
        self.bttn_systemZero = QtWidgets.QPushButton(self.centralwidget)
        self.bttn_systemZero.setGeometry(QtCore.QRect(20, 0, 111, 28))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setItalic(False)
        self.bttn_systemZero.setFont(font)
        self.bttn_systemZero.setObjectName("bttn_systemZero")
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
        self.bttn_stopRun.setText(_translate("MainWindow", "Stop"))
        self.bttn_reset.setText(_translate("MainWindow", "Reset"))
        self.label.setText(_translate("MainWindow", "Span"))
        self.bttn_captureZero.setText(_translate("MainWindow", "Capture Zero"))
        self.bttn_tareScale.setText(_translate("MainWindow", "Tare Scale"))
        self.bttn_setSpan.setText(_translate("MainWindow", "Set Span"))
        self.label_3.setText(_translate("MainWindow", "Duty Cycle"))
        self.label_4.setText(_translate("MainWindow", "Time Elasped:"))
        self.label_5.setText(_translate("MainWindow", "Position"))
        self.label_6.setText(_translate("MainWindow", "Weight"))
        self.bttn_close.setText(_translate("MainWindow", "Close"))
        self.bttn_pollSensors.setText(_translate("MainWindow", "Poll Sensors"))
        self.bttn_setTopBottom.setText(_translate("MainWindow", "Set Top and Bottom"))
        self.lb_topSet.setText(_translate("MainWindow", "Not Set "))
        self.lb_bottomSet.setText(_translate("MainWindow", "Not Set "))
        self.bttn_setDutyCycle.setText(_translate("MainWindow", "Set Duty Cycle"))
        self.bttn_goTop.setText(_translate("MainWindow", "Go Top"))
        self.bttn_goBottom.setText(_translate("MainWindow", "Go Bottom"))
        self.label_8.setText(_translate("MainWindow", "Stop"))
        self.label_7.setText(_translate("MainWindow", "Fast"))
        self.rb_forward.setText(_translate("MainWindow", "FWD"))
        self.rb_reverse.setText(_translate("MainWindow", "REV"))
        self.bttn_stopMotor.setText(_translate("MainWindow", "Stop"))
        self.bttn_resetTare.setText(_translate("MainWindow", "Reset Tare"))
        self.bttn_systemZero.setText(_translate("MainWindow", "System Zero"))

from pyqtgraph import PlotWidget