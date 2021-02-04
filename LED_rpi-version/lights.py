from gpiozero import RGBLED
from colorzero import Color
from enum import Enum
import asyncio
from time import sleep
from threading import Thread
from math import sin
from datetime import datetime

REFRESH_RATE = 30
TRANSITION_DURATION = 1
FADE_DURATION = 5

DEFAULT_COLOR = 'purple'

AUTODIM = True
DIM_START_HOUR = 0
DIM_END_HOUR = 12

LED_bright_terms = {
	'bright': 1.0, 'full': 1.0,
	'half': 0.5,
	'dim': 0.25, 'low': 0.25
}

LightChanges = Enum('LightChanges', 'instant transition pulse rainbow')

class LED:
	def __init__(self, red, green, blue, verbose=False):
		self.led = RGBLED(red, green, blue)
		self.bright = 1
		self.thread = Thread()
		self.stop_thread = False
		self.verbose = verbose
		if AUTODIM:
			t = Thread(target=self.autoDimming, daemon=True)
			t.start()
		self.changeLights(LightChanges.instant, DEFAULT_COLOR)
		self.dprint('lights init')

	def handle(self, payload):
		#kill old thread
		self.killThread()

		#handle brightness
		if payload in LED_bright_terms:
			self.dprint('brightness to {}'.format(payload))
			self.bright = LED_bright_terms[payload]
			self.changeLights(self.change_type, self.color)
			return True

		change_type = LightChanges.transition
		#handle toggle/on/off/stop
		if payload == 'toggle':
			self.dprint('toggle')
			if self.led.is_lit:
				self.led.off()
			else:
				self.changeLights(change_type, self.color)
			return True
		if payload == 'off':
			self.dprint('off')
			self.led.off()
			return True
		if payload == 'on':
			self.dprint('on')
			self.changeLights(change_type, self.color)
			return True
		if payload == 'stop':
			self.dprint('stop')
			self.led.color = self.led.color
			return True

		color = payload
		if 'pulse' in payload:
			color = payload.replace('pulse', '').replace(' ', '')
			if color == '':
				color = self.color
			change_type = LightChanges.pulse
		elif 'rain' in payload:
			color = 'black'
			change_type = LightChanges.rainbow

		#handle color
		self.thread = Thread(target=self.changeLights, args=(change_type, color), daemon=True)
		self.thread.start()
		return True

	def changeLights(self, type, colortext='black'):
		try:
			color = Color(colortext)
		except ValueError:
			self.dprint('error while trying to parse {}'.format(colortext))
			return False
		self.dprint('change type {} to {}{}{}'.format(type, color, color.rgb, Color('white')))
		self.change_type = type
		switcher = {
			LightChanges.instant: self.setColor,
			LightChanges.transition: self.chgTrans,
			LightChanges.pulse: self.chgPulse,
			LightChanges.rainbow: self.chgRain
		}
		switcher.get(type, lambda x: self.dprint('invalid input'))(color)
		return True

	def setColor(self, color, ignore_bright=False):
		self.color = color
		self.led.color = self.applyBright(color) if ignore_bright is False else color
		self.dprint('set color to {}{}{}'.format(color, color.rgb, Color('white')))

	def applyBright(self, color):
		if self.bright == 1:
			return color
		else:
			return Color(tuple(self.bright*x for x in color))

	def chgTrans(self, new_color, ignore_bright=False, duration=TRANSITION_DURATION):
		N = REFRESH_RATE * duration
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
			self.setColor(Color(tuple(step_color)), ignore_bright)
			sleep(1/REFRESH_RATE)
		self.setColor(new_color, ignore_bright)

	def chgPulse(self, color):
		self.dprint('pulsing on {}{}{}'.format(color, color.rgb, Color('white')))
		color = self.applyBright(color)
		self.led.pulse(fade_in_time=FADE_DURATION, fade_out_time=FADE_DURATION, on_color=color)

	def chgRain(self, _):
		self.dprint('running rainbow')
		freq1, freq2, freq3 = .03, .03, .03
		ph1, ph2, ph3 = 0, 2, 4
		center, width = 128, 127
		#center, width = 230, 25 #for pastels
		length = 200
		while self.stop_thread is not True:
			for i in range(length):
				if self.stop_thread is True:
					break
				red = sin(freq1*i + ph1) * width + center
				green = sin(freq2*i + ph2) * width + center
				blue = sin(freq3*i + ph3) * width + center
				self.setColor(Color(red, green, blue))
				sleep((1/REFRESH_RATE)*2)

	def autoDimming(self):
		last_dimmed_day = 0
		last_undimmed_day = 0
		while True:
			dt = datetime.now()
			if (last_dimmed_day != dt.day) and (DIM_START_HOUR <= dt.hour < DIM_END_HOUR) and self.bright != 0.25:
				self.dprint('auto-dimming')
				last_dimmed_day = dt.day
				self.bright = 0.25
			elif (last_undimmed_day != dt.day) and (dt.hour < DIM_START_HOUR or dt.hour >= DIM_END_HOUR) and self.bright != 1:
				self.dprint('auto-undimming')
				last_undimmed_day = dt.day
				self.bright = 1
			else:
				sleep(60)
				continue

			if self.led.is_lit:
				self.killThread()
				if self.change_type == LightChanges.transition:
					self.chgTrans(applyBright(self.color), ignore_bright=True, duration=3)
				else:
					self.changeLights(self.change_type, self.color)
			sleep(60)

	def killThread(self):
		if self.thread.is_alive() is not True:
			return
		self.dprint('stop thread')
		self.stop_thread = True
		self.thread.join()
		self.stop_thread = False

	def dprint(self, text):
		if self.verbose:
			print(text)
