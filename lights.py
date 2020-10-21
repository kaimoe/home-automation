from gpiozero import RGBLED
from colorzero import Color
import enum import Enum
import asyncio
from time import sleep

REFRESH_RATE = 30

TRANSITION_DURATION = 1

LED_bright_terms = {
	'bright': 1.0, 'full': 1.0,
	'half': 0.5,
	'dim': 0.25, 'low': 0.25
}

LightChanges = Enum('LightChanges', 'instant transition pulse rainbow')

class LED:
	def __init__(self, red, green, blue):
		self.led = RGBLED(red, green, blue)
		self.bright = 1
		self.changeLights('white', LightChanges.instant)

	def handle(self, payload):
		#handle brightness
		if payload in LED_bright_terms:
			self.bright = LED_bright_terms[payload]
			self.changeLights(self.color, LightChanges.transition)
			return

		#handle on/off
		if payload == 'off':
			self.led.off()
			return
		if payload == 'on':
			self.led.color = LED_color
			return

		#handle fade TODO
		#handle rainbow TODO

		#handle color
		color = 0
		try:
			color = Color(payload)
		except ValueError:
			#handle unknown color/invalid input
			return
		self.changeLights(color, LightChanges.transition)

	def changeLights(self, type, color=self.led.color):
		switcher = {
			1: self.setColor,
			2: self.chgTrans,
			3: self.chgFade
		}
		switcher.get(type, lambda: False)(color)

	def setColor(self, color):
		self.color = color
		self.led.color = Color(tuple(self.bright*x for x in self.color))

	def chgTrans(self, new_color):
		n = REFRESH_RATE * TRANSITION_DURATION
		diff = new_color - self.led.color
		step = Color(tuple(x/n for x in diff.color))
		for _ in range(n-1):
			self.setColor(self.led.color + step)
			sleep(1/REFRESH_RATE)
		self.setColor(new_color)

	def chgFade(self, color):#TODO

		#x = threading.Thread(target=thread_function, args=(1,))
    	#x.start()
		pass
