from numpad import NumPad_Dialog 
from PyQt5.QtWidgets import QDialog

class NumPadPopup(QDialog):
    
    ui = NumPad_Dialog()
    result = None

    def __init__(self):
        super().__init__()
        self.ui.setupUi(self)
        self.ui.lineEdit.setMaxLength(10)
        self.ui.pushButton0.clicked.connect(self.push_button0_clicked)
        self.ui.pushButton1.clicked.connect(self.push_button1_clicked)
        self.ui.pushButton2.clicked.connect(self.push_button2_clicked)
        self.ui.pushButton3.clicked.connect(self.push_button3_clicked)
        self.ui.pushButton4.clicked.connect(self.push_button4_clicked)
        self.ui.pushButton5.clicked.connect(self.push_button5_clicked)
        self.ui.pushButton6.clicked.connect(self.push_button6_clicked)
        self.ui.pushButton7.clicked.connect(self.push_button7_clicked)
        self.ui.pushButton8.clicked.connect(self.push_button8_clicked)
        self.ui.pushButton9.clicked.connect(self.push_button9_clicked)
        self.ui.pushButton_submit.clicked.connect(self.push_buttonsubmit_clicked)
        self.ui.pushButton_erase.clicked.connect(self.pushButton_erase_clicked)
        self.ui.pushButton_clear.clicked.connect(self.pushButton_clear_clicked)  

    def push_button0_clicked(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text() + '0')

    def push_button1_clicked(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text() + '1')

    def push_button2_clicked(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text() + '2')

    def push_button3_clicked(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text() + '3')

    def push_button4_clicked(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text() + '4')

    def push_button5_clicked(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text() + '5')

    def push_button6_clicked(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text() + '6')

    def push_button7_clicked(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text() + '7')

    def push_button8_clicked(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text() + '8')

    def push_button9_clicked(self):
        self.ui.lineEdit.setText(self.ui.lineEdit.text() + '9')

    def push_buttonsubmit_clicked(self):
        
        if self.ui.lineEdit.text() != "":
            self.result = int(self.ui.lineEdit.text())
        else:
            self.result = 0 
        self.accept()

    def pushButton_erase_clicked(self):
        text = self.ui.lineEdit.text()
        textLength = len(text)
        if(textLength):
            newtext = text[:textLength - 1]
            self.ui.lineEdit.setText(newtext)

    def pushButton_clear_clicked(self):
        self.ui.lineEdit.clear()

    def closeEvent(self,event):
        self.Form.setEnabled(True)

