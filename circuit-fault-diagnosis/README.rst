Demo of Circuit Fault Diagnosis
===============================
Fault diagnosis is the combinational problem of quickly localizing failures as soon as they are detected in systems.
Circuit fault diagnosis is the problem of identifying a minimum-sized set of components that, if faulty, explains an
observation of incorrect outputs given a set of inputs.

Usage
-----
Run ``demo.py`` and then follow the on-screen instructions.
::
  python demo.py

Code Overview
-------------
This code demonstrates the use of the D-Wave system to solve such a problem in the case of a three-bit multiplier
circuit. The user is prompted to enter three integers: A and B, which are the inputs the circuit is expected to
multiply, and the circuit's output, P, which represents either a valid or incorrect product of the inputs.

.. code-block::

  Input multiplier     ( 0 <= A <=  7):
  Input multiplicand   ( 0 <= B <=  7):
  Input product        ( 0 <= P <= 63):

The algorithm returns the minimum fault diagnosis (the smallest number of faulty components it found to cause the given
inputs and product) and the number of distinct fault states with this many faults it observed.

Code Specifics
--------------

Advanced Options
~~~~~~~~~~~~~~~~

The :code:`--verbose` option displays the valid/fault status of each component for each minimum fault diagnosis.

.. code-block:: bash

  python demo.py --verbose

Interesting Use Cases
---------------------

A single faulty component leads to five incorrect bits in the product's six bits (due to the commutative property of
multiplication, these are two isomorphic sets) in these four cases:

.. code-block::

  A = 6; B = 5; P = 32
  A = 5; B = 6; P = 32
  A = 7; B = 4; P = 34
  A = 4; B = 7; P = 34

Two faulty components lead to all the product's six bits being incorrect (this is due to the least significant bit being
determined solely by one AND gate) in these four cases:

.. code-block::

  A = 6; B = 5; P = 33
  A = 5; B = 6; P = 33
  A = 7; B = 4; P = 35
  A = 4; B = 7; P = 35

Four faulty components, which is the maximum number of faulty components for a minimum fault diagnosis for this circuit,
lead to five incorrect bits in the product's six bits in this case (one of many such cases):

.. code-block::

  A = 7; B = 6; P = 1

In general, the number of incorrect bits in the product is greater than or equal to the number of faulty components.

References
----------

Z. Bian, F. Chudak, R. B. Israel, B. Lackey, W. G. Macready, and A. Roy, “Mapping constrained optimization problems to quantum annealing with application to fault diagnosis,” Frontiers in ICT, vol. 3, p. 14, 2016.
https://www.frontiersin.org/articles/10.3389/fict.2016.00014/full

A. Perdomo-Ortiz, J. Fluegemann, S. Narasimhan, R. Biswas, and V. N. Smelyanskiy, “A quantum annealing approach for fault detection and diagnosis of graph-based systems,” European Physical Journal Special Topics, vol. 224, Feb. 2015.
https://arxiv.org/abs/1406.7601v2

License
-------
Released under the Apache License 2.0. See `LICENSE <../LICENSE>`_ file.

