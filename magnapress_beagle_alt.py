import sys # We need sys so that we can pass argv to QApplication
import asyncio
from uio.ti.icss import Icss
from uio.ti.pwmss import Pwmss
from ctypes import c_uint32 as uint32, c_uint8 as uint8, c_uint16 as uint16, c_uint64 as uint64, c_char as char, c_int32 as int32, Structure
from pathlib import Path
from time import sleep 


class Message( Structure ):
    _fields_ = [
            ("time", uint32),   # time in cycles
            ("position", uint32), # in encoder pulsest 1140 per Revo 
            ("force", int32),  # in grams i
            ("duty_cycle", uint8), # duty cycle 0%-100%
            ("wave_shape",uint8), # wave shape input  

        ]

# used to communicate ddr layout to C program
class DDRLayout( Structure ):
    _fields_ = [
            ( 'msgbuf',      uint32 ),
            ( 'num_msgs',    uint16 ),
            ( 'msg_size',    uint16 ),
        ]

# volatile variables in pruss shared memory
class SharedVars( Structure ):
    _fields_ = [
            ( 'abort_file', uint32 ),
            ( 'abort_line', uint32 ),

            ( 'ridx',       uint16 ),
        ]

class Gpio:
    def __init__( self, name ):
        self.name = name
        self._value_path = Path( '/dev/gpio', name, 'value' )
 
    def get_value( self ):
        return int( self._value_path.read_text() )
 
    def set_value( self, value ):
        self._value_path.write_text( str( value ) )

class PruVars( Structure ):
    _fields_ = [
            ("position", uint32), # in encoder pulsest 1140 per Revo 
            ("force", int32),  # in grams i
            ("duty_cycle", uint8), # duty cycle 0%-100%
            ("wave_shape",uint8), # wave shape input  
        ]

