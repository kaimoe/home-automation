import requests

DEST_IP = 'localhost'
PORT = 8080

WORDS = ['LIGHTS']

non_color_words = ['lights', 'light', 'make', 'turn', 'set', 'switch', 'the', 'to', 'please']

colortext = ''

def isValid(text):
	input = text.split()
	colortext = ''.join([x for x in input if x not in non_color_words])
	return bool(colortext)

def handle(text, mic, profile):
	r = requests.post('{}:{}/lights'.format(DEST_IP, PORT), data={'payload': colortext})
