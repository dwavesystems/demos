from __future__ import print_function

import dwavebinarycsp as dbc
from dimod.reference.samplers import ExactSolver
from dwave.system.samplers import DWaveSampler 
from dwave.system.composites import EmbeddingComposite

def getGrid(nRows, nCols):
	positions = []		# Positions in the maze
	directions = []		# Edge nodes; the four directions of each position
	for i in range(nRows):
		for j in range(nCols):
			curr = str(i) + "," + str(j)
			positions.append(curr)
	return positions

def equal(a, b):
	return a==b

def sumToTwoOrZero(*args):
	sumValue = sum(args)
	return sumValue in [0, 2]
	

def mazeBQM(nRows, nCols, start, end, walls):
	positions = getGrid(nRows, nCols)

	# Make constraints
	csp = dbc.ConstraintSatisfactionProblem(dbc.BINARY)

	# Constraint: Enforce North/South, East/West rule
	# (ie Row above's south is row below's north. Likewise with east and west)
	for i in range(0, nRows-1):
		for j in range(nCols):
			aboveNode = str(i) + "," + str(j) + "s"
			belowNode = str(i+1) + "," + str(j) + "n"
			csp.add_constraint(equal, [aboveNode, belowNode])

	for i in range(nRows):
		for j in range(0, nCols-1):
			leftNode = str(i) + "," + str(j) + "e"		
			rightNode = str(i) + "," + str(j+1) + "w"		
			csp.add_constraint(equal, [leftNode, rightNode])
	
	# Constraint: Each eNode's N,S,E,W must sum to zero or two
	for pos in positions:
		directions = {pos+"n", pos+"s", pos+"e", pos+"w"}
		csp.add_constraint(sumToTwoOrZero, directions)	

	#TODO: Have a way for user to easily set up walls, start and end
	# Constraint: Start and end locations
	csp.fix_variable(start, 1)		# start location
	csp.fix_variable(end, 1)		# end location
	
	# Constraint: No walking through boarders of the maze
	for j in range(nCols):
		topBoarder = "0," + str(j) + "n"
		bottomBoarder = str(nRows-1) + "," + str(j) + "s"

		try:
			csp.fix_variable(topBoarder,0)	
		except ValueError:
			if not topBoarder in [start, end]:
				raise ValueError

		try:
			csp.fix_variable(bottomBoarder,0)	
		except ValueError:
			if not bottomBoarder in [start, end]:
				raise ValueError

	for i in range(nRows):
		leftBoarder = str(i) + ",0" + "w"
		rightBoarder = str(i) + "," + str(nCols-1) + "e"

		try:
			csp.fix_variable(leftBoarder, 0)	
		except ValueError:
			if not leftBoarder in [start, end]:
				raise ValueError

		try:
			csp.fix_variable(rightBoarder,0)	
		except ValueError:
			if not rightBoarder in [start, end]:
				raise ValueError

	# Constraint: Inner walls of the maze
	for wall in walls:
		csp.fix_variable(wall, 0)

	bqm = dbc.stitch(csp)
	print(bqm)

	# Sample
	sampler = EmbeddingComposite(DWaveSampler())
	response = sampler.sample(bqm, num_reads=10000)
	#sampler = ExactSolver()
	#response = sampler.sample(bqm)
	for i, (sample, energy, nOccurences, chainBreakFraction) in enumerate(response.data()):
		if i==3:
			break

		print("Energy: ", str(energy))

		keys = sample.keys()
		for key in sorted(keys):
			print(key, ": ", str(sample[key]))

		print("")


def smallMaze():
	nRows = 3
	nCols = 3
	start = "0,0n"
	end = "2,2s"
	walls = ["0,0s", "0,1e", "1,1s", "1,2s"]
	mazeBQM(nRows, nCols, start, end, walls)

def mediumMaze():
	nRows = 4
	nCols = 4
	start = "3,1s"
	end = "1,3e"
	walls = ["0,1s","0,2s","1,2e","1,3s","2,0n","2,1n","2,2w","3,1n","3,3n"]
	mazeBQM(nRows, nCols, start, end, walls)

def largeMaze():
	# Maze is probably too large. Got error "ValueError: no embedding found"
	# On top of 4 directions for the 5*6 maze positions, there were 30+
	# auxiliary variables.
	nRows = 6
	nCols = 5
	start = "5,1s"
	end = "2,4e"
	walls = ["0,0s", "0,2s", "0,3s", "1,0e", "1,3e","2,1n","2,2n","2,2e",
			"2,3e","2,4s","3,1w","3,1e","3,2e", "3,2s","3,3s","4,1w","5,1n",
			"5,2n","5,2e","5,4n"]
	mazeBQM(nRows, nCols, start, end, walls)

smallMaze()
