# runs a test battery

from utils import *
import randtest
import time
import readwrite

tests={1:'monobitfrequencytest',\
       2:'blockfrequencytest',\
       3:'runstest',\
       4:'longestrunones10000',
       5:'binarymatrixranktest',\
       6:'spectraltest',\
       7:'nonoverlappingtemplatematchingtest',\
       8:'overlappingtemplatematchingtest',\
       9:'maurersuniversalstatistictest',\
       #10:'linearcomplexitytest',\
       #11:'serialtest',\
       #12:'aproximateentropytest',\
       13:'cumultativesumstest',\
       14:'randomexcursionstest',\
       15:'randomexcursionsvarianttest',\
       16:'cumultativesumstestreverse',\
       #17:'lempelzivcompressiontest'\
      }

'''
	Must pass name. Either pass nums or infile.
	name	the name to call this battery (usually the source). Make it filename-friendly, like "my-nums"
	nums	list of ints
	bits	num bits to use when converting to binary. We'll auto-calc this, but pass it if you want to mandate a certain value.
	infile	name of file containing a binary sequence
'''
def run_test_battery(name,nums=None, bits=None, infile=None):
	# we need a big binary string
	string = ''
	if nums:
		if not bits:
			bits = bits_needed(nums)
		string = binarify(nums, bits)
	elif infile:
		string = readwrite.bin_read(infile)
	
	results = Results(name)	# storage of all scores
		
	for i in tests:
		try:
			test_name = tests.get(i)
			score = eval("randtest."+test_name)(string)
			results[test_name] = score # put to results storage
			# print test_name
		except:
			print str(tests.get(i)) + ': failed' 
			pass
	
	#print "Done tests for " + name
	
	return results

#def results_combined_to_csv(results_list)

'''
	Given a list of Results objects - probably from a bunch of trials - this will output a CSV file containing all that
'''
def results_to_csv(results_list):
	# we're assuming all the results lists have the same name. The filename is [name].csv
	filename = "results/" + results_list[0].name + ".csv"
	
	# see if there's anything in there
	f = None
	trial_start = 0
	if(file_exists(filename)):
		# don't write a header in, open w/ appending
		# figure out how many trials are in there
		f = open(filename, 'a')
		#print("Appending results to " + filename);
	else:
		# no file, write in header
		f = open(filename, 'w')
		# header row
		# again assuming all of the results went through the same tests
		header = "average," + ','.join(results_list[0].sorted_test_names)
		f.write(header + "\n")
		#print("Creating " + filename)
	# now write in actual data
	for results in results_list:
		text = results.to_csv()
		f.write(text + "\n")
	f.close()
	
	# quick analytics
	score_sum = sum([ r.aggregate for r in results_list ])
	score_len = len(results_list)
	avg_score = score_sum/score_len
	print filename + " done.\n\tAverage score: " + str(avg_score)

class Results(dict):
	def __init__(self,name):
		dict.__init__(self)
		self.name = name
		
	'''
		Prints information about this to the console.
	'''
	def display(self):
		print '===' + self.name.upper() + '==='
		print '\tAggregate:' + str(self.aggregate)
		for test_name in self:
			print '\t' + test_name + ':\t' + str(self.get_score(test_name))
	
	'''
		Gives the names of the tests this underwent in alpha order.
		For example, ['test1', 'test2', 'test3']
	'''
	@property
	def sorted_test_names(self):
		return sorted(self)
	
	def to_csv(self):
		# alphabetize all the scores by test name
		sorted_scores = [ str(self.get_score(name)) for name in sorted(self) ] # the result for 'a' is first, then 'b', etc
		# in format aggregate,score1,score2,score3
		string = str(self.aggregate) + ",";
		#remainder is the other scores joined by commas
		remainder = ','.join(sorted_scores)
		return string + remainder
		
	'''
		Returns a score for a given test.
		But if that score is a list, this returns the average of that list.
	'''
	def get_score(self, test_name):
		score = self.get(test_name)
		if isinstance(score, list):
			return sum(score)/len(score)
		else:
			return score
    
	'''
		Averages the individual scores.
	'''
	@property
	def aggregate(self):
		# get the sum. Totally unweighted
		total = sum([ self.get_score(test_name) for test_name in self])
		# average it
		average = total / len(self)
		return average
