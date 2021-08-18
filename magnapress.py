import sys # We need sys so that we can pass argv to QApplication
import asyncio
from qasync import QEventLoop,asyncSlot
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QTimer, QThread, QObject, QThreadPool
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QDialog, QMessageBox
from mainmenu import Ui_MainWindow 
from calibrate_loadcell import Ui_Calibrate_LoadCell
from calibrate_position import Ui_Calibrate_Position
from calibrate_camera  import Ui_Calibrate_Camera
from freespin import Ui_FreeSpin
from async_client import beagle_client
import pyqtgraph as pg
from image_reader import Visualize_Sample
import faulthandler

class Generic_Window():

    @pyqtSlot()
    def COM_to_Beagle(self,message):
        self.parent().SendSingleCommand(message)

    @pyqtSlot()
    def Return_To_MainMenu(self):
        self.parent().Toggle_Window(self)
        self.parent().showMaximized()
    #    self.parent().Toggle_Window(self.parent()) # Fix later cannot pass parent 


class Calibrate_Camera_Window(QMainWindow,Generic_Window):

    ui = Ui_Calibrate_Camera()
    current_strain = 0

    def __init__(self, parent):
        super(Calibrate_Camera_Window,self).__init__(parent)
        self.ui.setupUi(self)
        self.ui.bttn_BACK_MAIN.clicked.connect(self.Return_To_MainMenu)
        self.ui.bttn_AQUIRE_IMAGES.clicked.connect(self.get_images)
        self.ui.bttn_SETMAX.clicked.connect(self.get_max_profile)
        self.ui.cb_HydrogelSample.stateChanged.connect(self.SwitchSampleType)
        self.ui.bttn_RESAMPLE.clicked.connect(self.get_new_surface_sample)

    @asyncSlot()
    async def get_images(self):
        await self.parent().camera.aquire_images(True,self)
        #await active_process
        
    @asyncSlot()
    async def get_max_profile(self):
        await self.parent().camera.get_profile()

    @asyncSlot()
    async def get_new_surface_sample(self):
        await self.parent().camera.get_newsample()

    @asyncSlot()
    async def SwitchSampleType(self):
        if (self.ui.cb_HydrogelSample.checkState()):
            await self.parent().camera.change_sample_type(True)
        else: 
            await self.parent().camera.change_sample_type(False) 

class Calibrate_LoadCell_Window(QMainWindow,Generic_Window):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    ui = Ui_Calibrate_LoadCell()
    def __init__(self, parent):
        super(Calibrate_LoadCell_Window,self).__init__(parent)
        self.ui.setupUi(self)
        self.ui.bttn_BACK_MAIN.clicked.connect(self.Return_To_MainMenu)
        self.ui.bttn_SYSTEM_ZERO.clicked.connect(
            lambda x: self.COM_to_Beagle("SYSTEM_ZERO")
        )
        self.ui.bttn_RESET_ZERO.clicked.connect(
            lambda x: self.COM_to_Beagle("RESET_ZERO")
        )
        self.ui.bttn_CAPTURE_ZERO.clicked.connect(
            lambda x: self.COM_to_Beagle("CAPTURE_ZERO")
        )
        self.ui.bttn_STAGE_UP_SINGLE.clicked.connect(
            lambda x: self.COM_to_Beagle("STEPPER_UP_SINGLE")
        )
        self.ui.bttn_STAGE_DOWN_SINGLE.clicked.connect(
            lambda x: self.COM_to_Beagle("STEPPER_DOWN_SINGLE") 
        )
        self.ui.bttn_STAGE_UP_MULTI.clicked.connect(
            lambda x: self.COM_to_Beagle("STEPPER_UP_MULTI,"+self.ui.tb_NUMOFSTEPS.text())
        )
        self.ui.bttn_STAGE_DOWN_MULTI.clicked.connect(
            lambda x: self.COM_to_Beagle("STEPPER_DOWN_MULTI,"+self.ui.tb_NUMOFSTEPS.text())
        )
        self.ui.bttn_SET_SPAN.clicked.connect(
            lambda x: self.COM_to_Beagle("SET_SPAN,"+self.ui.tb_SPAN.text())
        )
        self.ui.bttn_TARE_SCALE.clicked.connect(
            lambda x: self.COM_to_Beagle("TARE_SCALE")
        )
        self.ui.bttn_RESET_TARE.clicked.connect(
            lambda x: self.COM_to_Beagle("RESET_TARE")
        )
        self.ui.bttn_GO_TOP.clicked.connect(
            lambda x: self.COM_to_Beagle("SET_TOP")
        )
        self.ui.bttn_GO_BOTTOM.clicked.connect(
            lambda x: self.COM_to_Beagle("GO_BOTTOM")
        )
        self.ui.bttn_POLL_SENSORS.clicked.connect(
            lambda x: self.COM_to_Beagle("POLL_LOAD_SENSOR")
        )  

    def updateLCD(self,val,LCD):
        LCD.display(int(val))


    def process_response(self,message):
        if (message[2] == 'WEIGHT'):
            self.updateLCD(message[3],self.ui.lcd_WEIGHT)
        elif (message[2] == 'SET_TARE'):
            self.updateLCD(message[3],self.ui.lcd_TARE)
        elif (message[2] == 'RESET_TARE'):
            self.updateLCD(0,self.ui.lcd_TARE)
        elif (message[2] == 'RESET_ZERO'):
            pass
        else: 
            print('command not recognized')


