from gpiozero import RGBLED
from colorzero import Color
from enum import Enum
import asyncio
from time import sleep

REFRESH_RATE = 10

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
		self.changeLights(LightChanges.instant, 'white')
		print('lights init')

	def handle(self, payload):
		#handle brightness
		if payload in LED_bright_terms:
			print('brightness')
			self.bright = LED_bright_terms[payload]
			self.changeLights(LightChanges.transition, self.color)
			return

		#handle on/off
		if payload == 'off':
			print('off')
			self.led.off()
			return
		if payload == 'on':
			print('on')
			self.led.color = self.color
			return

		#handle color
		self.changeLights(LightChanges.transition, payload)

	def changeLights(self, type, color_str=''):
		color = 0
		try:
			color = Color(color_str)
		except ValueError:
			#handle unknown color/invalid input
			return
		print('change type {} to {}'.format(type, color.rgb))
		switcher = {
			LightChanges.instant: self.setColor,
			LightChanges.transition: self.chgTrans,
			LightChanges.pulse: self.chgPulse, #TODO
			LightChanges.rainbow: self.chgRain #TODO
		}
		switcher.get(type, lambda x: False)(color)

	def setColor(self, color):
		self.color = color
		self.led.color = Color(tuple(self.bright*x for x in self.color))
		print('set color to {}'.format(color.rgb))

	def chgTrans(self, new_color):
		N = REFRESH_RATE * TRANSITION_DURATION
		diff = []
		for n, c in zip(new_color, self.color):
			diff.append(n - c)

		step = tuple(x/N for x in diff)
		for _ in range(N-1):
			step_color = []
			for c, s in zip(self.color, step):
				step_color.append(c+s)
			self.setColor(Color(tuple(step_color)))
			sleep(1/REFRESH_RATE)
		self.setColor(new_color)

	def chgPulse(self, color):#TODO

		#x = threading.Thread(target=thread_function, args=(1,))
    	#x.start()
		pass
