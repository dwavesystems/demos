Demo of Factoring
=================

Integer factoring is the decomposition of an integer into factors that, when multiplied together, give the original
number. For example, the factors of 15 are 3 and 5.
 
D-Wave quantum computers allow us to factor numbers in an entirely new way, by turning a multiplication circuit into a
constraint satisfaction problem that allows the quantum computer to compute inputs from a predefined output.
Essentially, this means running the multiplication circuit in reverse!

A Boolean logic circuit is usually viewed as computing outputs from inputs based on the logic of the gates.  However,
the problem can also be thought of as seeking an assignment of values to the inputs and outputs consistent with the
logic of all the gates in the circuit.  This perspective of  constraint satisfaction has no directionality. That is,
input values do not need to flow through a series of gates to yield a result, as they do in a multiplication circuit.

This code demonstrates the use of the D-Wave system to solve such a problem in the case of a three-bit multiplier
circuit.

Running the Demo
----------------

The demo constructs a binary quadratic model and minor-embeds it on the D-Wave system.

To setup the required dependencies, in the root directory of a copy of this repository, run the following:

.. code-block:: bash

  pip install . --extra-index-url https://pypi.dwavesys.com/simple

Access to a D-Wave system must be configured, as described in the `dwave-cloud-client`_ documentation. A default solver
is required.

The penalty model cache file (env/data/dwave-penaltymodel-cache/penaltymodel_cache_v0.2.0.db) must be placed in the
appropriate location for the given OS and virtual environment configuration. This location can be found as follows:

.. code-block:: python

  >>> from penaltymodel_cache import cache_file
  >>> cache_file()
  '/home/bellert/git_root/factoring-demo/env/data/dwave-penaltymodel-cache/penaltymodel_cache_v0.2.0.db'
  
A minimal working example using the main interface function can be seen by running:

.. code-block:: bash

  python demo.py
  
The user is prompted to enter a six-bit integer: P, which represents a product to be factored.

.. code-block::

  Input product        ( 0 <= P <= 63):

The algorithm returns possible A and B values, which are the inputs the circuit multiplies to calculate the product, P.

License
-------

Released under the Apache License 2.0. See LICENSE file.

.. _`dwave-cloud-client`: http://dwave-cloud-client.readthedocs.io/en/latest/#module-dwave.cloud.config
