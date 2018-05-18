.. image:: https://circleci.com/gh/dwavesystems/structural-imbalance-demo.svg?style=svg
    :target: https://circleci.com/gh/dwavesystems/structural-imbalance-demo

Demo for the Structural Imbalance Project
=========================================

Data is from the Stanford Militants Mapping Project

Mapping Militant Organizations, Stanford University, last modified February 28, 2016,
http://web.stanford.edu/group/mappingmilitants/cgi-bin/.

Setting Up the Demo
-------------------

Copy (clone) this structural-imbalance-demo repository to your local machine.

To set up the required dependencies, in the root directory of a copy (clone) of this repository, run the following:

.. code-block:: bash

  pip install .

Configuring the Demo
--------------------

To run the demo on the QPU, extra dependencies must be installed by running the following:

.. code-block:: bash

  pip install .[qpu] --extra-index-url https://pypi.dwavesys.com/simple

Access to a D-Wave system must be configured, as described in the `dwave-cloud-client
<http://dwave-cloud-client.readthedocs.io/en/latest/reference/intro.html#configuration>`_ documentation. A default
solver is required.

Running the Demo
----------------

To run the demo:

.. code-block:: bash

    python demo.py

License
-------

See LICENSE file.
