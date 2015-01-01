#!/usr/bin/env python

# easy library for writing stuff

from utils import *
		
# writes a series of numbers as bits (like 010101 - in string form)	
def bin_write(filename, num_list, num_bits):
	try:
		with open(filename, 'w') as file:
			# turn num list into a string of binary digs (0100010) and write that in
			string = binarify(num_list, num_bits)
			# print string
			file.write(string)
			print('Wrote to ' + filename)
	except IOError as err:
			print('File Error: ' + str(err))
			
# reads from a file containing binary code (1's and 0's)
# returns the string of 1's and 0's		
def bin_read(filename):
	try:
		f = open(filename)
		string = ''.join([line for line in f])
		# 86 any \r or \n
		string = string.rstrip('\r\n')
		f.close()
		return string
	except IOError as err:
			print('File Error: ' + str(err))	

# reads from a file containing pure numbers (1 per line)
# returns an array of those nums
def num_read(filename):
	f = open(filename)
	nums = list()
	for each_line in f:
		try:
			nums.append(int(each_line))
		except:
			pass #probably empty line
	f.close()
	return nums
