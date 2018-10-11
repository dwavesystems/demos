from __future__ import print_function

import dwavebinarycsp as dbc
from dimod.reference.samplers import ExactSolver
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite


def get_grid(n_rows, n_cols):
    positions = []  # Positions in the maze
    directions = []  # Edge nodes; the four directions of each position
    for i in range(n_rows):
        for j in range(n_cols):
            curr = str(i) + "," + str(j)
            positions.append(curr)
    return positions


def equal(a, b):
    return a == b


def sum_to_two_or_zero(*args):
    sum_value = sum(args)
    return sum_value in [0, 2]


def maze_bqm(n_rows, n_cols, start, end, walls):
    positions = get_grid(n_rows, n_cols)

    # Make constraints
    csp = dbc.ConstraintSatisfactionProblem(dbc.BINARY)

    # Constraint: Enforce North/South, East/West rule
    # (ie Row above's south is row below's north. Likewise with east and west)
    for i in range(0, n_rows - 1):
        for j in range(n_cols):
            above_node = str(i) + "," + str(j) + "s"
            below_node = str(i + 1) + "," + str(j) + "n"
            csp.add_constraint(equal, [above_node, below_node])

    for i in range(n_rows):
        for j in range(0, n_cols - 1):
            left_node = str(i) + "," + str(j) + "e"
            right_node = str(i) + "," + str(j + 1) + "w"
            csp.add_constraint(equal, [left_node, right_node])

    # Constraint: Each eNode's N,S,E,W must sum to zero or two
    for pos in positions:
        directions = {pos + "n", pos + "s", pos + "e", pos + "w"}
        csp.add_constraint(sum_to_two_or_zero, directions)

    # TODO: Have a way for user to easily set up walls, start and end
    # Constraint: Start and end locations
    csp.fix_variable(start, 1)  # start location
    csp.fix_variable(end, 1)  # end location

    # Constraint: No walking through boarders of the maze
    for j in range(n_cols):
        top_boarder = "0," + str(j) + "n"
        bottom_boarder = str(n_rows - 1) + "," + str(j) + "s"

        try:
            csp.fix_variable(top_boarder, 0)
        except ValueError:
            if not top_boarder in [start, end]:
                raise ValueError

        try:
            csp.fix_variable(bottom_boarder, 0)
        except ValueError:
            if not bottom_boarder in [start, end]:
                raise ValueError

    for i in range(n_rows):
        left_boarder = str(i) + ",0" + "w"
        right_boarder = str(i) + "," + str(n_cols - 1) + "e"

        try:
            csp.fix_variable(left_boarder, 0)
        except ValueError:
            if not left_boarder in [start, end]:
                raise ValueError

        try:
            csp.fix_variable(right_boarder, 0)
        except ValueError:
            if not right_boarder in [start, end]:
                raise ValueError

    # Constraint: Inner walls of the maze
    for wall in walls:
        csp.fix_variable(wall, 0)

    bqm = dbc.stitch(csp)
    print(bqm)

    # Sample
    sampler = EmbeddingComposite(DWaveSampler())
    response = sampler.sample(bqm, num_reads=10000)
    # sampler = ExactSolver()
    # response = sampler.sample(bqm)
    for i, (sample, energy, n_occurences, chain_break_fraction) in enumerate(response.data()):
        if i == 3:
            break

        print("Energy: ", str(energy))

        keys = sample.keys()
        for key in sorted(keys):
            print(key, ": ", str(sample[key]))

        print("")


def small_maze():
    n_rows = 3
    n_cols = 3
    start = "0,0n"
    end = "2,2s"
    walls = ["0,0s", "0,1e", "1,1s", "1,2s"]
    maze_bqm(n_rows, n_cols, start, end, walls)


def medium_maze():
    n_rows = 4
    n_cols = 4
    start = "3,1s"
    end = "1,3e"
    walls = ["0,1s", "0,2s", "1,2e", "1,3s", "2,0n", "2,1n", "2,2w", "3,1n", "3,3n"]
    maze_bqm(n_rows, n_cols, start, end, walls)


def large_maze():
    # Maze is probably too large. Got error "ValueError: no embedding found"
    # On top of 4 directions for the 5*6 maze positions, there were 30+
    # auxiliary variables.
    n_rows = 6
    n_cols = 5
    start = "5,1s"
    end = "2,4e"
    walls = ["0,0s", "0,2s", "0,3s", "1,0e", "1,3e", "2,1n", "2,2n", "2,2e",
             "2,3e", "2,4s", "3,1w", "3,1e", "3,2e", "3,2s", "3,3s", "4,1w", "5,1n",
             "5,2n", "5,2e", "5,4n"]
    maze_bqm(n_rows, n_cols, start, end, walls)


small_maze()
