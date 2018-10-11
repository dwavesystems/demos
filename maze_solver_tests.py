from itertools import islice
import unittest

from dimod.reference.samplers import ExactSolver
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
from maze_solver import maze_bqm

#TODO: Heuristic solutions are not ideal for unit tests. However, these problems are too large for an exact solver.

def compare(self, response, expected):
    """ Comparing response to expected results
    """
    for sample in islice(response.samples(), 1):
        # Comparing variables found in sample and expected
        expected_keys = set(expected.keys())
        sample_keys = set(sample.keys())
        common_keys = expected_keys & sample_keys
        different_keys = expected_keys - sample_keys  # expected_keys is a superset

        # Check that common variables match
        for key in common_keys:
            self.assertEqual(sample[key], expected[key])

        # Check that non-existent 'sample' variables are 0
        for key in different_keys:
            self.assertEqual(expected[key], 0)


#class test_maze_solutions(unittest.TestCase):
def test_small_maze():
    # Create maze
    n_rows = 3
    n_cols = 3
    start = "0,0n"
    end = "3,2n"
    walls = ["1,0n", "0,2w", "2,1n", "2,2n"]
    bqm = maze_bqm(n_rows, n_cols, start, end, walls)

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

test_small_maze()

"""
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
"""
