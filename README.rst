Demo of Qboost
==============

D-Wave quantum computer has been widely studied as a discrete optimization engine that accepts any problem formulated as quadratic unconstrained binary optimization (QUBO). In 2008, Google and D-Wave published a paper describing an algorithm to make binary classification amenable to quantum computing, namely the Qboost algorithm Training a Binary Classifier with the Quantum Adiabatic Algorithm.

In Qboost, the problem is formulated as a thresholded linear superposition of a set of weak classifiers. D-Wave quantum computer is then used to optimize the weights in a learning process that strives to minimize the training error as well as the number of weak classifiers used.



Setting up of the demo
----------------------

Copy (clone) this qboost repository to your local machine

To set up the required dependencies, in the root directory of a copy (clone) of this repository, run the following:

.. code-block:: bash

  virtualenv env

  source env/bin/activate

  pip install -r requirements.txt

Configuring the Demo
--------------------

Access to a D-Wave system must be configured, as described in the `dwave-cloud-client`_ documentation. A default solver
is required.

In `demo.py`, you need to fill in your `token` and `solver_name`

Running the Demo
----------------

A minimal working example using the main interface function can be seen by running:

.. code-block:: bash

  python demo.py
