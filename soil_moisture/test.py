from machine import Pin, ADC
import utime

sensor = ADC(26)
conversion_factor = 3.3 / (65535)

sens_ctl = Pin(22, Pin.OUT)
sens_ctl.on()

print('start')
while True:
	utime.sleep(2)
	reading = sensor.read_u16() * conversion_factor
	print(reading)
