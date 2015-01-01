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

import functools, sys
bitsPerFloat = sys.float_info.mant_dig

int16 = functools.partial(int, base=16)

class RandomDotOrg(Random):
	"""Alternate random number generator using random.org as the
	source.
	
	Requires Internet access."""
	
	__version__ = '0.1.0'
	
	_intMin = -1000000000
	_intMax = 1000000000
	_maxWidth = _intMax - _intMin + 1
	
	_hexMax = int(_floor(_log(_intMax, 16)))
	_bitsMax = _hexMax << 2
	_bitsMaxInt = 2**_bitsMax-1
	
	_fetchMax = 10000
	
	def _fetch(self, service, **kwargs):
		"Fetch data from the Random.org HTTP Interface"
		url = 'https://www.random.org/%s/?' % urlquote(service)
		options = dict(format='plain')
		options.update(kwargs)
		headers = {'User-Agent': 'RandomSources.randomDotOrg/%s' % self.__version__}
		
		req = Request(url + urlencode(options), headers=headers)
		return urlopen(req).read().splitlines()
	
	def fetchHex(self, digits, rnd='new'):
		remainderDigits = digits % self._hexMax
		fullInts = digits // self._hexMax
		remainderFetch = fullInts % self._fetchMax
		fullFetches = fullInts // self._fetchMax
		
		r = ''
		options = dict(col=1, base=16, min=0, max=self._bitsMaxInt, num=self._fetchMax, rnd=rnd)
		if fullFetches > 0:
			r += ''.join(''.join(self._fetch('integers', **options)) for i in xrange(fullFetches))
		if remainderFetch > 0:
			options['num'] = remainderFetch
			r += ''.join(self._fetch('integers', **options))
		if remainderDigits > 0:
			options['max'] = 16**remainderDigits - 1
			options['num'] = 1
			r += self._fetch('integers', **options)[0]
		return r
	
	def fetchIntegers(self, imin, imax, num, rnd='new'):
		fullFetches = num // self._fetchMax
		remainderFetch = num % self._fetchMax
		
		r = []
		options = dict(col=1, base=10, min=imin, max=imax, num=self._fetchMax, rnd=rnd)
		for i in xrange(num // self._fetchMax):
			r.extend(map(int, self._fetch('integers', **options)))
		if remainderFetch > 0:
			options['num'] = remainderFetch
			r.extend(map(int, self._fetch('integers', **options)))
		return r
	
	def checkBitQuota(self):
		return int(self._fetch('quota', format='plain')[0])
	
	def random(self, n=1):
		if n == 1:
			return self.getrandbits(bitsPerFloat) * 2**-bitsPerFloat
		return [x * 2**-bitsPerFloat for x in self.getrandbits(bitsPerFloat, n)]
	random.__doc__ = Random.random.__doc__
	
	def getrandbits(self, k, n=1):
		"getrandbits(k) -> x. Generates a long int with k random bits."
		if k == 0:
			return 0
		
		hexString = self.fetchHex((k*n + 3) // 4)
		result = long(hexString, 16)
		filter = 2**k - 1
		
		if n == 1:
			return result & filter
		
		r = []
		for i in xrange(n):
			r.append(result & filter)
			result >>= k
		return r
	
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

	def randrange(self, start, stop=None, step=1, n=1):	
		# This function exactly parallels the code in Random.py,
		# with the one additional feature of fetching multiple
		# requests together; most comments are copied here.
		
		imin = self._intMin
		maxwidth = self._maxWidth
		
		# This code is a bit messy to make it fast for the
		# common case while still doing adequate error checking.
		istart = int(start)
		if istart != start:
			raise ValueError('non-integer arg 1 for randrange()')
		if stop is None:
			if istart > 0:
				if istart > maxwidth:
					if n > 1:
						return self._randbelow(istart, n)
					return self._randbelow(istart)
				r = self.fetchIntegers(imin, imin + istart - 1, n)
				if n == 1:
					return r[0]
				return r
			raise ValueError('empty range for randrange()')
		
		# stop argument supplied.
		istop = int(stop)
		if istop != stop:
			raise ValueError('non-integer stop for randrange()')
		width = istop - istart
		if step == 1 and width > 0:
			if width >= maxwidth:
				if n > 1:
					return [int(istart + x) for x in self._randbelow(width, n)]
				return int(istart + self._randbelow(width))
			shift = istart - imin
			r = self.fetchIntegers(imin, imin + width - 1, n)
			if n == 1:
				return shift + r[0]
			return [int(shift + x) for x in r]
		if step == 1:
			raise ValueError('empty range for randrange() (%d,%d, %d)' % (istart, istop, width))
		
		# Non-unit step argument supplied.
		istep = int(step)
		if istep != step:
			raise ValueError('non-integer step for randrange()')
		if istep > 0:
			size = (width + istep - 1) // istep
		elif istep < 0:
			size = (width + istep + 1) // istep
		else:
			raise ValueError('zero step for randrange()')
		
		if size <= 0:
			raise ValueError('empty range for randrange()')
		
		if size >= maxwidth:
			if n > 1:
				return [int(istart + istep*x) for x in self._randbelow(size, n)]
			return int(istart + istep*self._randbelow(size))
		shift = istart - istep*imin
		r = self.fetchIntegers(imin, imin + size - 1, n)
		if n == 1:
			return int(shift + istep*r[0])
		return [int(shift + istep*x) for x in r]
	randrange.__doc__ = Random.randrange.__doc__
	
	def randint(self, a, b, n=1):
		return self.randrange(a, b+1, n=n)
	randint.__doc__ = Random.randint.__doc__
	
	def _randbelow(self, n, num=1, _log=_log, int=int):
		k = int(1.00001 + _log(n-1, 2.0))   # 2**k > n-1 > 2**(k-2)
		
		if num == 1:
			r = self.getrandbits(k)
			while r >= n:
				r = self.getrandbits(k)
			return r
		
		r = []
		filter = (1 << k) - 1
		while num > 0:
			bits = self.getrandbits(k*num)
			for i in xrange(num):
				x = bits & filter
				if x < n:
					r.append(x)
					num -= 1
		return r
	_randbelow.__doc__ = Random._randbelow.__doc__

## -------------------- sequence methods  -------------------
	
	def choice(self, seq, n=1):
		length = len(seq)
		if length == 0:
			raise IndexError('list index out of range')
		
		if n == 1:
			return seq[self.randrange(length)]
		
		return [seq[i] for i in self.randrange(length, n=n)]
	choice.__doc__ = Random.choice.__doc__
	
	def shuffle(self, x, random=None):
		if random is not None:
			return Random.shuffle(self, x, random)
		
		randrange = self.randrange
		for i in reversed(xrange(1, len(x))):
			# pick an element in x[:i+1] with which to exchange x[i]
			j = randrange(i + 1)
			x[i], x[j] = x[j], x[i]
	shuffle.__doc__ = Random.shuffle.__doc__
	
	def sample(self, population, k):
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
				j = randrange(n-i)
				result[i] = pool[j]
				pool[j] = pool[n-i-1]
		else:
			try:
				selected = set()
				selected_add = selected.add
				for i in xrange(k):
					j = randrange(n)
					while j in selected:
						j = randrange(n)
					selected_add(j)
					result[i] = population[j]
			except (TypeError, KeyError):
				if isinstance(population, list):
					raise
				return self.sample(tuple(population), k)
		return result
	sample.__doc__ = Random.sample.__doc__

if __name__ == '__main__': 
   print __doc__.strip()