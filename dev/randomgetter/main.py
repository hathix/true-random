from quantumRandom import QuantumRandom
from randomDotOrg import RandomDotOrg

GENERATE = 4500 # CHANGE ME
MULT = 1*10**10

# Get a bunch of random numbers (like thousands) and store in a file
qr = QuantumRandom()
with open('quantumrandom.txt', 'a') as qrfile:
	for x in range(0,GENERATE):
		num = int(qr.random() * MULT)
		qrfile.write(str(num) + '\n')
	qrfile.close()
#except IOError as err:
#	print err
print 'Done Quantum Random'



rdo = RandomDotOrg()
before = rdo.checkBitQuota()

# max 1,000,000 bits per day. if we have any less than 10,000 that's critical
if before<10000:
	print 'We only have ' + str(before) + ' bits left today. Critically low - exiting!'
	exit()

with open('randomdotorg.txt', 'a') as rdofile:
	# get them all at once (easier)
	nums = rdo.random(GENERATE)
	for num in nums:
		num = int(num * MULT)
		rdofile.write(str(num) + '\n')
	rdofile.close()	
after = rdo.checkBitQuota()	

# analytics
drop = before-after	
bits_per_num = int(drop/GENERATE)
nums_left = int(after / bits_per_num)
print 'Done RandomDotOrg'
print 'Our bit quota went from ' + str(before) + ' to ' + str(after) + ', a drop of ' + str(drop)
print 'For ' + str(GENERATE) + ' numbers, that\'s ' + str(bits_per_num) + ' bits per number'
print 'At that rate, we can generate ' + str(nums_left) + ' more numbers'
