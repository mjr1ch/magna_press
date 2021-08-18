#!/usr/bin/python3

from uio.utils import fix_ctypes_struct
from uio.ti.icss import Icss
import ctypes
from ctypes import c_uint32 as u32, c_uint16 as u16, c_int32 as int32
from time import sleep
from sys import exit

pruss = Icss( "/dev/uio/pruss/module" )
pruss.initialize()
ddr = pruss.ddr
pruss.uart.initialize(baudrate = 460800)


core_1 = pruss.core1
core_1.load( 'fw-c/stream.out' )


core_0 = pruss.core0
core_0.load( 'fw/decoder.bin' )

class Message( ctypes.Structure ):
    _fields_ = [
            ( 'id',     u32 ),
            ('timestamp',u32),
            ('position',   u32),
            ('force', int32),
        ]

# used to communicate ddr layout to C program
class DDRLayout( ctypes.Structure ):
    _fields_ = [
            ( 'msgbuf',      u32 ),
            ( 'num_msgs',    u16 ),
            ( 'msg_size',    u16 ),
        ]

# volatile variables in pruss shared memory
class SharedVars( ctypes.Structure ):
    _fields_ = [
            ( 'abort_file', u32 ),
            ( 'abort_line', u32 ),
            ( 'ridx',       u16 ),
        ]

# if you don't want the ringbuffer at the start of the ddr region, specify offset here
MSGBUF_OFFSET = 0

# you can use a fixed ringbuffer size:
#NUM_MSGS = 1024
# or you can scale the ringbuffer to fit the size of the ddr region:
NUM_MSGS = ( ddr.size - MSGBUF_OFFSET - ctypes.sizeof( u16 ) ) // ctypes.sizeof( Message )
NUM_MSGS = min( NUM_MSGS, 65535 )  # make sure number of messages fits in u16

# map shared memory variables
ddr_layout = core_1.map( DDRLayout, 0x10000 )
shmem = core_1.map( SharedVars, 0x10100 )
msgbuf = ddr.map( Message * NUM_MSGS, MSGBUF_OFFSET )
ddr_widx = ddr.map( u16, MSGBUF_OFFSET + ctypes.sizeof( msgbuf ) )

# inform pru about layout of shared ddr memory region
ddr_layout.msgbuf       = ddr.address + MSGBUF_OFFSET
ddr_layout.num_msgs     = NUM_MSGS
ddr_layout.msg_size     = ctypes.sizeof( Message )

# local copies of read-pointer and write-pointer
ridx = 0
widx = 0
id_value = 0
timestamp_cycles = 0


# initialize pointers in shared memory
shmem.ridx = ridx
ddr_widx.value = widx

# ready, set, go!
pruss.ecap.pwm.initialize( 2**32 )
core_0.run()
core_1.run()

def check_core():
    if not core_1.halted:
        return

    if core_1.state.crashed:
        msg = f'core crashed at pc={core_1.pc}'
    elif shmem.abort_file == 0:
        msg = f'core halted at pc={core_1.pc}'
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
    global ridx, widx, lastid, timestamp_cycles

    # read updated write-pointer
    widx = ddr_widx.value
    assert widx < NUM_MSGS  # sanity-check


    position = 0
    force = 0 
    timestamp = 0
    # process messages
    while ridx != widx:
        # note: it may be faster to copy a batch of messages from shared memory
        # instead of directly accessing individual messages and their fields.
        msg = msgbuf[ ridx ]
        # sanity-check that message id increments monotonically
        lastid = ( lastid + 1 ) & 0xffffffff
        assert msg.id == lastid
        # get 32-bit timestamp (in cycles) from message and unwrap it:
        timestamp_cycles += ( msg.timestamp - timestamp_cycles ) & 0xffffffff
        timestamp_ms = timestamp_cycles // 200000
        timestamp_s = ( timestamp_ms % 60000 ) / 1000
        timestamp_m = timestamp_ms // 60000
        timestamp_h = timestamp_m // 60
        timestamp_m = timestamp_m % 60
        timestamp = f'{timestamp_h:02d}:{timestamp_m:02d}:{timestamp_s:06.3f}' 
        # convert to timestamp in seconds:
        
        position = msg.position
        force = msg.force
        # consume message and update read pointer
        del msg  # direct access to message forbidden beyond this point
        ridx += 1
        if ridx == NUM_MSGS:
            ridx = 0
        shmem.ridx = ridx

    # update user interface
    print(f'\ridx=0x{ridx:04x} id=0x{lastid:08x} time={timestamp} position={position:08d} force={force:08d}', end='', flush=True )


try:
    while True:
        recv_messages()
        check_core()
        sleep( 0.01 )

except KeyboardInterrupt:
    pass

finally:
    print( '', flush=True )
    core_0.halt()
    core_1.halt()
    pruss.uart.io.write( b'FFV\r', discard=True, flush=True )  # interrupt continuous transmission
    sleep( 0.01 )  # make sure that response has been received
    pruss.uart.io.discard()  # discard response
