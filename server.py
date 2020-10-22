#!/usr/bin/env python3
PORT=8080

LED_RED = 17
LED_GREEN = 22
LED_BLUE = 24
#--------------------#
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging

from lights import LED

paths = ['/lights']

def initHandler(handler_class):
	handler_class.led = LED(LED_RED, LED_GREEN, LED_BLUE)
	return handler_class

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
		if self.headers['Content-Type'] != 'application/json':
			self._set_empty()
			return

		length = int(self.headers['Content-Length']) # <--- Gets the size of data
		data = json.loads(self.rfile.read(length)) # <--- Gets the data itself
		logging.info('POST request,\nPath: %s\nHeaders:\n%s\nBody:\n%s\n',
			str(self.path), str(self.headers), data)

		if self.path not in paths:
			self._set_empty()
			return

		success = False

		if self.path == '/lights':
			success = self.led.handle(data['payload'])

		if not success:
			self._set_empty()
			return

		self._set_headers()


def run(server_class=HTTPServer, handler_class=S, port=8080):
	logging.basicConfig(level=logging.INFO)
	server_address = ('', port)
	httpd = server_class(server_address, initHandler(handler_class))
	logging.info('Starting httpd...\n')
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
	logging.info('Stopping httpd...\n')

if __name__ == '__main__':
	from sys import argv

	if len(argv) == 2:
		run(port=int(argv[1]))
	else:
		run()
