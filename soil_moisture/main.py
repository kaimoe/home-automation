from machine import Pin, ADC
import utime

sensor = ADC(26)
conversion_factor = 3.3 / (65535)

sens_ctl = Pin(22, Pin.OUT)

led = Pin(7, Pin.OUT)

print('start')
while True:
	sens_ctl.on()
	utime.sleep(2)
	reading = sensor.read_u16() * conversion_factor
	print(reading)

	led.on()
	utime.sleep(5)

	led.off()
	sens_ctl.off()
	utime.sleep(20)
