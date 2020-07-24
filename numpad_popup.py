from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel,QWidget
from numpad import NumPad_Dialog

class numpadPopup(QWidget):
    
    def __init__(self):
        super().__init__()
        pad = NumPad_Dialog()
        pad.setupUi(pad)
        self.pad.lineEdit.setMaxLength(10)
        self.pushButton0.clicked.connect(self.push_button0_clicked)
        self.pushButton1.clicked.connect(self.push_button1_clicked)
        self.pushButton2.clicked.connect(self.push_button2_clicked)
        self.pushButton3.clicked.connect(self.push_button3_clicked)
        self.pushButton4.clicked.connect(self.push_button4_clicked)
        self.pushButton5.clicked.connect(self.push_button5_clicked)
        self.pushButton6.clicked.connect(self.push_button6_clicked)
        self.pushButton7.clicked.connect(self.push_button7_clicked)
        self.pushButton8.clicked.connect(self.push_button8_clicked)
        self.pushButton9.clicked.connect(self.push_button9_clicked)
        self.pushButton_submit.clicked.connect(self.pushButton_submit_clicked)
        self.pushButton_erase.clicked.connect(self.pushButton_erase_clicked)
        self.pushButton_clear.clicked.connect(self.pushButton_clear_clicked)

    def push_button0_clicked(self):
        self.lineEdit.setText(self.lineEdit.text() + '0')

    def push_button1_clicked(self):
        self.lineEdit.setText(self.lineEdit.text() + '1')

    def push_button2_clicked(self):
        self.lineEdit.setText(self.lineEdit.text() + '2')

    def push_button3_clicked(self):
        self.lineEdit.setText(self.lineEdit.text() + '3')

    def push_button4_clicked(self):
        self.lineEdit.setText(self.lineEdit.text() + '4')

    def push_button5_clicked(self):
        self.lineEdit.setText(self.lineEdit.text() + '5')

    def push_button6_clicked(self):
        self.lineEdit.setText(self.lineEdit.text() + '6')

    def push_button7_clicked(self):
        self.lineEdit.setText(self.lineEdit.text() + '7')

    def push_button8_clicked(self):
        self.lineEdit.setText(self.lineEdit.text() + '8')

    def push_button9_clicked(self):
        self.lineEdit.setText(self.lineEdit.text() + '9')

    def push_button_submit_clicked(self):
        self.hide()
        if self.lineEdit.text() != "":
            self.numberSet.setText(self.constantText + self.lineEdit.text())
        self.Form.setEnabled(True)

        if self.callOnSubmit != None:
            self.callOnSubmit(*self.args)

    def pushButton_erase_clicked(self):
        text = self.lineEdit.text()
        textLength = len(text)
        if(textLength):
            newtext = text[:textLength - 1]
            self.lineEdit.setText(newtext)

    def pushButton_clear_clicked(self):
        self.lineEdit.clear()

    def closeEvent(self,event):
        self.Form.setEnabled(True)

