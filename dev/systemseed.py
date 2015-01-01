# uses the built-in python.random() to return a seed

import random

# returns a seed from 1-1000
def get_seed():
	sr = random.SystemRandom()
	return int(sr.random() * 1000)
