Demo of Circuit Fault Diagnosis
===============================

Fault diagnosis is the combinational problem of quickly localizing failures as soon as they are detected in systems.
Circuit fault diagnosis is the problem of identifying a minimum-sized set of components that, if faulty, explains an
observation of incorrect outputs given a set of inputs.

This code demonstrates the use of the D-Wave system to solve such a problem in the case of a three-bit multiplier
circuit. The user is prompted to enter three integers: A and B, the inputs the circuit is expected to multiply, and the
circuit's output, P, which represents either a valid or incorrect product of the inputs.

* :code:`multiplier     ( 0 <= A <=  7)`
* :code:`multiplicand   ( 0 <= B <=  7)`
* :code:`product        ( 0 <= P <= 63)`

General References
------------------

* Z. Bian, F. Chudak, R. B. Israel, B. Lackey, W. G. Macready, and A. Roy, “Mapping constrained optimization problems
  to quantum annealing with application to fault diagnosis,” Frontiers in ICT, vol. 3, p. 14, 2016.
  https://www.frontiersin.org/articles/10.3389/fict.2016.00014/full
* A. Perdomo-Ortiz, J. Fluegemann, S. Narasimhan, R. Biswas, and V. N. Smelyanskiy, “A quantum annealing approach for
  fault detection and diagnosis of graph-based systems,” European Physical Journal Special Topics, vol. 224, Feb. 2015.
  https://arxiv.org/abs/1406.7601v2

Requirements
------------

* An installed SMT solver

  The *circuit-fault-diagnosis-demo* code has a dependency on `penaltymodel_maxgap`_, which requires that an SMT solver
  is installed. The solvers are accessed through the pysmt_ package. See the accompanying *pysmt* documentation for
  installing smt solvers.
* Access to a D-Wave system set up with a `.dwrc`_ file

  :code:`connection label | server url, token, proxy url, default solver name`

  The first connection is used. A default solver is required. For example:

  :code:`connection-one|https://one.com,token-one,,solver-one`

Running the Demo
----------------

The demo constructs a binary quadratic model and `qbsolv's`_ tabu search to solve the problem **classically**. The
algorithm returns a minimum fault diagnosis and the number of distinct fault states it found.

.. code-block:: bash

  pip install -r requirements.txt
  pysmt-install --z3

accept the license terms when prompted

.. code-block:: bash

  eval $(pysmt-install --env)
  python demo.py

The :code:`--verbose` option will display the status (valid/fault) of each component for each minimum fault diagnosis.

Running the Demo with the QPU
-----------------------------

The demo constructs a binary quadratic model and minor-embeds it on the **D-Wave system**. The system returns a minimum
fault diagnosis and the number of distinct fault states it found.

**Note that the only difference from running the demo classically is the requirements file used.**

.. code-block:: bash

  pip install -r requirements_qpu.txt
  pysmt-install --z3

accept the license terms when prompted

.. code-block:: bash

  eval $(pysmt-install --env)
  python demo.py

The :code:`--verbose` option will display the status (valid/fault) of each component for each minimum fault diagnosis.

Interesting Use Cases
---------------------

A single faulty component leads to five incorrect bits in the product's six bits (due to the commutative property of
multiplication, these are two isomorphic sets) in these four cases:

* :code:`A = 6; B = 5; P = 32`
* :code:`A = 5; B = 6; P = 32`
* :code:`A = 7; B = 4; P = 34`
* :code:`A = 4; B = 7; P = 34`

Two faulty components lead to all the product's six bits being incorrect (this is due to the least significant bit being
determined solely by one AND gate) in these four cases:

* :code:`A = 6; B = 5; P = 33`
* :code:`A = 5; B = 6; P = 33`
* :code:`A = 7; B = 4; P = 35`
* :code:`A = 4; B = 7; P = 35`

Four faulty components, which is the maximum number of faulty components for a minimum fault diagnosis for this circuit,
lead to five incorrect bits in the product's six bits in this case (one of many such cases):

* :code:`A = 7; B = 6; P = 1`.

In general, the number of incorrect bits in the product is greater than or equal to the number of faulty components.

License
-------

Released under the Apache License 2.0. See LICENSE file.

.. _`penaltymodel_maxgap`: https://github.com/dwavesystems/penaltymodel_maxgap
.. _pysmt: https://github.com/pysmt/pysmt
.. _`.dwrc`: http://dwave-micro-client.readthedocs.io/en/latest/#configuration
.. _`qbsolv's`: https://github.com/dwavesystems/qbsolv