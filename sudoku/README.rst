Sudoku Demo
===========

A demo on how to solve a Sudoku with D-Wave Ocean.

Code Overview
-------------
The idea is to pose the Sudoku puzzle as a constraint satisfaction problem
(CSP). By laying down these constraints, our solver can optimize over them and
hopefully return a solution that satisfies all our constraints.

There are several constraints in Sudoku:
- Each cell in the sudoku array must contain one digit
- Each row may not have duplicate digits
- Each column may not have duplicate digits
- Each sub-square may not have duplicate digits

Code Specifics
--------------
Inputs
~~~~~~

Comments on variables and labels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

References
----------


