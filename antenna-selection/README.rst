Demo of Antennas Selection
===========================
This code was taken from the webinar, *Quantum Programming with the Ocean Tools Suite*.

This is a graph representing antenna coverage. Each of the seven nodes below represents
an antenna with some amount of coverage. Note that the coverage provided by each
antenna is identical. The edges between each node represent antennas with overlapping
coverage.

.. image:: readme_imgs/example_original.png

Problem: Given the above set of antennas, which antennas should you choose such that
you maximize antenna coverage without any overlaps?

Solution: One possible solution is indicated by the red nodes below.

.. image:: readme_imgs/example_solution.png

Usage
-----
To run the demo:
::
  python antennas.py

Code Overview
-------------

The program ``antennas.py`` creates a graph using the Python package ``networkx``, and then uses the Ocean software tools to run the ``maximum_independent_set`` function from within the ``dwave_networkx`` package.

Further Information
-------------------
V. Goliber,
"Quantum Programming with the Ocean Tools Suite",
`www.youtube.com/watch?v=ckJ59gsFllU <https://www.youtube.com/watch?v=ckJ59gsFllU>`_

A. Lucas,
"Ising formulations of many NP problems",
`doi: 10.3389/fphy.2014.00005 <https://www.frontiersin.org/articles/10.3389/fphy.2014.00005/full>`_

License
-------
Released under the Apache License 2.0. See `LICENSE <../LICENSE>`_ file.
