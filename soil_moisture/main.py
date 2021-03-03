from machine import Pin, ADC
from utime import sleep, sleep_ms

#global values
THRESHOLD = 0.63
DELAY = 1800

#init
sensor = ADC(26)
conversion_factor = 3.3 / (65535)
sens_ctl = Pin(22, Pin.OUT)
sens_ctl.off()
led = Pin(7, Pin.OUT)
led.off()

#led flash
sleep(1)
led.on()
sleep_ms(200)
led.off()
sleep_ms(200)
led.on()
sleep_ms(200)
led.off()

#wait to normalize readings
sleep(300)

print('start')
while True:
    sens_ctl.on()
    sleep(10)

    print('scanning')
    arr = []
    for i in range(50):
        arr.append(sensor.read_u16() * conversion_factor)
        sleep_ms(100)

    if (sum(arr)/len(arr) < THRESHOLD):
        print('too low!')
        led.on()
    else:
        print('acceptable')
        led.off()

    sens_ctl.off()
    sleep(DELAY)
