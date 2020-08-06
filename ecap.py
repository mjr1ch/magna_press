#!/usr/bin/python3 

import Adafruit_BBIO.GPIO as gpio
from uio.ti.icss import Icss 
from time import sleep  
 
pruss = Icss( "/dev/uio/pruss/module" ) 
core = pruss.core0 
 
gpio.setup('P9_16',gpio.OUT)
gpio.output('P9_16',gpio.HIGH)
gpio.output('P9_16',gpio.LOW)
 
pruss.initialize()

#PWM_PERIOD = 400000000  # in 200 MHz pru cycles 0.5Hz
#PWM_PERIOD = 200000000 # in 200 MHz pru cycles 1Hz
#PWM_PERIOD = 20000000 # in 200 MHz pru cycles 10Hz
#PWM_PERIOD = 2000000 # in 200 MHz pru cycles 100Hz
PWM_PERIOD = 200000 # in 200 MHz pru cycles 1kHz
#PWM_PERIOD = 40000 # in 200 MHz pru cycles 10kHz

print( f'pwm frequency: {200e6/PWM_PERIOD/1000} kHz' )

pruss.ecap.pwm.initialize( PWM_PERIOD ) 
pruss.ecap.pwm.duty_cycle = 0.75

sleep(10)

pruss.ecap.pwm.duty_cycle = 0.0
