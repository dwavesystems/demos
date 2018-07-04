Demo of Qboost
==============

The D-Wave quantum computer has been widely studied as a discrete optimization engine that accepts
any problem formulated as quadratic unconstrained  binary  optimization  (QUBO). In 2008, Google and
D-Wave published a paper, `Training a Binary Classifier with the Quantum Adiabatic Algorithm`_\ ,
which describes how the `Qboost` ensemble method makes binary classification amenable to quantum
computing: the problem is formulated as a thresholded linear superposition of a set of weak classifiers
and the D-Wave quantum computer is  used to optimize the weights in a learning process that
strives to minimize the training error and number of weak classifiers

This code demonstrates the use of the D-Wave system to solve a binary classification problem using the
Qboost algorithm.

Disclaimer
----------

This demo and its code are intended for demonstrative purposes only and are not
designed for performance.

For state-of-the-art machine learning, please contact Quadrant, the
machine learning business unit of D-Wave Systems.

Setting Up the Demo
----------------------

It's recommended that you work in a `virtual environment`_ on your local machine; depending on
your machine, you may need to first install virtualenv and then create a virtual environment,
for example:

.. code-block:: bash

  virtualenv env
  cd env
  source ./bin/activate

Copy (clone) this Qboost repository to your local machine's newly created virtual environment.

To set up the required dependencies, in the root directory of a copy (clone) of this repository, run the following:

.. code-block:: bash

  pip install -r requirements.txt

Configuring the Demo
--------------------

Access to a D-Wave system must be configured, as described in the `dwave-cloud-client`_ documentation.
A default solver is required.

Running the Demo
----------------

A minimal working example using the main interface function can be seen by running:

.. code-block:: bash

  python demo.py  --wisc --mnist

License
-------

Released under the Apache License 2.0. See LICENSE file.

.. _`dwave-cloud-client`: http://dwave-cloud-client.readthedocs.io/en/latest/#module-dwave.cloud.config
.. _`Training a Binary Classifier with the Quantum Adiabatic Algorithm`: https://arxiv.org/pdf/0811.0416.pdf
.. _`virtual environment`: https://packaging.python.org/guides/installing-using-pip-and-virtualenv
