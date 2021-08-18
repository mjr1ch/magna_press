from time import sleep
from uio.ti.pwmss import Pwmss

ehrpwm0 = Pwmss("/dev/uio/pwmss0").pwm

period = 20000
max_duty = period


ehrpwm0.initialize(period,1)



ehrpwm0.ld_compare_a = max_duty
ehrpwm0.ld_compare_b = 0
sleep(3)

ehrpwm0.ld_compare_a = 0
ehrpwm0.ld_compare_b = int(max_duty/2)
sleep(3)

ehrpwm0.ld_compare_a = int(max_duty/5)
ehrpwm0.ld_compare_b = 0
sleep(3)

ehrpwm0.ld_compare_a = 0
ehrpwm0.ld_compare_b = int(max_duty/3)
sleep(3)

ehrpwm0.ld_compare_a = 0
ehrpwm0.ld_compare_b = int(max_duty)
sleep(3)

ehrpwm0.stop()
