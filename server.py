#!/usr/bin/env python3
#from gpiozero import RGBLED
#from colorzero import Color
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging

PORT=8080

LED_RED = 17
LED_GREEN = 22
LED_BLUE = 24

paths = ['lights']

LED = 0
LED_bright = 0

def init():
	LED = RGBLED(LED_RED, LED_GREEN, LED_BLUE)
	LED.color = Color('white')

class S(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()

	def _set_empty(self):
		self.send_response(400)
		self.end_headers()

	def do_GET(self):
		logging.info('GET request,\nPath: %s\nHeaders:\n%s\n', str(self.path), str(self.headers))
		self._set_empty()
		return

	def do_POST(self):
		if ctype != 'application/json':
			self._set_empty()
			return

		length = int(self.headers['Content-Length']) # <--- Gets the size of data
		message = json.loads(self.rfile.read(length)) # <--- Gets the data itself
		logging.info('POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n',
			str(self.path), str(self.headers), post_data.decode('utf-8'))

		if self.path not in paths:
			self._set_empty()
			return

		if self.path == 'lights':
			handleLights(message[payload])


		self._set_headers()

def handleLights(payload):


def run(server_class=HTTPServer, handler_class=S, port=8080):
	logging.basicConfig(level=logging.INFO)
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	logging.info('Starting httpd...\n')
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
	logging.info('Stopping httpd...\n')

if __name__ == '__main__':
	from sys import argv

	init()

	if len(argv) == 2:
		run(port=int(argv[1]))
	else:
		run()
