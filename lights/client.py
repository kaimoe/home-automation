import requests

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
	r = requests.post('{}:{}/lights'.format(DEST_IP, PORT), data={'payload': colortext})
