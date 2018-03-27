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

The demo constructs a binary quadratic model and minor-embeds it on the D-Wave system.

Access to a D-Wave system must be configured, as described in the `dwave-cloud-client`_ documentation. A default solver
is required.

.. code-block:: bash

  pip install . --extra-index-url https://pypi.dwavesys.com/simple
  python demo.py

License
-------

Released under the Apache License 2.0. See LICENSE file.

.. _`dwave-cloud-client`: http://dwave-cloud-client.readthedocs.io/en/latest/#module-dwave.cloud.config
