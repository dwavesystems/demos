Sudoku Demo
===========
A demo on how to solve a Sudoku puzzle with D-Wave Ocean.

Code Overview
-------------
The idea is to describe the Sudoku puzzle as a set of constraints that our
solution needs to satisfy (i.e. we are posing the puzzle as a constraint
satisfaction problem). By laying down these constraints, our solver can
optimize over them and hopefully return a solution that satisfies all
our constraints.

There are several constraints in Sudoku:

* Each cell in the Sudoku array must contain one digit
* Each row may not have duplicate digits
* Each column may not have duplicate digits
* Each sub-square may not have duplicate digits

Code Specifics
--------------
Inputs
~~~~~~
* The Sudoku puzzle needs to be given as a text file
* The text file should only contain the puzzle (i.e. don't add comments)
* Each Sudoku cell value in the text file is separated with a space
* Empty Sudoku cells should be represented with 0
* For example,
  ::
    5 0 0 8 3 1 0 6 0
    3 0 0 0 9 2 0 0 5
    0 0 4 0 7 6 0 2 0
    0 2 0 0 6 7 1 0 0
    9 0 0 0 0 0 0 0 4
    0 0 6 9 4 0 0 3 0
    0 4 0 2 8 0 7 0 0
    2 0 0 7 1 0 0 0 6
    0 7 0 6 5 3 0 0 9
 
Comments on the variables
~~~~~~~~~~~~~~~~~~~~~~~~~
* For a Sudoku puzzle with ``n`` by ``n`` cells, it requires that each
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
  runs multiple solvers in parallel and combines their solutions together
* We are using Kerberos because it can break down our problem into smaller
  chunks that could then be solved by our solvers. These smaller solutions
  are then composed together, resulting to our final solution
