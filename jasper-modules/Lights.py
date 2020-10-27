from urllib2 import Request, urlopen
import json
import re

DEST_IP = 'localhost'
PORT = 8080

WORDS = ['LIGHTS', 'LIGHTING']

non_color_words = ['lighting','lights', 'light', 'make', 'turn', 'set', 'switch', 'the', 'to', 'please']

colortext = ''

def isValid(text):
	return bool(re.search(r'\blight\b', text, re.IGNORECASE))
	#colortext = ''.join([x for x in input if x not in non_color_words])

def handle(text, mic, profile):
	payload = ''.join(text.split())
	data = json.dumps({'payload': payload})
	headers = {'Content-Type': 'application/json'}
	req = Request('http://'+DEST_IP+':'+str(PORT)+'/lights', data, headers)
	try:
		res = urlopen(req)
	except:
		mic.say("Did not understand")
