import asyncio
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QDialog, QMessageBox
from qasync import QEventLoop,asyncSlot

class Data_Link(QObject):
    transmission = pyqtSignal(str)

class beagle_client():

    @asyncSlot()
    async def tcp_echo_client(self,message, loop,form):
        response_link = Data_Link()
        response_link.transmission.connect(form.RecieveResponse)
        port = 7777
        server = 'beaglebone.local'
        # loopback 
        reader, writer = await asyncio.open_connection(server,port,loop=loop)
        print('Send: %r' % message)
        writer.write(message.encode())
        if (message not in []):
            data = await reader.read(100)
            val = data.decode()
            #print('Received: %r' % val)
            val = message + ',' + val         
            print('Close the socket')
            writer.close()
            print('emitting value:',val)
            response_link.transmission.emit(val)
   
    @asyncSlot()
    async def capture_stream(self,loop,form):
        data_link = Data_Link()
        data_link.transmission.connect(form.RecieveStream)
        port = 7778
        server = 'beaglebone.local'
        print('Connecting to server {} on port {} '.format(server,port))
        try: 
            # loopback 
            reader, writer = await asyncio.open_connection(server,port,loop=loop)
        except ConnectionRefusedError:
            print('Connection to server {} on port {} failed!'.format(server,port))
        else: 
            print('connected successfully')
        while True:
            
            try:
                data = await reader.readuntil(separator=b'\r')
            except asyncio.IncompleteReadError:        
                print('stream buffer empty')
                continue
            else:
                #print( f'received {len(data)} bytes' )
                val = data.decode()
                data_link.transmission.emit(val)

