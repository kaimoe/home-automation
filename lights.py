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
	def __init__(self, red, green, blue, debug=False):
		self.led = RGBLED(red, green, blue)
		self.bright = 1
		self.thread = Thread()
		self.stop_thread = False
		self.changeLights(LightChanges.instant, 'white')
		self.debug = debug
		self.dprint('lights init')

	def handle(self, payload):
		#handle brightness
		if payload in LED_bright_terms:
			self.dprint('brightness')
			self.bright = LED_bright_terms[payload]
			self.changeLights(LightChanges.instant, self.color)
			return True

		#kill old thread
		if self.thread.is_alive():
			self.dprint('stop thread')
			self.killThread()


		change_type = LightChanges.transition
		#handle toggle/on/off/stop
		if payload == 'toggle':
			self.dprint('toggle')
			if self.led.islit():
				changeLights(change_type, 'black')
			else:
				changeLights(change_type, self.color)
			return True
		if payload == 'off':
			self.dprint('off')
			changeLights(change_type, 'black')
			return True
		if payload == 'on':
			self.dprint('on')
			changeLights(change_type, self.color)
			return True
		if payload == 'stop':
			self.dprint('stop')
			self.led.color = self.led.color
			return True

		if 'pulse' in payload:
			payload = payload.replace('pulse', '').replace(' ', '')
			if payload == '':
				payload = self.color
			change_type = LightChanges.pulse

		elif 'rainbow' in payload:
			change_type = LightChanges.rainbow

		#handle color
		self.thread = Thread(target=self.changeLights, args=(change_type, payload), daemon=True)
		self.thread.start()
		return True

	def changeLights(self, type, payload='black'):
		color = 0
		try:
			color = Color(payload)
		except ValueError:
			return False
		self.dprint('change type {} to {}{}{}'.format(type, color, color.rgb, Color('white')))
		switcher = {
			LightChanges.instant: self.setColor,
			LightChanges.transition: self.chgTrans,
			LightChanges.pulse: self.chgPulse,
			LightChanges.rainbow: self.chgRain
		}
		switcher.get(type, lambda x: self.dprint('invalid input'))(color)
		return True

	def setColor(self, color):
		self.color = color
		self.led.color = Color(tuple(self.bright*x for x in self.color))
		self.dprint('set color to {}{}{}'.format(color, color.rgb, Color('white')))

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
		self.dprint('pulsing on {}{}{}'.format(color, color.rgb, Color('white')))
		self.led.pulse(fade_in_time=FADE_DURATION, fade_out_time=FADE_DURATION, on_color=color)

	def chgRain(self, _):
		self.dprint('running rainbow')
		freq1, freq2, freq3 = .03, .03, .03
		ph1, ph2, ph3 = 0, 2, 4
		center, width = 128, 127
		#center, width = 230, 25 #for pastels
		length = 220
		while self.stop_thread is not True:
			for i in range(length):
				if self.stop_thread is True:
					break
				red = sin(freq1*i + ph1) * width + center
				green = sin(freq2*i + ph2) * width + center
				blue = sin(freq3*i + ph3) * width + center
				self.setColor(Color(red, green, blue))
				sleep((1/REFRESH_RATE)*2)

	def killThread(self):
		self.stop_thread = True
		self.thread.join()
		self.stop_thread = False

	def dprint(self, text):
		if self.debug:
			print(text)
