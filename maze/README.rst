Maze Solver Demo
================
Getting the D-Wave Quantum Computer to solve a maze!

The purpose of this demo is to take a simple and familiar problem - solving a maze - and go through
the steps of submitting the problem to the quantum computer.

Code Overview
-------------
The idea is to describe the rules of how one can move through a maze with a set of constraints.
Using the Ocean toolkit, these constraints can be converted into a binary quadratic model (BQM)
that can then be solved with a D-Wave quantum computer. The solution that gets returned by the
quantum computer is the path needed to get through the maze.

There are several constraints involved with a maze:
* Specify valid path moves (ie if the path enters a grid point, it must also leave said grid point)
* Path has a specific start and end position
* Path cannot go beyond the border of the maze
* Path cannot go through the walls within the maze

Each of these constraints are implemented by the `maze` functions: `_apply_valid_move_constraint()`,
`_set_start_and_end()`, `_set_borders()`, and `_set_inner_walls()`, respectively. These functions
are called when the user calls `get_maze_bqm(..)` in Example below.

Code Specifics
--------------
The maze is a rectangular grid. The path segments (aka edges) that can be formed in this grid are
described with respect to a grid point.

Consider the edge labelled `'1,0w'`:
* `1,0` refers to grid point on row 1, column 0
* `w` refers to "west"
* Hence, if you imagine a compass that is centered at position `1,0`, the edge `'1,0w'` is the
west "spoke" of this compass

Note that the code only accepts edge inputs in the north direction (`'<row>,<col>n'`) and the west
direction (`'<row>,<col>w'`). So if edges in the south or east directions are needed, please rewrite
in terms of north and west. Namely,
.. code-block::
  '<row>,<col>s' == '<row+1>,<col>n'
  '<row>,<col>e' == '<row>,<col+1>w'

Example
-------
.. code-block:: python

  from maze import get_maze_bqm
  from dwave.system.samplers import DWaveSampler
  from dwave.system.composites import EmbeddingComposite

  # Create maze
  n_rows = 2
  n_cols = 2
  start = '0,0n'
  end = '1,0w'
  walls = ['1,1n']

  # Get bqm
  bqm = get_maze_bqm(n_rows, n_cols, start, end, walls)

  # Submit bqm to a D-Wave Sampler
  sampler = EmbeddingComposite(DWaveSampler())
  result = sampler.sample(bqm, num_reads=1000)
  print(result)

.. code-block::
   1,0n  0,1w  1,1w  energy  num_occ.  chain_b.
0     1     0     0    -3.5      1000       0.0

