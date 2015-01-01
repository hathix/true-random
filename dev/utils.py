#!/usr/bin/env python

from math import *

# turns a decimal number to a binary string
# dec2bin(13) = '1101'
dec2bin = lambda x: (dec2bin(x/2) + str(x%2)) if x else ''

# turns a decimal number to a binary string but puts 0's in front to make it length len
# binwpad(2, 3) -> would normally be 10 but we give 010
def binwpad(decimal, length):
	raw_bin = dec2bin(decimal)
	padded_bin = raw_bin.zfill(length)
	return padded_bin

# given a list of normal numbers, smooshes them into one huge binary string and returns it
# num_bits: how long each small binary string should be (we'll add 0's on the front if it's too small)
def binarify(num_list, num_bits):
	strs = [ binwpad(x, num_bits) for x in num_list ]
	combined = ''.join(strs)
	return combined
	
def bits_needed(nums):
	return int(log(max(nums),2)+1)

def file_exists(filename):
	import os
	return os.path.exists(filename)
