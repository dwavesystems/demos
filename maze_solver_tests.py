from itertools import islice
import unittest

from dimod.reference.samplers import ExactSolver
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
from maze_solver import maze_bqm
from neal import SimulatedAnnealingSampler

#TODO: Heuristic solutions are not ideal for unit tests. However, these problems are too large for an exact solver.
def compare(self, response, expected):
    """Comparing response to expected results
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


class TestMazeSolverConstraints(unittest.TestCase):
    def test_sum_to_zero_or_two_constraint(self):
        pass

    def test_boarders_constraint(self):
        pass

class TestMazeSolverResponse(unittest.TestCase):
    #TODO: compare response with expected solution
    def test_small_maze(self):
        # Create maze
        n_rows = 3
        n_cols = 3
        start = "0,0n"
        end = "3,2n"
        walls = ["1,0n", "0,2w", "2,1n", "2,2n"]
        bqm = maze_bqm(n_rows, n_cols, start, end, walls)

        # Sample
        sampler = SimulatedAnnealingSampler()
        response = sampler.sample(bqm)
        self.assertGreaterEqual(len(response), 1)

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

if __name__ == "__main__":
    unittest.main()
