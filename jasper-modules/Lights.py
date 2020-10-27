from urllib2 import Request, urlopen
import json
import re

DEST_IP = 'localhost'
PORT = 8080

WORDS = ['LIGHT', 'LIGHTS', 'LIGHTING', 'PULSE', 'RAINBOW', 'ON', 'OFF', 'STOP', 'DIM', 'BRIGHT', 'HALF', 'FULL', 'LOW''BLUE', 'RED', 'GREEN', 'YELLOW', 'ORANGE', 'PURPLE', 'WHITE', 'PINK', 'CYAN', 'DARK']

non_color_words = ['lighting','lights', 'light', 'make', 'turn', 'set', 'switch', 'the', 'to', 'please']

colortext = ''

def isValid(text):
	return bool(re.search(r'light', text, re.IGNORECASE))

def handle(text, mic, profile):
	input = text.lower().split()
	colortext = ''.join([x for x in input if x not in non_color_words])
	if not colortext:
		mic.say('What color?')
		colortext = mic.activeListen().lower().replace('', '')
	data = json.dumps({'payload': colortext})
	headers = {'Content-Type': 'application/json'}
	req = Request('http://'+DEST_IP+':'+str(PORT)+'/lights', data, headers)
	try:
		res = urlopen(req)
	except:
		mic.say("Did not understand")
