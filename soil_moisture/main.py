from machine import Pin, ADC
from utime import sleep, sleep_ms

THRESHOLD = 2.0

sensor = ADC(26)
conversion_factor = 3.3 / (65535)

sens_ctl = Pin(22, Pin.OUT)

led = Pin(7, Pin.OUT)

print('start')
while True:
	sens_ctl.on()
	sleep(60)

	print('scanning')
	arr = []
	for i in range(50):
		reading = sensor.read_u16() * conversion_factor
		arr.append(reading)
		sleep_ms(100)

	if (sum(arr)/len(arr) < THRESHOLD):
		print('too low')

	else:
		print('acceptable')
		led.off()
