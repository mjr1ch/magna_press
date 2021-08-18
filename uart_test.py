 #!/usr/bin/python3 

from uio.ti.icss import Icss
from time import sleep

pruss = Icss( "/dev/uio/pruss/module" )
#core = pruss.core0 


print(f'Activate UART')

pruss.uart.initialize(baudrate = 9600)

#pruss.uart.io()
pruss.uart.io.write(b'CE\r')

message = pruss.uart.io.readline(newline =b'\r')

#message = message[0:len(message)-1]

print(message)


pruss.uart.io.close()
