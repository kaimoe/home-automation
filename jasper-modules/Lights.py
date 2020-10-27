from urllib2 import Request, urlopen
import json
import string

DEST_IP = 'localhost'
PORT = 8080

WORDS = ['LIGHTS', 'LIGHTING']

non_color_words = ['lighting','lights', 'light', 'make', 'turn', 'set', 'switch', 'the', 'to', 'please']

colortext = ''

def isValid(text):
	input = text.lower().split()
	colortext = ''.join([x for x in input if x not in non_color_words])
	return bool(colortext)

def handle(text, mic, profile):
	data = json.dumps({'payload': string.join(text.split(), '')})
	headers = {'Content-Type': 'application/json'}
	req = Request('http://'+DEST_IP+':'+str(PORT)+'/lights', data, headers)
	try:
		res = urlopen(req)
	except:
		mic.say("Did not understand")
