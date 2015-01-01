#!/usr/bin/env python

# This file is part of RandomSources.
#
#    Copyright (C) 2012, Eric Astor
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from math import log as _log, ceil as _ceil, floor as _floor
from random import Random
from urllib import urlencode, quote as urlquote
from urllib2 import Request, urlopen

import sys
bitsPerFloat = sys.float_info.mant_dig

try:
	import json
except ImportError:
	import simplejson as json

class QuantumRandom(Random):
	"""Alternate random number generator using the ANU Quantum
	Random Numbers Server as the source.
	
	Requires Internet access."""
	
	_URL = 'https://qrng.anu.edu.au/API/jsonI.php'
	_DATATYPES = ['uint8', 'uint16', 'hex16']
	_MAXLEN = 1024
	_MAXINT = 65536
	
	_generator = None
	
	def _fetch(self, dataType, arrayLength=1, blockSize=1):
		"Fetch data from the ANU Quantum Random Numbers JSON API"
		if dataType not in self._DATATYPES:
			raise ValueException('dataType must be one of %s' % self._DATATYPES)
		if arrayLength > self._MAXLEN:
			raise ValueException('arrayLength cannot be larger than %d' % self._MAXLEN)
		if blockSize > self._MAXLEN:
			raise ValueException('blockSize cannot be larger than %d' % self._MAXLEN)
		
		options = dict(type=dataType, length=arrayLength, size=blockSize)
		url = 'https://qrng.anu.edu.au/API/jsonI.php?' + urlencode(options)
		
		def object_hook(obj):
			if obj.get('type') == 'string':
				obj['data'] = [s.encode('ascii') for s in obj['data']]
			return obj
		data = json.loads(urlopen(url).read(), object_hook=object_hook)
		assert data['success'] is True, data
		assert data['length'] == arrayLength, data
		return data['data']
	
	def cached_generator(self, dataType='uint16', cacheSize=None):
		"""Returns numbers from the ANU Quantum Random Numbers Server.
		
		Caches numbers to avoid latency."""
		if cacheSize is None:
			cacheSize = self._MAXLEN
		while 1:
			for n in self._fetch(dataType, cacheSize, cacheSize):
				yield n
	
	def random(self, generator=None):
		return self.getrandbits(bitsPerFloat, generator) * 2**-bitsPerFloat
	random.__doc__ = Random.random.__doc__
	
	def getrandbits(self, k, generator=None):
		"getrandbits(k) -> x. Generates a long int with k random bits."
		if k == 0:
			return 0
		
		if generator is None:
			if self._generator is None:
				self._generator = self.cached_generator()
			generator = self._generator
		maxlen = self._MAXLEN
		
		if k <= 16*maxlen: # A uint16 fetch supplies enough bits
			r = 0
			for i in xrange((k + 15) // 16):
				r <<= 16
				r |= generator.next()
			if k%16:
				r >>= 16 - (k%16)
			return r
		else:
			fullFetch = 8*maxlen*maxlen
			fullBlock = 8*maxlen
			remainingBits = k%fullBlock
			
			hexString = ''
			if remainingBits:
				s = hex(self.getrandbits(remainingBits, generator))
				hexString = (s[:-1] if s.endswith('L') else s)
			if k >= fullFetch:
				hexString += ''.join(''.join(self._fetch('hex16', maxlen, maxlen)) for i in xrange(k // fullFetch))
				k %= fullFetch
			if k >= fullBlock:
				hexString += ''.join(self._fetch('hex16', k // fullBlock, maxlen))
			
			return long(hexString, 16)
	
	def _stub(self, *args, **kwargs):
		"Stub method. Not used for a remote random number generator."
		return None
	seed = _stub
	jumpahead = _stub
	
	def _notimplemented(self, *args, **kwargs):
		"Method should not be called for a remote random number generator."
		raise NotImplementedError('Remote entropy sources do not have state.')
	getstate = _notimplemented
	setstate = _notimplemented

## -------------------- integer methods  -------------------

	def randrange(self, start, stop=None, step=1, generator=None):	
		# This function exactly parallels the code in Random.py,
		# so most comments are copied here.
		
		# This code is a bit messy to make it fast for the
		# common case while still doing adequate error checking.
		istart = int(start)
		if istart != start:
			raise ValueError('non-integer arg 1 for randrange()')
		if stop is None:
			if istart > 0:
				return self._randbelow(istart, generator)
			raise ValueError('empty range for randrange()')
		
		# stop argument supplied.
		istop = int(stop)
		if istop != stop:
			raise ValueError('non-integer stop for randrange()')
		width = istop - istart
		if step == 1:
			if width > 0:
				return int(istart + self._randbelow(width, generator))
			raise ValueError('empty range for randrange() (%d,%d, %d)' % (istart, istop, width))
		
		# Non-unit step argument supplied.
		istep = int(step)
		if istep != step:
			raise ValueError('non-integer step for randrange()')
		if istep > 0:
			n = (width + istep - 1) // istep
		elif istep < 0:
			n = (width + istep + 1) // istep
		else:
			raise ValueError('zero step for randrange()')
		
		if n <= 0:
			raise ValueError('empty range for randrange()')
		
		return int(istart + istep*self._randbelow(n, generator))
	randrange.__doc__ = Random.randrange.__doc__
	
	def _randbelow(self, n, generator=None, _log=_log, int=int):
		k = int(1.00001 + _log(n-1, 2.0))   # 2**k > n-1 > 2**(k-2)
		r = self.getrandbits(k, generator)
		while r >= n:
			r = self.getrandbits(k, generator)
		return r
	_randbelow.__doc__ = Random._randbelow.__doc__

## -------------------- sequence methods  -------------------

	def choice(self, seq, generator=None):
		length = len(seq)
		if length == 0:
			raise IndexError('list index out of range')
		return seq[self.randrange(length, generator=generator)]
	choice.__doc__ = Random.choice.__doc__
	
	def shuffle(self, x, random=None, generator=None):
		if random is not None:
			return Random.shuffle(self, x, random)
		
		randrange = self.randrange
		for i in reversed(xrange(1, len(x))):
			# pick an element in x[:i+1] with which to exchange x[i]
			j = randrange(i + 1, generator=generator)
			x[i], x[j] = x[j], x[i]
	shuffle.__doc__ = Random.shuffle.__doc__
	
	def sample(self, population, k, generator=None):
		# This function exactly parallels the code in Random.py.
		# Comments are therefore omitted, to save space.
		
		n = len(population)
		if not 0 <= k <= n:
			raise ValueError('sample larger than population')
		randrange = self.randrange
		result = [None] * k
		setsize = 21
		if k > 5:
			setsize += 4 ** _ceil(_log(k * 3, 4))
		if n <= setsize or hasattr(population, 'keys'):
			pool = list(population)
			for i in xrange(k):
				j = randrange(n-i, generator=generator)
				result[i] = pool[j]
				pool[j] = pool[n-i-1]
		else:
			try:
				selected = set()
				selected_add = selected.add
				for i in xrange(k):
					j = randrange(n, generator=generator)
					while j in selected:
						j = randrange(n, generator=generator)
					selected_add(j)
					result[i] = population[j]
			except (TypeError, KeyError):
				if isinstance(population, list):
					raise
				return self.sample(tuple(population), k, generator)
		return result
	sample.__doc__ = Random.sample.__doc__

if __name__ == '__main__': 
   print __doc__.strip()