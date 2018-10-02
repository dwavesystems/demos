from itertools import islice
import unittest
from jobShopScheduler import JobShopScheduler

def fillWithZeros(myDict, jobDict, maxTime):
	""" Fills the 'missing' myDict keys with a value of 0.
	args:
		myDict: a dictionary.  {taskName: taskValue, ..}
		jobDict: a dictionary. {jobName: [(machineVal, taskTimeSpan), ..], ..}
		maxTime: integer. Max time for the schedule
	"""
	for job, tasks in jobDict.items():
		for pos in xrange(len(tasks)):
			prefix = str(job) + "_" + str(pos)

			for t in xrange(maxTime):
				key = prefix + "," + str(t)

				if key not in myDict:
					myDict[key] = 0
	
class TestIndividualJSSConstraints(unittest.TestCase):
	def test_oneStartConstraint(self):
		jobs = {"car":[("key",2),("gas",1)],
				"stove":[("gas",4)]}
		jss = JobShopScheduler(jobs, 3)
		jss._addOneStartConstraint()

		# Tasks only start once
		oneStartSoln = {"car_0,0": 1, "car_0,1": 0, "car_0,2": 0,
						"car_1,0": 0, "car_1,1": 1, "car_1,2": 0,
						"stove_0,0":1, "stove_0,1": 0, "stove_0,2": 0}

		# Task car_1 starts twice; it starts on times 0 and 1
		multiStartSoln = {"car_0,0": 1, "car_0,1": 0, "car_0,2": 0,
						  "car_1,0": 0, "car_1,1": 1, "car_1,2": 0,
						  "stove_0,0":1, "stove_0,1": 1, "stove_0,2": 0}

		self.assertTrue(jss.csp.check(oneStartSoln))
		self.assertFalse(jss.csp.check(multiStartSoln))
	
	def test_precedenceConstraint(self):
		jobs = {0: [("m1", 2), ("m2", 1)]}
		maxTime = 4
		jss = JobShopScheduler(jobs, maxTime)
		jss._addPrecedenceConstraint()

		# Task 0_0 starts after task 0_1
		backwardSoln = {"0_0,3":1, "0_1,0":1}	
		fillWithZeros(backwardSoln, jobs, maxTime)

		# Tasks start at the same time
		sameStartSoln = {"0_0,1":1, "0_1,1":1}
		fillWithZeros(sameStartSoln, jobs, maxTime)

		# Task 0_1 starts before 0_0 has completed
		overlapSoln = {"0_0,1":1, "0_1,2":1}
		fillWithZeros(overlapSoln, jobs, maxTime)

		# Tasks follows correct order and respects task duration	
		orderedSoln = {"0_0,0":1, "0_1,2":1}
		fillWithZeros(orderedSoln, jobs, maxTime)

		self.assertFalse(jss.csp.check(backwardSoln))
		self.assertFalse(jss.csp.check(sameStartSoln))
		self.assertFalse(jss.csp.check(overlapSoln))
		self.assertTrue(jss.csp.check(orderedSoln))

	def test_shareMachineConstraint(self):
		jobs = {"movie": [("pay",1), ("watch",3)],
				"tv": [("watch",1)],
				"netflix": [("watch",3)]}
		maxTime = 7
		jss = JobShopScheduler(jobs, maxTime)
		jss._addShareMachineConstraint()

		# All jobs 'watch' at the same time
		sameStartSoln = {"movie_0,0":1, "movie_1,1":1,
						 "tv_0,1":1, 
						 "netflix_0,1":1}
		fillWithZeros(sameStartSoln, jobs, maxTime)

		# 'movie' does not obey precedence, but respects machine sharing
		badOrderShareSoln = {"movie_0,4":1, "movie_1,0":1,
							 "tv_0,3":1,
							 "netflix_0,4":1}
		fillWithZeros(badOrderShareSoln, jobs, maxTime)

		self.assertFalse(jss.csp.check(sameStartSoln))
		self.assertTrue(jss.csp.check(badOrderShareSoln))

	def test_absurdTimesAreRemoved(self):
		pass


