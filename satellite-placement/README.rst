Satellite Placement Demo
========================
A demo on how to group a set of satellites into constellations of
size x, such that the average coverage of each constellation is maximized.

An alternate interpretation of this code could be: how do you group your class
of students into teams of size x, such that you maximize the average
performance of each team?

Usage
-----
To run the demo,
::
  python satellite.py

It will print out a set of satellite constellations.

Code Overview
-------------
The idea is to consider all possible combinations of satellites, eliminate
constellations with particularly low coverage, and encourage certain
properties in our final solution. Namely, we want to encourage:

* Constellations that have better coverage
* Satellites to only join *one* constellation
* A specific number of constellations in our final solution

Code Specifics
--------------

* The ``score_threshold`` - used to determine bad constellations - was
  assigned an arbitrarily picked number
* In ``bqm.add_variable(frozenset(constellation), -score)``, we are using
  ``frozenset(constellation)`` rather than simply ``constellation`` because
  (1) we want our ``constellation`` variable to be a set (i.e. the order of the
  satellites in a constellation should not matter.
  ``{'a', 'b', 'c'} == {'c','a','b'}``) and (2) ``add_variable(..)`` needs its
  variables to be immutable (hence a ``frozenset`` rather than simply ``set``.

References
----------
G. Bass, C. Tomlin, V. Kumar, P. Rihaczek, J. Dulny III.
Heterogeneous Quantum Computing for Satellite Constellation Optimization:
Solving the Weighted K-Clique Problem. 2018 Quantum Sci. Technol. 3 024010.
https://arxiv.org/abs/1709.05381

License
-------
Released under the Apache License 2.0. See `LICENSE <../LICENSE>`_ file.
