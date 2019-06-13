Map Coloring Demo
===================
A demo on using the D-Wave Ocean SDK to solve the map coloring problem. Namely,
given a map, color the regions of the map such that no two regions sharing a
border would share the same color.

.. figure:: graph.png
  :align: center
  :figclass: align-center
  
  A graph representation of Canada's provinces. Provinces connected by edges
  share a border together. This is a sample output produced by this demo.

Usage
-----
Simply run the code with
::
  python map_coloring.py

Code Overview
-------------
The idea is to describe the map coloring problem in terms of constraints.
Once this is done, we can use tools from the Ocean SDK to convert these
constraints into a binary quadratic model (BQM), a type of equation that can be
ingested by the quantum computer. Afterwards, we will hopefully have a solution
to our map coloring problem.

Constraints to describe the map coloring problem:

* Each region can only select one color
* No regions sharing a border can share a color

Code Specifics
--------------
Why only four colors?
~~~~~~~~~~~~~~~~~~~~~~
* In the code, we let each of the regions choose one among four colors. Why
  are we limiting ourselves to only four colors? According to the `Four Colour
  Theorem <https://en.wikipedia.org/wiki/Four_color_theorem>`_, we need no more
  than four colors to color any map such that no two adjacent regions share
  the same color

License
-------
Released under the Apache License 2.0. See `LICENSE <../LICENSE>`_ file.
