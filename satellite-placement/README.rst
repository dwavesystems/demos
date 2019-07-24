Satellite Placement Demo
========================
A demo on how to group a fleet of satellites into constellations of size x,
such that the average coverage of each constellation is maximized.

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
particularly "bad" constellations, and enforce rules on the final solution.
These rules (or constraints) will:

* Favour constellations with better coverage
* Encourage satellites to only join *one* constellation
* Only allow a limited number of constellations to be chosen

Code Specifics
--------------

* The ``score_threshold`` - used to determine "bad" constellations - was assigned an arbitrarily picked number
* In ``bqm.add_variable(frozenset(constellation), -score)``, we are using
``frozenset`` because ...?

References
----------
G. Bass, C. Tomlin, V. Kumar, P. Rihaczek, J. Dulny III.
Heterogeneous Quantum Computing for Satellite Constellation Optimization:
Solving the Weighted K-Clique Problem. 2018 Quantum Sci. Technol. 3 024010.
https://arxiv.org/abs/1709.05381

License
-------
Released under the Apache License 2.0. See `LICENSE <../LICENSE>`_ file.
