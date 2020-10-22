from gpiozero import RGBLED
from colorzero import Color
from enum import Enum
import asyncio
from time import sleep
from threading import Thread
from math import sin

REFRESH_RATE = 30
TRANSITION_DURATION = 1
FADE_DURATION = 5

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
		self.thread = Thread()
		self.stop_thread = False
		self.changeLights(LightChanges.instant, 'white')
		print('lights init')

	def handle(self, payload):
		#handle brightness
		if payload in LED_bright_terms:
			print('brightness')
			self.bright = LED_bright_terms[payload]
			self.changeLights(LightChanges.instant, self.color)
			return True

		#kill old thread
		if self.thread.is_alive():
			print('stop thread')
			killThread()

		#handle on/off/stop
		if payload == 'off':
			print('off')
			self.led.off()
			return True
		if payload == 'on':
			print('on')
			self.led.color = self.color
			return True
		if payload == 'stop':
			print('stop')
			self.led.color = self.led.color #NOTE for pulse, no idea if this works lol
			return True

		change_type = LightChanges.transition
		if 'pulse' in payload:
			payload = payload.replace('pulse', '')
			if payload == '':
				payload = self.color
			change_type = LightChanges.pulse

		elif 'rainbow' in payload:
			change_type = LightChanges.rainbow

		#handle color
		self.thread = Thread(target=self.changeLights, args=(change_type, payload), daemon=True)
		self.thread.start()
		return True

	def changeLights(self, type, color_str=''):
		color = 0
		try:
			color = Color(color_str)
		except ValueError:
			return False
		print('change type {} to {}{}{}'.format(type, color, color.rgb, Color('white')))
		switcher = {
			LightChanges.instant: self.setColor,
			LightChanges.transition: self.chgTrans,
			LightChanges.pulse: self.chgPulse, #TODO
			LightChanges.rainbow: self.chgRain #TODO
		}
		switcher.get(type, lambda x: False)(color)
		return True

	def setColor(self, color):
		self.color = color
		self.led.color = Color(tuple(self.bright*x for x in self.color))
		print('set color to {}{}{}'.format(color, color.rgb, Color('white')))

	def chgTrans(self, new_color):
		N = REFRESH_RATE * TRANSITION_DURATION
		#total color difference
		diff = []
		for n, c in zip(new_color, self.led.color):
			diff.append(n - c)
		self.color = self.led.color

		#color change per update
		step = tuple(x/N for x in diff)
		for _ in range(N-1):
			step_color = []
			for c, s in zip(self.color, step):
				step_color.append(c+s)
			self.setColor(Color(tuple(step_color)))
			sleep(1/REFRESH_RATE)
		self.setColor(new_color)

	def chgPulse(self, color):
		print('pulsing on {}{}{}'.format(color, color.rgb, Color('white')))
		self.led.pulse(fade_in_time=FADE_DURATION, fade_out_time=FADE_DURATION, on_color=color)

	def chgRain(self, _):#TODO
		freq1, freq2, freq3 = .3, .3, .3
		ph1, ph2, ph3 = 0, 2, 4
		center, width = 128, 127
		#center, width = 230, 25 #for pastels
		length = 22
		while self.stop_thread is not True:
			for i in range(length):
				if self.stop_thread is not True:
					break
				red = sin(freq1*i + ph1) * width + center
				green = sin(freq2*i + ph2) * width + center
				blue = sin(freq3*i + ph3) * width + center
				self.setColor(Color(red, green, blue))


	def killThread(self):
		self.stop_thread = True
		self.thread.join()
		self.stop_thread = False
