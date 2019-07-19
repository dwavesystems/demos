Sudoku Demo
===========
A demo on how to solve a Sudoku puzzle with D-Wave Ocean.

Usage
-----
``python sudoku.py <sudoku file path>``

For example,
::
    python sudoku.py problem.txt

Code Overview
-------------
The idea is to describe the Sudoku puzzle as a set of constraints that our
solution needs to satisfy (i.e. we are posing the puzzle as a constraint
satisfaction problem). By laying down these constraints, we can get our solver
to optimize over them and hopefully return a solution that satisfies all
our constraints.

There are several constraints in Sudoku:

* Each cell in the Sudoku array must contain one digit
* No row may have duplicate digits
* No column may have duplicate digits
* No sub-square may have duplicate digits

Code Specifics
--------------
Input
~~~~~
The code takes as its input a text file containing a Sudoku puzzle in
the following format:

* Rows of the puzzle are represented as a sequence of lines, one per row
* Cells in each row of the puzzle are represented as space-separated integers
* Empty cells are represented by zeros
* The file should not contain any additional lines (e.g. headers) or comments

For example,
::
  8 2 0 9 1 0 0 0 7
  9 0 0 7 0 6 8 1 2
  0 1 7 8 0 0 0 9 0
  0 8 0 0 0 0 9 7 0
  0 5 2 0 9 3 1 8 0
  6 0 0 1 8 7 0 0 0
  0 7 8 0 0 9 0 5 0
  3 0 0 2 5 0 7 6 0
  5 0 9 3 0 1 2 0 8
 
Comments on the variables
~~~~~~~~~~~~~~~~~~~~~~~~~
* A Sudoku puzzle with ``n`` by ``n`` cells requires that each
  row, column, and sub-square have ``n`` unique values. Since the
  sub-square is a square matrix with ``n`` items, it means that ``n``
  must be a square number (i.e. for a sub-square of size ``m`` by ``m``,
  ``m * m = n``). Hence in the code, the variables ``n`` and ``m``
  represent:
  ::
    n == number of rows == number of columns
    m == sqrt(n) == number of sub-square rows == number of sub-square columns
 
Comments on the solver
~~~~~~~~~~~~~~~~~~~~~~
* We are using a hybrid solver called Kerberos (specifically,
  ``hybrid.reference.KerberosSampler``). It is a hybrid solver because it
  combines classical and quantum resources together
* We are using Kerberos because it can break down our problem into smaller
  chunks that could then be solved by our quantum computer. The quantum
  and classical solutions are then combined together, resulting in our final
  solution

License
-------
Released under the Apache License 2.0. See `LICENSE <../LICENSE>`_ file.
