import sys # We need sys so that we can pass argv to QApplication
import asyncio
from uio.ti.icss import Icss
from uio.ti.pwmss import Pwmss
from ctypes import c_uint32 as uint32, c_uint8 as uint8, c_uint16 as uint16, c_uint64 as uint64, c_char as char, c_int32 as int32, Structure
from ctypes import sizeof as c_sizeof
from pathlib import Path
from time import sleep 

class Message( Structure ):
    _fields_ = [
            ("id",uint32),
            ("timestamp", uint32),   # time in cycles
            ("position", uint32), # in encoder pulsest 1140 per Revo 
            ("force", int32),  # in grams
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
    NUM_MSGS = None
    ddr_layout = None
    shmem = None 
    msgbuf = None 
    ddr_widx = None 
    ddr_layout = None 
    rdix = 0 
    wdix = 0
    lastid = 0 
    timestamp_cycles = 0 

    def __init__(self):
        super().__init__()
        #setup_pruss
        self.pruss.initialize()
        self.period = round( 100e6 / self.divider / self.frequency )
        self.top_motor_speed = self.period
        self.pruss.uart.initialize(baudrate = 460800)
        self.position = self.pruss.dram0.map( uint32 )
        self.motor = Pwmss( "/dev/uio/pwmss1" ).pwm
        self.motor.initialize(self.period,self.divider)
        self.current_motor_speed = 0
        #self.stepper_MS1 = Gpio('P8_10')
        self.stepper_MS2 = Gpio('MS2')
        self.stepper_enable = Gpio('enable')
        self.stepper_direction = Gpio('stepper_dir')
        self.motor_direction = Gpio('motor_dir')
        self.stepper_step = Gpio('step')
        self.stepper_direction.set_value( 0 ) 
        self.motor_direction.set_value( 1)
        self.stepper_step.set_value( 0 ) 
        self.stepper_enable.set_value( 0 )
        self.stepper_delay = 1000/1000000.0
        self.stepper_multi_delay= 1000/1000000.0
        self.data_queue = asyncio.Queue() 
        self.stop_active_run = False 
        self.current_position = 9999
        self.shut_down = False 
        self.ddr = self.pruss.ddr 
        self.core_0.load('decoder.bin')
        self.core_0.run()
        self.core_1.load('stream.out')
        # if you don't want the ringbuffer at the start of the ddr region, specify offset here
        self.MSGBUF_OFFSET = 0
        # you can use a fixed ringbuffer size:
        #NUM_MSGS = 1024
        # or you can scale the ringbuffer to fit the size of the ddr region:
        self.NUM_MSGS = ( self.ddr.size - self.MSGBUF_OFFSET - c_sizeof( uint16 ) ) // c_sizeof( Message )
        self.NUM_MSGS = min( self.NUM_MSGS, 65535 )  # make sure number of messages fits in u16
        # map shared memory variables
        self.ddr_layout = self.core_1.map( DDRLayout, 0x10000 )
        self.shmem = self.core_1.map( SharedVars, 0x10100 )
        self.msgbuf = self.ddr.map( Message * self.NUM_MSGS, self.MSGBUF_OFFSET )
        self.ddr_widx = self.ddr.map( uint16, self.MSGBUF_OFFSET + c_sizeof( self.msgbuf ) )
        # inform pru about layout of shared ddr memory region
        self.ddr_layout.msgbuf       = self.ddr.address + self.MSGBUF_OFFSET
        self.ddr_layout.num_msgs     = self.NUM_MSGS
        self.ddr_layout.msg_size     = c_sizeof( Message )

    def _TrimMessage(self,message,start,finish):
        return message[start-1:finish-1]
   

    def _OpenCalibration(self):
        print("open calibration")
        self.pruss.uart.io.write(b'CE\r')
        response = self.pruss.uart.io.readline(newline =b'\r').decode('ascii')
        calib_num = int(self._TrimMessage(response,3,len(response)))
        self.pruss.uart.io.write(bytes('CE ' + str(calib_num) + '\r','ascii'))
        response = self.pruss.uart.io.readline(newline =b'\r').decode("ascii")
        print(response)

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

    async def _StartRun(self):
        
        self.stop_active_run = False 
        # local copies of read-pointer and write-pointer
        self.ridx = 0
        self.widx = 0

        # initialize pointers in shared memory
        self.shmem.ridx = self.ridx
        self.ddr_widx.value = self.widx

        # ready, set, go!
        print('lauching core 1')
        self.pruss.ecap.pwm.initialize( 2**32 )
        self.core_1.run()
        try:
            while (self.stop_active_run == False and self.shut_down == False):
                await self.recv_messages()
                await self.check_core()
                await asyncio.sleep( 0 )
        except KeyboardInterrupt:
            pass

        finally:
            print( '', flush=True )
            self.core_1.halt()
            self.pruss.uart.io.write( b'FFV\r', discard=True, flush=True )  # interrupt continuous transmission
            await asyncio.sleep( 0.01 )  # make sure that response has been received
            self.pruss.uart.io.discard()  # discard response            
            self.pruss.uart.io.close() 
            self.pruss.uart.initialize(baudrate = 460800)
    
    async def _StopRun(self):
        self.stop_active_run = True 
        await asyncio.sleep( 0 ) 

    async def _ShutDown(self):
        self.shut_down = True 
        await asyncio.sleep( 0 ) 

    def _ChangeDirection(self):
        print('Executing direction change')
        val = self.motor_direction.get_value() 
        if (int(val) == 0):
            self.motor_direction.set_value( 1 ) 
        else: 
            self.motor_direction.set_value( 0 ) 

    def _ChangeMotorSpeed(self,value):
        try:
            self.current_motor_speed = int(self.period*float(int(value)/100))
        except:
            print('Command Failed')
        else:
            return "New Speed is " + str(self.current_motor_speed)


    async def _SetTop(self):
        self.motor.ld_compare_a = int(self.period/15)
        self.motor.ld_compare_b = 0
        self.core_1.load('find_max.out')
        self.core_1.run()
        counter = 0
        max_weight = 0
        max_position = 0
        prev_weight = 0
        max_counter = 0
        desc_counter = 0
        print('getting started') 
        while(self.shut_down == False):
            position = self.pruvars.position
            weight = self.pruvars.force
            print("Counter {} Max_Counter {} Descreasing Counter {}".format(counter,max_counter,desc_counter))
            print("Current Weight {} Max Weight {}".format(weight,max_weight))
            if (weight >= prev_weight):
                desc_counter = 0
                print("weight increaseing new max weight set")
                if (weight > max_weight):
                    max_weight = weight
                    max_position = (position + 1) % 4096
                    max_counter = 0
                else:
                    print("weight increasing but below max weight")
                    max_counter = max_counter + 1
            else:
                max_counter = max_counter + 1
                if (desc_counter > 3):
                    print("Weight dscresing for too long changing direction")
                    self._ChangeDirection()
                    desc_counter = 0
                else:
                    print("Weight descrsing but not long enough to give up this way")
                    desc_counter = desc_counter + 1
            if (max_counter > 30 or counter > 500):
                break
            counter = counter + 1
            prev_weight = weight
            await asyncio.sleep(0.1)
            val = str(position) + ',' + str(weight)
            await self.data_queue.put(val)

        self.pruss.uart.io.write( b'FFV\r', discard=True, flush=True )  # interrupt continuous transmission
        sleep( 0.1 )  # make sure that response has been received
        self.pruss.uart.io.discard()  # discard response
        self.core_1.halt()
        print('Finished')

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
            await self._StartRun()
            result = 'OK' #istr(self._StartRun())
            term1 = 'FREESPIN,'
            term2 = 'STATUS,'
            val = term1.encode("ascii")+term2.encode("ascii")+result.encode("ascii")
        elif (message[0] == "STOP_RUN"):
            await self._StopRun()
            result = 'OK' #istr(self._StartRun())
            term1 = 'POSITION,'
            term2 = 'STATUS,'
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
        elif(message[0] == "SET_TOP"):
            await self._SetTop() 
            term1 = 'LOADCELL,'
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


    async def check_core(self):
        
        if not self.core_1.halted:
            return
        if self.core_1.state.crashed:
            msg = f'core crashed at pc={self.core_1.pc}'
        elif self.shmem.abort_file == 0:
            msg = f'core halted at pc={self.core_1.pc}'
        else:
            # FIXME figure out better way to read C-string from PRU memory
            abort_file = self.core_1.read( char * 32, self.shmem.abort_file ).value
            abort_file = abort_file.decode("ascii")
            msg = f'core aborted at pc={self.core_1.pc} ({abort_file}:{self.shmem.abort_line})'

        # dump some potentially interesting information:
        msg += f'\n   ridx       = {self.ridx}'
        msg += f'\n   shmem.ridx = {self.shmem.ridx}'
        msg += f'\n   ddr_widx   = {self.ddr_widx.value}'

        exit( msg )

        astid = 0

    async def recv_messages(self):

        # read updated write-pointer
        self.widx = self.ddr_widx.value
        assert self.widx < self.NUM_MSGS  # sanity-check

        position = 0
        force = 0 
        timestamp = 0
        # process messages
        
        while self.ridx != self.widx:
            # note: it may be faster to copy a batch of messages from shared memory
            # instead of directly accessing individual messages and their fields.
            msg = self.msgbuf[ self.ridx ]
            # sanity-check that message id increments monotonically
            self.lastid = ( self.lastid + 1 ) & 0xffffffff
            assert msg.id == self.lastid
            # get 32-bit timestamp (in cycles) from message and unwrap it:
            self.timestamp_cycles += ( msg.timestamp - self.timestamp_cycles ) & 0xfffffff    
            # convert to timestamp in seconds    
            timestamp = self.timestamp_cycles / 200e6 * 10E4   
            position = msg.position    
            force = msg.force    
            val = [timestamp, force, position]
            self.data_queue.put_nowait(val)
            # consume message and update read pointe    
            del msg  
            # direct access to message forbidden beyond this poin    
            self.ridx += 1    
            if (self.ridx == self.NUM_MSGS):
                self.ridx = 0      
            self.shmem.ridx = self.ridx
            #update user interface
            print(f'\ridx=0x{self.ridx:04x} id=0x{self.lastid:08x} time={timestamp:5.3f} position={position} force={force:08d}', end='', flush=True ) 
    
    
    async def data_emitter(self,reader, writer):
        print('emitting data active') 
        delay = 0.01
        terminator = bytes("\r",'ascii')
        seperator = bytes(',','ascii')
        while (self.shut_down != True):
            val_list = []
            data = bytes('','ascii') 
            if not (self.data_queue.empty()): 
                val_list = self.data_queue.get_nowait()
                for i in range (0,len(val_list)):
                    val = str(val_list[i]).encode('ascii')
                    data += val + seperator
                data += terminator 
                writer.write(data)
                await writer.drain()
                delay = 0.01
            await asyncio.sleep(0.0001)#delay)
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
            #self.loop.create_task(self.check_position())

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
