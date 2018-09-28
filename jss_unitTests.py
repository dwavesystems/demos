import unittest
from jobShopScheduler import JobShopScheduler

def fillWithZeros(myDict, keyTuples, maxTime):
	""" Fills the 'missing' myDict keys with a value of 0.
	args:
		myDict: a dictionary.  {jobName: [(machineVal, taskTimeSpan),..]}
		keyTuples: list of tuples.  [(jobName, numberOfTasksInJob),..]
		maxTime: integer. Max time for the schedule
	"""
	for job, nTasks in keyTuples:
		for pos in xrange(nTasks):
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
		fillWithZeros(backwardSoln, [("0",2)], maxTime)

		# Tasks start at the same time
		sameStartSoln = {"0_0,1":1, "0_1,1":1}
		fillWithZeros(sameStartSoln, [("0",2)], maxTime)

		# Task 0_1 starts before 0_0 has completed
		overlapSoln = {"0_0,1":1, "0_1,2":1}
		fillWithZeros(overlapSoln, [("0",2)], maxTime)

		# Tasks follows correct order and respects task duration	
		orderedSoln = {"0_0,0":1, "0_1,2":1}
		fillWithZeros(orderedSoln, [("0",2)], maxTime)

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
		fillWithZeros(sameStartSoln, [("movie",2), ("tv",1), ("netflix",1)],\
			maxTime)

		# 'movie' does not obey precedence, but respects machine sharing
		badOrderShareSoln = {"movie_0,4":1, "movie_1,0":1,
							 "tv_0,3":1,
							 "netflix_0,4":1}
		fillWithZeros(badOrderShareSoln,\
			[("movie",2), ("tv",1), ("netflix",1)], maxTime)

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
		fillWithZeros(goodSoln, [("a",3),("b",3),("c",3)], maxTime)

		# Tasks a_1 and b_1 overlap in time on machine 2
		overlapSoln = {"a_0,0":1, "a_1,2":1, "a_2,4":1,
					   "b_0,0":1, "b_1,3":1, "b_2,5":1,
					   "c_0,0":1, "c_1,2":1, "c_2,5":1}
		fillWithZeros(overlapSoln, [("a",3),("b",3),("c",3)], maxTime)

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
		fillWithZeros(goodSoln, [("breakfast",2),("music",1)], maxTime)

		# 'breakfast' tasks are out of order
		badOrderSoln = {"breakfast_0,1":1, "breakfast_1,0":1,
						"music_0,0":1}
		fillWithZeros(goodSoln, [("breakfast",2),("music",1)], maxTime)

		self.assertTrue(jss.csp.check(goodSoln))
		self.assertFalse(jss.csp.check(badOrderSoln))

if __name__ == "__main__":
	unittest.main()
