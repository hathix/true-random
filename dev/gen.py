import random

f = open('a.dat', 'w')
for x in range(1,1000):
	f.write(str(random.getrandbits(32)))
f.close()
