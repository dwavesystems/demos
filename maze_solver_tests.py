import unittest
from maze-solver import maze_bqm

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