class async_server():

    loop = None
    coro = None
    server = None 
    pruss = Icss( "/dev/uio/pruss/module" )
    core_0 = pruss.core0
    core_1 = pruss.core1
    frequency= 10000
    period = None
    divider = 1
    position = None
    weight = None
    pruvars = None
    top_motor_speed = period
    current_motor_speed = None
    maxloadposition = None
    minloadposition = None
    _last_timestamp_cycles = 0
    stepper_step = None 
    stepper_direction = None 
    server1 = None
    server2 = None 
    coro1 = None 
    coro2 = None 
    data_queue = None 
    active_run = None 
    shut_down = None 

    def __init__(self):
        super().__init__()
        #setup_pruss
        self.period = round( 100e6 / self.divider / self.frequency )
        self.top_motor_speed = self.period
        self.pruss.uart.initialize(baudrate = 460800)
        self.core_0.load('decoder.bin')
        self.core_0.run()
        self.core_1.load('stream.out')
        self.position = self.pruss.dram0.map( uint32 )
        self.pruvars = self.pruss.dram2.map( PruVars )
        self.motor = Pwmss( "/dev/uio/pwmss1" ).pwm
        self.motor.initialize(self.period,self.divider)
        self.current_motor_speed = 0
        #self.stepper_MS1 = Gpio('P8_10')
        self.stepper_MS2 = Gpio('MS2')
        self.stepper_enable = Gpio('enable')
        self.stepper_direction = Gpio('direction')
        self.stepper_step = Gpio('step')
        self.stepper_direction.set_value( 0 ) 
        self.stepper_step.set_value( 0 ) 
        self.stepper_enable.set_value( 0 )
        self.stepper_delay = 1000/1000000.0
        self.stepper_multi_delay= 1000/1000000.0
        self.data_queue = asyncio.Queue() 
        self.active_run = False 
        self.current_position = 9999
        self.shut_down = False 

    def _timestamp_ns(self):
        """Returns the current timestamp in nanoseconds (integer)"""
        return self.timestamp_cycles() * 5

    def _timestamp_seconds(self):
        """Returns the current timestamp in seconds (floating-point)"""
        return self.timestamp_cycles() / 200e6

    def _TrimMessage(self,message,start,finish):
        return message[start-1:finish-1]

    async def check_position(self):
        delay = 0.01 
        while (self.active_run == False and self.shut_down == False):
            if (self.current_position != self.position.value):
                self.current_position = self.position.value 
                await self.data_queue.put([self.current_position])
                delay = 0.01 
            await asyncio.sleep(delay) 
            if (delay <= 0.5):
                delay += 0.05

    def _OpenCalibration(self):
        print("open calibration")
        self.pruss.uart.io.write(b'CE\r')
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        calib_num = int(self._TrimMessage(response,3,len(response)))
        self.pruss.uart.io.write(bytes('CE ' + str(calib_num) + '\r','ascii'))
        response = self.pruss.uart.io.readline(newline =b'\r').decode("ascii")
        print(response)

    def _ChangeDirection(self):
        if (self.ui.rb_forward.isChecked()):
            self.ui.rb_reverse.setChecked(True)
            #self.RevRadioButton_on_click(self.motor.ld_compare_a,self.motor.ld_compare_b)
        else:
            self.ui.rb_forward.setChecked(True)
            #self.FwdRadioButton_on_click(self.motor.ld_compare_a,self.motor.ld_compare_b)

    def _TareScale(self):
        try:
            self.pruss.uart.io.write(b'ST\r')
        except:
            print('Command Failed')
        
        else:
            return self.pruss.uart.io.readline(newline =b'\r').decode('ascii')

    def _ResetTare(self):
        try:
            self.pruss.uart.io.write(b'RT\r')
        except:
            print('Command Failed')
        
        else:
            return self.pruss.uart.io.readline(newline =b'\r').decode('ascii')

    def _SystemZero(self):
        try: 
            self.pruss.uart.io.write(b'SZ\r')
        except:
            print('Command Failed')
        
        else:
            return self.pruss.uart.io.readline(newline =b'\r').decode('ascii')

    def _CaptureZero(self):
        try:
            self._OpenCalibration()
            self.pruss.uart.io.write(b'CZ\r')
        except:
            print('Command Failed')
        
        else:
            return self.pruss.uart.io.readline(newline =b'\r').decode('ascii')

    def _SetSpan(self,value):
        try:
            self.pruss.uart.io.write(b'CG\r')
            response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
            self._OpenCalibration()
            self.pruss.uart.io.write(bytes('CG ' + str(value) + '\r','ascii'))
            response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
            self._OpenCalibration()
            self.pruss.uart.io.write(b'CS\r')
            response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        except:
            print('Command Failed')
        
        else:
            return response

    def _StopMotor(self):
        try:
            self.motor.ld_compare_a = 0
            self.motor.ld_compare_b = 0 
        except:
            print('Command Failed')
        
        else:
            return "OK"

    def _StartMotor(self):
        self.motor.ld_compare_a = int(self.current_motor_speed)
        self.motor.ld_compare_b = int(self.current_motor_speed) 

    def _StartRun(self):
        # if you don't want the ringbuffer at the start of the ddr region, specify offset here
        MSGBUF_OFFSET = 0

        # you can use a fixed ringbuffer size:
        #NUM_MSGS = 1024
        # or you can scale the ringbuffer to fit the size of the ddr region:
        NUM_MSGS = ( ddr.size - MSGBUF_OFFSET - ctypes.sizeof( u16 ) ) // ctypes.sizeof( Message )
        NUM_MSGS = min( NUM_MSGS, 65535 )  # make sure number of messages fits in u16

        # map shared memory variables
        ddr_layout = core.map( DDRLayout, 0x10000 )
        shmem = core.map( SharedVars, 0x10100 )
        msgbuf = ddr.map( Message * NUM_MSGS, MSGBUF_OFFSET )
        ddr_widx = ddr.map( u16, MSGBUF_OFFSET + ctypes.sizeof( msgbuf ) )

        # inform pru about layout of shared ddr memory region
        ddr_layout.msgbuf       = ddr.address + MSGBUF_OFFSET
        ddr_layout.num_msgs     = NUM_MSGS
        ddr_layout.msg_size     = ctypes.sizeof( Message )

        # local copies of read-pointer and write-pointer
        ridx = 0
        widx = 0

        # initialize pointers in shared memory
        shmem.ridx = ridx
        ddr_widx.value = widx

        # ready, set, go!
        
        core_1.run()
        try:
            while True:
                recv_messages()
                check_core()

                asynicio.sleep( 0.01 )

        except KeyboardInterrupt:
            pass

        finally:
            print( '', flush=True )
            core_1.halt()

    def _ChangeMotorSpeed(self,value):
        try:
            self.current_motor_speed = int(self.period*float(int(value)/100))
        except:
            print('Command Failed')
        
        else:
            return "New Speed is " + str(self.current_motor_speed)

    def _Step_Up_Single(self):
        try:
            self.stepper_enable.set_value( 1 )
            self.stepper_direction.set_value( 1 )
            self.stepper_step.set_value( 1 )
            self.stepper_step.set_value( 0 )
            asyncio.sleep(self.stepper_delay)
        except:
            print('Command Failed')
        
        else:
            self.stepper_enable.set_value( 0 )
            return "OK"

    def _Step_Down_Single(self):
        try:
            self.stepper_enable.set_value( 1 )
            self.stepper_direction.set_value( 0 )
            self.stepper_step.set_value( 1 )
            self.stepper_step.set_value( 0 )
            asyncio.sleep(self.stepper_delay)
        except:
            print('Command Failed')
        
        else:
            self.stepper_enable.set_value( 0 )
            return "OK"

    def _Step_Up_Multi(self,num_of_steps):
        try:
            self.stepper_enable.set_value( 1 )
            self.stepper_direction.set_value( 1 )
            for i in range(0,num_of_steps):
                self.stepper_step.set_value( 1 )
                self.stepper_step.set_value( 0 )
                asyncio.sleep(self.stepper_multi_delay)
        except:
            print('Command Failed')
        
        else:
            self.stepper_enable.set_value( 0 )
            return "OK"

    def _Step_Down_Multi(self,num_of_steps):
        try:
            self.stepper_enable.set_value( 1 )
            self.stepper_direction.set_value( 0 )
            for i in range(0,num_of_steps):
                self.stepper_step.set_value( 1 )
                self.stepper_step.set_value( 0 )
                asyncio.sleep(self.stepper_multi_delay)
        except:
            print('Command Failed')
        
        else:
            self.stepper_enable.set_value( 0 )
            return "OK"

    def _Poll_Load_Sensor(self):
        try:
            self.pruss.uart.io.write(b'GN\r')
            response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        except:
            print('Command Failed')
        
        else:
            return  int(self._TrimMessage(response,2,len(response)))

    def _Poll_PositionSensor(self):
        return (self.position.value + 1) % 4096

    def _Poll_Timer(self):
        pass 


    async def handle_echo(self,reader, writer):
        print('processing connection') 
        data = await reader.read(100)
        message = data.decode()
        message = message.split(",")
        addr = writer.get_extra_info('peername')
        print("Received %r from %r" % (message, addr))
        if (message[0] == "START_RUN"):
            result = str(self._StartRun())
            term1 = 'FREESPIN'
            term2 = 'STATUS'
            val = term1.encode("ascii")+term2.encode("ascii")+result.encode("ascii")
        elif (message[0] == "START_MOTOR"):
            result = str(self._StartMotor())
            term1 = 'POSITION,'
            term2 = 'STATUS,'
            val = term1.encode("ascii")+term2.encode("ascii")+result.encode("ascii")
        elif (message[0] == "STOP_MOTOR"):
            result = str(self._StopMotor())
            term1 = 'POSITION,'
            term2 = 'STATUS,'
            val = term1.encode("ascii")+term2.encode("ascii")+result.encode("ascii")
        elif (message[0] == "CHANGE_SPEED"):
            result = str(self._ChangeMotorSpeed(message[1]))
            term1 = 'POSITION,'
            term2 = 'STATUS,'
            val = term1.encode("ascii")+term2.encode("ascii")+result.encode("ascii")
        elif(message[0] == "SYSTEM_ZERO"):
            result = str(self._SystemZero())
            term1 = 'LOADCELL,'
            term2 = 'STATUS,'
            val = term1.encode("ascii")+term2.encode("ascii")+result.encode("ascii")
        elif(message[0] == "CAPTURE_ZERO"):
            result = str(self._CaptureZero())
            term1 = 'LOADCELL,'
            term2 = 'STATUS,'
            val = term1.encode("ascii")+term2.encode("ascii")+result.encode("ascii")
        elif(message[0] == "SET_SPAN"):
            result = str(self._SetSpan(int(message[1])))
            term1 = 'LOADCELL,'
            term2 = 'STATUS,'
            val = term1.encode("ascii")+term2.encode("ascii")+result.encode("ascii")
        elif(message[0] == "STEPPER_UP_MULTI"):
            result = str(self._Step_Up_Multi(int(message[1])))
            term1 = 'POSITION,'
            term2 = 'STATUS,'
            val = term1.encode("ascii")+term2.encode("ascii")+result.encode("ascii")
        elif(message[0] == "STEPPER_DOWN_MULTI"):
            result = str(self._Step_Down_Multi(int(message[1])))
            term1 = 'POSITION,'
            term2 = 'STATUS,'
            val = term1.encode("ascii")+term2.encode("ascii")+result.encode("ascii")
        elif(message[0] == "STEPPER_UP_SINGLE"):
            result = str(self._Step_Up_Single())
            term1 = 'POSITION,'
            term2 = 'STATUS,'
            val = term1.encode("ascii")+term2.encode("ascii")+result.encode("ascii")
        elif(message[0] == "STEPPER_DOWN_SINGLE"):
            result = str(self._Step_Down_Single())
            term1 = 'POSITION,'
            term2 = 'STATUS,'
            val = term1.encode("ascii")+term2.encode("ascii")+result.encode("ascii")
        elif(message[0] == "TARE_SCALE"):
            result = str(self._TareScale())
            term1 = 'POSITION,'
            term2 = 'STATUS,'
            val = term1.encode("ascii")+term2.encode("ascii")+result.encode("ascii")
        elif(message[0] == "RESET_TARE"):
            result = str(self._ResetTare())
            term1 = 'POSITION,'
            term2 = 'STATUS,'
            val = term1.encode("ascii")+term2.encode("ascii")+result.encode("ascii")
        elif(message[0] == "GO_TOP"):
            print('trying to go to top')
            term1 = 'POSITION,'
            term2 = 'STATUS,'
            term3 = 'OK'
            val = term1.encode("ascii")+term2.encode("ascii")+term3.encode("ascii")
        elif(message[0] == "GO_BOTTOM"):
            print('trying to go to bottom')
            term1 = 'POSITION,'
            term2 = 'STATUS,'
            term3 = 'OK'
            val = term1.encode("ascii")+term2.encode("ascii")+term3.encode("ascii")
        elif (message[0] == "POLL_LOAD_SENSOR"):
            print('trying to read load sensors')
            val = str(self._Poll_Load_Sensor())
            term1 = 'LOADCELL,'
            term2 = 'WEIGHT,'
            val = term1.encode("ascii")+term2.encode("ascii")+val.encode("ascii")
        writer.write(val)
        await writer.drain()
        print("Send: %r" % val)
        print("Close the client socket")
        writer.close()


    def check_core():
        if not core.halted:
            return

        if core.state.crashed:
            msg = f'core crashed at pc={core.pc}'
        elif shmem.abort_file == 0:
            msg = f'core halted at pc={core.pc}'
        else:
            # FIXME figure out better way to read C-string from PRU memory
            abort_file = core.read( ctypes.c_char * 32, shmem.abort_file ).value
            abort_file = abort_file.decode("ascii")
            msg = f'core aborted at pc={core.pc} ({abort_file}:{shmem.abort_line})'

        # dump some potentially interesting information:
        msg += f'\n   ridx       = {ridx}'
        msg += f'\n   shmem.ridx = {shmem.ridx}'
        msg += f'\n   ddr_widx   = {ddr_widx.value}'

        exit( msg )

        lastid = 0

    def recv_messages():
        global ridx, widx, lastid

        # read updated write-pointer
        widx = ddr_widx.value
        assert widx < NUM_MSGS  # sanity-check

        # process messages
        while ridx != widx:
            # note: it may be faster to copy a batch of messages from shared memory
            # instead of directly accessing individual messages and their fields.
            msg = msgbuf[ ridx ]

            # sanity-check that message id increments monotonically
            lastid = ( lastid + 1 ) & 0xffffffff
            assert msg.id == lastid

            # consume message and update read pointer
            del msg  # direct access to message forbidden beyond this point
            ridx += 1
            if ridx == NUM_MSGS:
                ridx = 0
            shmem.ridx = ridx

            # update user interface
            print( f'\ridx=0x{ridx:04x} id=0x{lastid:08x} ', end='', flush=True )
    
    
    async def data_emitter(self,reader, writer):
        print('emitting data active') 
        delay = 0.01
        terminator = bytes("\r",'ascii')
        seperator = bytes(',','ascii')
        while (self.shut_down != True):
            val_list = []
            data = bytes('','ascii') 
            if not (self.data_queue.empty()): 
                val_list = await self.data_queue.get()
                for i in range (0,len(val_list)):
                    val = str(val_list[i]).encode('ascii')
                    data += val + seperator
                data += terminator 
                writer.write(data)
                await writer.drain()
                delay = 0.01
            await asyncio.sleep(delay)
            if (delay <= 0.1):
                delay += 0.01
        print("Close the client socket")
        writer.close()          

    def launch_server(self):
        self.loop = asyncio.get_event_loop()
        #self.coro1 = asyncio.start_server(self.handle_echo, '127.0.0.1', 7777, loop=self.loop)
        self.coro1 = asyncio.start_server(self.handle_echo,None, 7777, loop=self.loop)
        self.server1 = self.loop.run_until_complete(self.coro1)
        print('Serving on {}'.format(self.server1.sockets[0].getsockname()))
        
        self.coro2 = asyncio.start_server(self.data_emitter,None, 7778, loop=self.loop)
        #self.coro2 = asyncio.start_server(self.data_emitter, '127.0.0.1', 7778, loop=self.loop)
        self.server2 = self.loop.run_until_complete(self.coro2)
        print('Serving on {}'.format(self.server2.sockets[0].getsockname()))
        # Serve requests until Ctrl+C is pressed
        try:
            self.loop.create_task(self.check_position())
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            # Close the server
            self.server.close()
            self.loop.run_until_complete(self.server.wait_closed())
            self.loop.close()

def main():
    beaglebone = async_server()
    beaglebone.launch_server()

if __name__ == '__main__':
    main()
