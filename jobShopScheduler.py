from bisect import bisect_right
from itertools import islice

from dimod import ExactSolver
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
import dwavebinarycsp as dbc
from neal import SimulatedAnnealingSampler

def sumToOne(*args):
	return sum(args) == 1	

class Task():
	def __init__(self, job, position, machine, timeSpan):
		self.job = job
		self.pos = position
		self.mach = machine
		self.span = timeSpan
	
	def __str__(self):
		#TODO: could do better a differentiating strings and numbers
		job = "job: " + str(self.job)
		pos = "pos: " + str(self.pos)
		mach = "mach: " + str(self.mach)
		span = "span: " + str(self.span)
		taskStr = ", ".join([job, pos, mach, span])

		return "{" + taskStr + "}"

class KeyList():
	""" A wrapper to an array. Used for passing the key of a custom object
	to the bisect function.

	Note: bisect function does not let you choose an artbitrary key, hence
	this class was created.
	"""
	def __init__(self, array, keyFn):
		self.array = array	# An iterable
		self.keyFn = keyFn	# Function for grabbing the key of a given item

	def __len__(self):
		return len(self.array)

	def __getitem__(self, index):
		item = self.array[index]
		key = self.keyFn(item)
		return key

#TODO: put asserts to validate jobs
class JobShopScheduler():
	def __init__(self, jobDict, maxTime=None):
		self.tasks = []
		self.maxTime = maxTime
		self.csp = dbc.ConstraintSatisfactionProblem(dbc.BINARY)

		# Populates self.tasks and self.maxTime
		self._processData(jobDict)
		
	def _processData(self, jobs):
		""" Process user input into a format that is more convenient for
		JobShopScheduler functions.
		"""
		# Create and concatenate Task objects
		tasks = []
		totalTime = 0	# total time of all jobs
		for jName, jTasks in jobs.items():
			for i, (machine, timeSpan) in enumerate(jTasks):
				tasks.append(Task(jName, i, machine, timeSpan))	
				totalTime += timeSpan

		# Update values
		self.tasks = tasks
		if self.maxTime is None:
			self.maxTime = totalTime

	def _getLabel(self, task, time):
		""" Creates a standardized name for variables in the constraint
		satisfaction problem, self.csp.
		"""
		name = str(task.job) + "_" + str(task.pos)
		return name + "," + str(time)

	def _addOneStartConstraint(self):
		""" self.csp gets the constraint: A task can start once and only once
		"""
		for task in self.tasks:
			taskTimes = {self._getLabel(task, t) for t in xrange(self.maxTime)}
			self.csp.add_constraint(sumToOne, taskTimes)

	def _addPrecedenceConstraint(self):
		""" self.csp gets the constraint: Task must follow a particular order
		Note: assumes self.tasks are sorted by jobs and then by position
		"""
		validEdges = {(0,0),(1,0),(0,1)}
		for i, cTask in enumerate(self.tasks[:-1]):
			nTask = self.tasks[i+1]	
	
			if cTask.job != nTask.job:
				continue
	
			# Forming constraints with the relevant times of the next task
			for t in xrange(self.maxTime):
				cLabel = self._getLabel(cTask, t)
	
				for tt in xrange(min(t+cTask.span, self.maxTime)):
					nLabel = self._getLabel(nTask, tt)
					self.csp.add_constraint(validEdges, {cLabel, nLabel})

	def _addShareMachineConstraint(self):
		""" self.csp gets the constraint: At most one task per machine per time
		"""
		sortedTasks = sorted(self.tasks, key=lambda x: x.mach)
		wrappedTasks = KeyList(sortedTasks, lambda x: x.mach) # Key wrapper
	
		head = 0
		validValues = {(0,0),(1,0),(0,1)}
		while head < len(sortedTasks):
	
			# Find tasks that share a machine
			tail = bisect_right(wrappedTasks, sortedTasks[head].mach)
			sameMachTasks = sortedTasks[head:tail]
	
			# Update
			head = tail
	
			# No need to build coupling for a single task
			if len(sameMachTasks) < 2:
				continue
	
			# Apply constraint between all tasks for each unit of time
			for task in sameMachTasks:
				for otherTask in sameMachTasks:
					if task.job == otherTask.job and task.pos == otherTask.pos:
						continue
	
					for t in xrange(self.maxTime):
						currLabel = self._getLabel(task, t)
	
						for tt in xrange(t, min(t+task.span, self.maxTime)):
							self.csp.add_constraint(validValues,\
								{currLabel, self._getLabel(otherTask, tt)})

	def _removeAbsurdTimes(self):
		""" Sets impossible task times in self.csp to 0.
		"""
		#TODO: deal with overlaps in time
		for task in self.tasks:
			# Times that are too early for task
			for t in xrange(task.pos):
				label = self._getLabel(task, t)
				self.csp.fix_variable(label, 0)
	
			# Times that are too late for task to complete
			for t in xrange(task.span - 1):	# -1 to ignore span==1
				label = self._getLabel(task, (self.maxTime-1) - t) # -1 for zero-indexed time
				self.csp.fix_variable(label, 0)			

	def solve(self, sampler=None):
		""" Returns a response to the Job Shop Scheduling problem. Default
		sampler is simulated annealing.
		args:
			sampler: String. {"qpu", "exact", "sa"}
		"""
		# Apply constraints to self.csp
		self._addOneStartConstraint()
		self._addPrecedenceConstraint()
		self._addShareMachineConstraint()
		self._removeAbsurdTimes()
	
		# Get BQM
		bqm = dbc.stitch(self.csp)
	
		# Sample
		if sampler == "qpu":
			samp = EmbeddingComposite(DWaveSampler())
			response = samp.sample(bqm, num_reads=1000)

		elif sampler == "exact":
			samp = ExactSolver()
			response = samp.sample(bqm)

		else:
			samp = SimulatedAnnealingSampler()
			response = samp.sample(bqm, num_reads=100)

		return response, self.csp


def demo():
	# Solve JSS
	# Assumes that there are no tasks with non-positive processing times.
	jobs = {"j0":[(1,2),(2,2),(3,2)],                                           
			"j1":[(3,3),(2,1),(1,1)],                                           
			"j2":[(2,2),(1,3),(2,1)]}                                           
	nSamples = 1
	maxTime = 6

	scheduler = JobShopScheduler(jobs, maxTime)
	response, csp = scheduler.solve()

	# Print response
	for sample, energy, nOccurences in islice(response.data(), nSamples):
		print "energy: ", energy     
		print "check: ", csp.check(sample)

		for key in sorted(sample.keys()):
			print key, ": ", sample[key]
		print ""

if __name__ == "__main__":
	demo()