class FreeSpin_Window(QMainWindow,Generic_Window):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    ui = Ui_FreeSpin()
    time_array = [0]
    position_array = [0]
    weight_array = [0]
    strain_array = [0]
    pen_weight = None 
    pen_position = None
    pen_strain = None
    position_line = None  
    current_position = 0
    current_force = 0
    current_strain = 0 
    current_time = 0 
    current_timestamp = None 
    active_run = None 


    def __init__(self, parent):
        super(FreeSpin_Window,self).__init__(parent)
        self.ui.setupUi(self)
        self.ui.lcd_TIMER.setDigitCount(12) 
        pen_weight = pg.mkPen(color=(255,255,255), width=5)
        pen_position = pg.mkPen(color=(153, 204, 255), width=5)
        pen_strain = pg.mkPen(color=(0, 0, 204), width=5)
        styles = {'color':'y', 'font-size':'25px'}
        
        self.ui.graph_FORCE.setLabel('left', 'Weight (g)', **styles)
        self.ui.graph_FORCE.setLabel('bottom', 'Time (s)', **styles)
        
        self.ui.graph_POSITION.setLabel('left', 'Angle (-)', **styles)
        self.ui.graph_POSITION.setLabel('bottom', 'Time (s)', **styles)
        
        self.ui.graph_STRAIN.setLabel('left', 'Strain % (-)', **styles)
        self.ui.graph_STRAIN.setLabel('bottom', 'Time (s)', **styles)
        
        self.position_line = self.ui.graph_POSITION.plot([0], [0], pen = pen_position)
        self.weight_line = self.ui.graph_FORCE.plot([0], [0], pen = pen_weight)
        self.strain_line = self.ui.graph_STRAIN.plot([0], [0], pen = pen_strain)
        
        self.ui.sld_DUTYCYCLE.valueChanged.connect(self.SliderValueChange)
        self.ui.bttn_BACK_MAIN.clicked.connect(self.Return_To_MainMenu)
        self.ui.bttn_START.clicked.connect(self._StartRun)
        self.ui.bttn_STOP.clicked.connect(
            lambda x: self.COM_to_Beagle("STOP_RUN")
        )
        self.ui.bttn_RESET.clicked.connect(
            lambda x: self.COM_to_Beagle("RESET_RUN")
        )
        self.ui.bttn_RESUME.clicked.connect(
            lambda x: self.COM_to_Beagle("START_MOTOR")
        )
        self.ui.bttn_PAUSE.clicked.connect(
            lambda x: self.COM_to_Beagle("STOP_MOTOR")
        )
        self.ui.bttn_CHANGE_DIRECTION.clicked.connect(
            lambda x: self.COM_to_Beagle("TOGGLE_DIRECTION")
        )


    @asyncSlot()
    async def _StartRun(self):
        self.active_run = await self.parent().camera.aquire_images(False,self)
        self.COM_to_Beagle("START_RUN")
  
    @asyncSlot()
    async def Stop_Run(self):
        self.COM_to_Beagle("STOP_RUN")
        await self.parent().camera.get_profile()
        self.active_run.cancel() 

    def SliderValueChange(self,num):
        self.motor_duty = self.ui.sld_DUTYCYCLE.value()
        self.COM_to_Beagle("CHANGE_SPEED,"+str(self.motor_duty))
        
    def _Update_Plots(self,time,weight,position,strain):     
        if len(self.time_array) > 100: 
            self.time_array = self.time_array[1:]  # Remove the first y element. 
            self.position_array = self.position_array[1:]    
            self.weight_array = self.weight_array[1:]  
            self.strain_array = self.strain_array[1:]
        self.time_array.append( time )  # Add a new value 1 higher than the last. 
        self.position_array.append( position )  # Add a new random value. 
        self.weight_array.append ( weight )  
        self.strain_array.append ( strain )  
        self.position_line.setData(self.time_array, self.position_array)  
        self.weight_line.setData(self.time_array, self.weight_array)  
        self.strain_line.setData(self.time_array, self.strain_array)

    def _Update_Gui(self,time_stamp,weight): 
        self.ui.lcd_TIMER.display(time_stamp) 
        self.ui.lcd_WEIGHT.display(weight) 
         
    def Receive_Sensor_Data(self,time,timestamp_label,weight,position):
        self.current_position = position
        self.current_time = time
        self.current_force = weight
        self.current_timestamp = timestamp_label
        self._Update_Gui(timestamp_label,weight) 
        self._Update_Plots(time,weight,position,self.current_strain) 
    
    def Emit_Data(self):
        return self.current_time, self.current_timestamp, self.current_force, self.current_position

