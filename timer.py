#!/usr/bin/python3

from uio.ti.icss import Icss
from ctypes import c_uint32 as u32, Structure
from time import sleep

pruss = Icss( "/dev/uio/pruss/module" )
pruss.initialize()
pruss.ecap.pwm.initialize( 200000000 )  # 1 second period
pruss.ecap.irq.enabled = 1 << 6
pruss.ecap.irq.clear = 1 << 6

class Timestamp( Structure ):
    _fields_ = [
            ('s',   u32),
            ('ns',  u32),
        ]

seconds = pruss.dram2.map( u32, 0 );
ts = pruss.dram2.map( Timestamp, 4 );

core = pruss.core0
core.load( 'fw-c/timestamp.out' )
core.run()

prev = -1

try:
    while not core.halted:
        s = seconds.value
        # note: reading the fields like this obviously has a race condition
        if s == prev or s == prev + 1:
            print( f'\r{s}  {ts.s}.{ts.ns:09d} ', end='', flush=True )
        else:
            print( f' ->  {s}  {ts.s}.{ts.ns:09d} ', flush=True )
        prev = s
        sleep( 0.001 )

    print( "core halted??" )

except KeyboardInterrupt:
    # don't treat control-C as error
    print( '' )

finally:
    # always halt core when we're done
    core.halt()