class TestCombinedJSSConstraints(unittest.TestCase):
	#TODO: test job with no tasks
	#TODO: test no jobs
	#TODO: test non-integer durations
	#TODO: insufficient maxTime
	def test_denseSchedule(self):
		jobs = {"a": [(1,2),(2,2),(3,2)],                                           
				"b": [(3,3),(2,1),(1,1)],                                           
				"c": [(2,2),(1,3),(2,1)]}
		maxTime = 6
		jss = JobShopScheduler(jobs, maxTime)
		jss.solve()
	
		# Solution that obeys all constraints
		goodSoln = {"a_0,0":1, "a_1,2":1, "a_2,4":1,
					"b_0,0":1, "b_1,4":1, "b_2,5":1,
					"c_0,0":1, "c_1,2":1, "c_2,5":1}
		fillWithZeros(goodSoln, jobs, maxTime)

		# Tasks a_1 and b_1 overlap in time on machine 2
		overlapSoln = {"a_0,0":1, "a_1,2":1, "a_2,4":1,
					   "b_0,0":1, "b_1,3":1, "b_2,5":1,
					   "c_0,0":1, "c_1,2":1, "c_2,5":1}
		fillWithZeros(overlapSoln, jobs, maxTime)

		self.assertTrue(jss.csp.check(goodSoln))
		self.assertFalse(jss.csp.check(overlapSoln))

	def test_relaxedSchedule(self):
		jobs = {"breakfast": [("cook",2),("eat",1)],
				"music": [("play",2)]}
		maxTime = 7
		jss = JobShopScheduler(jobs, maxTime)
		jss.solve()

		# Solution obeys all constraints
		goodSoln = {"breakfast_0,0":1, "breakfast_1,4":1,
					"music_0,3": 1}
		fillWithZeros(goodSoln, jobs, maxTime)

		# 'breakfast' tasks are out of order
		badOrderSoln = {"breakfast_0,1":1, "breakfast_1,0":1,
						"music_0,0":1}
		fillWithZeros(badOrderSoln, jobs, maxTime)

		self.assertTrue(jss.csp.check(goodSoln))
		self.assertFalse(jss.csp.check(badOrderSoln))

class TestJSSResponse(unittest.TestCase):
	def compare(self, response, expected):
		""" Comparing response to expected results
		"""
		for sample in islice(response.samples(), 1):
			# Comparing variables found in sample and expected
			expectedKeys = set(expected.keys())
			sampleKeys = set(sample.keys())
			commonKeys = expectedKeys & sampleKeys
			diffKeys = expectedKeys - sampleKeys	# expectedKeys is a superset

			# Check that common variables match
			for key in commonKeys:
				self.assertEqual(sample[key], expected[key])

			# Check that non-existent 'sample' variables are 0
			for key in diffKeys:
				self.assertEqual(expected[key], 0)

	def test_tinySchedule(self):
		jobs = {"a": [(1,1),(2,1)],
				"b": [(2,1)]}
		maxTime = 2
		jss = JobShopScheduler(jobs, maxTime)
		response, csp = jss.solve("exact")

		# Create expected solution
		expected = {"a_0,0":1, "a_1,1":1, "b_0,0":1}
		fillWithZeros(expected, jobs, maxTime)

		# Compare variable values
		self.compare(response, expected)

	def test_largerSchedule(self):
		jobs = {'small1': [(1,1)],
				'small2': [(2,2)],
				'longJob': [(0,1),(1,1),(2,1)]}
		maxTime = 3
		jss = JobShopScheduler(jobs, maxTime)
		response, csp = jss.solve("exact")

		# Create expected solution
		expected = {"small1_0,0":1,
					"small2_0,0":1,
					"longJob_0,0":1, "longJob_1,1":1, "longJob_2,2":1}
		fillWithZeros(expected, jobs, maxTime)

		# Compare variable values
		self.compare(response, expected)

if __name__ == "__main__":
	unittest.main()