class Calibrate_Position_Window(QMainWindow,Generic_Window):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    ui = Ui_Calibrate_Position()

    def __init__(self, parent):
        super(Calibrate_Position_Window,self).__init__(parent)
        self.ui.setupUi(self)
        self.ui.bttn_BACK_MAIN.clicked.connect(self.Return_To_MainMenu)
        self.ui.sld_DUTYCYCLE.valueChanged.connect(self.SliderValueChange)
        self.ui.bttn_START.clicked.connect(
            lambda x: self.COM_to_Beagle("START_MOTOR")
        )
        self.ui.bttn_STOP.clicked.connect(
            lambda x: self.COM_to_Beagle("STOP_MOTOR")
        )
        self.ui.bttn_GO_TOP.clicked.connect(
            lambda x: self.COM_to_Beagle("GO_TOP")
        )
        self.ui.bttn_SET_TOP.clicked.connect(
            lambda x: self.COM_to_Beagle("SET_TOP")
        )
        self.ui.bttn_GO_BOTTOM.clicked.connect(
            lambda x: self.COM_to_Beagle("GO_BOTTOM")
        )
        self.ui.bttn_SET_BOTTOM.clicked.connect(
            lambda x: self.COM_to_Beagle("SET_BOTTOM")
        )
    
    def SliderValueChange(self,num):
        self.motor_duty = self.ui.sld_DUTYCYCLE.value()
        self.COM_to_Beagle("CHANGE_SPEED,"+str(self.motor_duty))

    def Update_Position_LCD(self,num):
        p = float((int(num) + 1) % 4096)
        a = float(p*360/4096)
        self.ui.lcd_position.display(a)

class MainWindow(QMainWindow):

    ui = Ui_MainWindow()
    loop = None
    camera = None 
    beagle = None 

    def __init__(self,loop=None, parent=None):	
        super().__init__()
        self.loop = loop or asyncio.get_event_loop()
        self.ui.setupUi(self)
        self.ui.bttn_EM100.clicked.connect(
                lambda x: self.SendSingleCommand("hey hey")
        )
        self.ui.bttn_CALIBRATE_LC.clicked.connect(
                lambda x: self.Toggle_Window(self.loadcell_window)
        ) 
        self.ui.bttn_CALIBRATE_P.clicked.connect(
                lambda x: self.Toggle_Window(self.position_window)
        )
        self.ui.bttn_TIME_LAPSE.clicked.connect(
                lambda x: self.Toggle_Window(self.freespin_window)
        )
        self.ui.bttn_CALIBRATE_C.clicked.connect(
                lambda x: self.Toggle_Window(self.camera_window)
        )
        self.loadcell_window = Calibrate_LoadCell_Window(self)
        self.freespin_window = FreeSpin_Window(self)
        self.position_window = Calibrate_Position_Window(self)
        self.camera_window = Calibrate_Camera_Window(self)
        self.camera = Visualize_Sample()
        self.beagle = beagle_client()
        self.beagle.capture_stream(self.loop,self)

    @asyncSlot()
    async def SendSingleCommand(self,command):
        print('attempting to send message')
        await self.beagle.tcp_echo_client(command,self.loop,self)

    @pyqtSlot(str)
    def RecieveResponse(self,message):
        message = message.split(',')
        print('back in form with message for :',message[0])
        if(message[1] == "LOADCELL"):
            self.loadcell_window.process_response(message) 
        elif (message[1] == "POSITON"): 
            self.position_window.process_response(message)
        elif (message[1] == "CAMERA"): 
            self.position_window.process_response(message)
        elif (message[1] == "FREESPIN"): 
            self.freespin_window.process_response(message)

    @pyqtSlot(str)
    def RecieveStream(self,message):
        message = message.split(',')
        del message[-1]
        if (len(message) == 1):
            self.position_window.Update_Position_LCD(message[0])      
        if (len(message) == 4):
            self.freespin_window.Receive_Sensor_Data(float(message[0]),message[1], int(message[2]),int(message[3]))

    @pyqtSlot()
    def Launch_Calibration_LoadCell(self):
        self.hide()
        self.loadcell_window.showMaximized() 

    def Toggle_Window(self,window):
        if window.isVisible():
            window.hide()
        else:
            window.showMaximized()

    @pyqtSlot()
    def Launch_Calibration_Position(self):
        self.hide()
        self.position_window.showMaximized() 

    @pyqtSlot()
    def Launch_FreeSpin(self):
        self.hide()
        self.freespin_window.showMaximized() 

    @pyqtSlot()
    def Launch_Calibration_Camera(self):
        self.hide()
        self.camera_window.showMaximized() 

def main():
    app = QApplication(sys.argv) # A new instance of QApplicatio0n
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    screen = MainWindow(loop)
    screen.showMaximized()
    with loop: 
        loop.run_forever()

if __name__ == '__main__':
    main()
