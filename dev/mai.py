#!/usr/bin/env python

# fixes a value stored in a file into a good binary equiv
# a max value of 999 999 999 turns into a max of 1023
def fix(n):
	decimal = n / (1.0*10**10) # dec like .123445345
	NUM_BITS = 10
	twos = int(decimal * 2.0**NUM_BITS) # 0 -> 1023 (inclusive)
	return twos

if __name__ == "__main__":
	from utils import *
	import random
	import twister
	import readwrite
	import randtest
	import tester
	
	import timeseed
	import builtin
	import systemseed
	from quantumRandom import QuantumRandom
	from randomDotOrg import RandomDotOrg

	'''
	# fix stuff in files
	f = open('randomgetter/randomdotorg.txt')
	nums = list() # contains good 0-1023 versions of each number
	for each_line in f:
		try:
			num = int(each_line)
			nums.append(fix(num))
		except:
			pass
	readwrite.ez_write('gen/randomdotorg.txt',nums, 10)
	'''

	
	# GOOD random nums are above this; bad are below
	randthresh = 0.01
	
	# we want at least this many nums in any sample
	sample_size= 2000
	trials = 100 # how many trials of each to run, for now
	'''
	# quantum random
	results = tester.run_test_battery('quantum random', infile='gen/quantumrandom.txt')
	results.display()
	
	# random.org
	results = tester.run_test_battery('random.org', infile='gen/randomdotorg.txt')
	results.display()
	'''
	
	# s = randtest.randgen(1000)
	# print randtest.spectraltest(s)

	# GENERATING SOME DATA BELOW. DON'T MESS AROUND.
	
	'''
	# quantum random
	results_list = []
	qr = QuantumRandom()
	bits = 40
	for trialnum in range(0,trials):
		nums = [ int(qr.random() * 2**bits) for i in range(0, sample_size)]
		results = (tester.run_test_battery('quantum random', nums=nums, bits=bits))
		results_list.append(results)
	tester.results_to_csv(results_list)
	
	# random.org
	results_list = []
	rdo = RandomDotOrg()
	quota = rdo.checkBitQuota()
	# max 1,000,000 bits per day. if we have any less than 10,000 that's critical
	if quota<10000:
		print 'We only have ' + str(before) + ' bits left today. Critically low - exiting!'
	else:
		bits = 40
		for trialnum in range(0,trials):
			nums = [ int(qr.random() * 2**bits) for i in range(0, sample_size)]
			results = (tester.run_test_battery('random.org', nums=nums, bits=bits))
			results_list.append(results)
		tester.results_to_csv(results_list)
	'''
	
	# OLD SCHOOL
	# random.org
	result = tester.run_test_battery('randomdotorg',infile='gen/randomdotorg.txt')
	result.display()
	
	# quantum random
	result = tester.run_test_battery('quantum random',infile='gen/quantumrandom.txt')
	result.display()
	
	# normal random
	bits = 40
	nums = [int(random.getrandbits(bits)) for x in range(0,sample_size)] # 0 -> 2**bits - 1
	result = tester.run_test_battery('default random', nums=nums, bits=bits)
	result.display()
	
	# system random
	sr = random.SystemRandom()
	nums = [int(sr.getrandbits(bits)) for x in range(0,sample_size)] # 0 -> 2**bits - 1
	result = (tester.run_test_battery('system random', nums=nums, bits=bits))	
	result.display()
	
	# normal random seeding mersenne
	nums = []
	seeds = 100
	runs_per_seed = int(sample_size / seeds)
	for a in range(0,100):
		seed = builtin.get_seed()
		nums.extend(twister.get_random_numbers(seed, runs_per_seed))
	result = (tester.run_test_battery('random seeding twister', nums=nums))	
	result.display()
	
	# time seeding mersenne
	nums = []
	seeds = 100
	runs_per_seed = int(sample_size / seeds)
	for a in range(0,100):
		seed = timeseed.get_seed()
		nums.extend(twister.get_random_numbers(seed, runs_per_seed))
	result = (tester.run_test_battery('time seeding twister', nums=nums))	
	result.display()
	
	# quantum random seeding mersenne
	nums = []
	qr = QuantumRandom()
	seeds = 100
	runs_per_seed = int(sample_size / seeds)
	for a in range(0,100):
		seed = int(qr.random() * 2**30)
		# only use first few for seeding use each one to seed for 100 more
		nums.extend(twister.get_random_numbers(seed, runs_per_seed))
	result = (tester.run_test_battery('quantum seeding twister', nums=nums))
	result.display()	
		
	'''
	# default random
	results_list = []
	bits = 10
	for trialnum in range(0,trials):
		nums = [int(random.getrandbits(bits)) for x in range(0,sample_size)] # 0 -> 2**bits - 1
		results_list.append(tester.run_test_battery('default random', nums=nums, bits=bits))
	tester.results_to_csv(results_list)	
	
	# system random
	results_list = []
	bits = 10
	for trialnum in range(0,trials):
		sr = random.SystemRandom()
		nums = [int(sr.getrandbits(bits)) for x in range(0,sample_size)] # 0 -> 2**bits - 1
		results_list.append(tester.run_test_battery('system random', nums=nums, bits=bits))
	tester.results_to_csv(results_list)		
	
	# default random seeding mersenne
	results_list = []
	bits = 10
	for trialnum in range(0,trials):
		nums = []
		seeds = 100
		runs_per_seed = int(sample_size / seeds)
		for a in range(0,100):
			seed = builtin.get_seed()
			nums.extend(twister.get_random_numbers(seed, runs_per_seed))
		results_list.append(tester.run_test_battery('random seeding twister', nums=nums))
	tester.results_to_csv(results_list)	
	
	# system random seeding mersenne
	results_list = []
	bits = 10
	for trialnum in range(0,trials):
		nums = []
		seeds = 100
		runs_per_seed = int(sample_size / seeds)
		for a in range(0,100):
			seed = systemseed.get_seed()
			nums.extend(twister.get_random_numbers(seed, runs_per_seed))
		results_list.append(tester.run_test_battery('system random seeding twister', nums=nums))
	tester.results_to_csv(results_list)		
	
	# time seeding mersenne
	results_list = []
	bits = 10
	for trialnum in range(0,trials):
		nums = []
		seeds = 100
		runs_per_seed = int(sample_size / seeds)		
		for a in range(0,100):
			seed = timeseed.get_seed()
			nums.extend(twister.get_random_numbers(seed, runs_per_seed))
		results_list.append(tester.run_test_battery('time seeding twister', nums=nums))
	tester.results_to_csv(results_list)	
		
	# quantum random seeding mersenne
	results_list = []
	bits = 10
	for trialnum in range(0,trials):
		nums = []
		qr = QuantumRandom()
		seeds = 100
		runs_per_seed = int(sample_size / seeds)
		for a in range(0,100):
			seed = int(qr.random() * 2**30)
			# only use first few for seeding use each one to seed for 100 more
			nums.extend(twister.get_random_numbers(seed, runs_per_seed))
		results_list.append(tester.run_test_battery('quantum seeding twister', nums=nums))
	tester.results_to_csv(results_list)
	'''
