Demo of Factoring
=================

Factoring is...

This code demonstrates the use of the D-Wave system to solve such a problem in the case of a three-bit multiplier
circuit. The user is prompted to enter an integer: P, which represents either a product to be factored.

.. code-block::

  Input product        ( 0 <= P <= 63):

The algorithm returns possible A and B, which are the inputs the circuit multiplies to calculate the product, P.

Running the Demo
----------------

You can run the demo on classical hardware (a CPU) or on a D-Wave QPU, with the selection made by the pip requirements
file used.

.. code-block:: bash

  pip install -r requirements_cpu.txt                                                     # to run on CPU
  pip install -r requirements_qpu.txt --extra-index-url https://pypi.dwavesys.com/simple  # to run on QPU

The demo code has a dependency on `penaltymodel_maxgap`_, which requires that an SMT solver is installed. The solvers
are accessed through the pysmt_ package. See the accompanying *pysmt* documentation for installing smt solvers.

Running on a CPU
~~~~~~~~~~~~~~~~

The demo constructs a binary quadratic model and uses `qbsolv's`_ tabu search to solve the problem classically.

First, install the required files:

.. code-block:: bash

  pip install -r requirements_cpu.txt

Use :code:`pysmt-install` as outlined in the `pysmt installation instructions`_ to setup an smt solver.

Note: For Windows, ``z3`` is currently the only supported solver.

.. code-block:: bash

  python demo.py

Running on a QPU
~~~~~~~~~~~~~~~~

The demo constructs a binary quadratic model and minor-embeds it on the D-Wave system.

Access to a D-Wave system must be configured, as described in the `dwave-cloud-client`_ documentation. A default solver
is required.

First, install the required files:

.. code-block:: bash

  pip install -r requirements_qpu.txt --extra-index-url https://pypi.dwavesys.com/simple

Use :code:`pysmt-install` as outlined in the `pysmt installation instructions`_ to setup an smt solver.

Note: For Windows, ``z3`` is currently the only supported solver.

.. code-block:: bash

  python demo.py

License
-------

Released under the Apache License 2.0. See LICENSE file.

.. _`penaltymodel_maxgap`: https://github.com/dwavesystems/penaltymodel_maxgap
.. _pysmt: https://github.com/pysmt/pysmt
.. _`qbsolv's`: https://github.com/dwavesystems/qbsolv
.. _`dwave-cloud-client`: http://dwave-cloud-client.readthedocs.io/en/latest/#module-dwave.cloud.config
.. _z3: https://github.com/Z3Prover/z3
.. _`pysmt installation instructions`: https://github.com/pysmt/pysmt#installation
