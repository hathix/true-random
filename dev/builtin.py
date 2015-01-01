# uses the built-in python.random() to return a seed

import random

# returns a seed from 1-1000
def get_seed():
	return int(random.random() * 1000)
