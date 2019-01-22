.. image:: https://circleci.com/gh/dwavesystems/structural-imbalance-demo.svg?style=svg
    :target: https://circleci.com/gh/dwavesystems/structural-imbalance-demo

Demo of Structural Imbalance in Signed Social Networks
======================================================

*Social networks* map relationships between people or organizations onto graphs, with
the people/organizations as nodes and relationships as edges; for example,
Facebook friends form a social network with friends represented as
nodes with connecting edges. *Signed social networks* map both friendly and
hostile relationships by setting the values of the edges between nodes with either plus ("+")
or minus ("-") signs. Such networks are said to be *structurally balanced* when they
can be clearly divided into two, with friendly relations (represented by positive-valued
edges) in each faction, and hostile relations (negative-valued edges) between these factions.

The measure of *structural imbalance* or *frustration* for a signed social network
is the minimum number of edges that violate this rule.

.. figure:: _static/Social.png
  :name: social
  :alt: Three-person social network

Social theory suggests that
increased frustration predicts social instability. In the context of militant organizations,
this can result in increased violence.

This demo calculates and shows structural imbalance for social networks of militant
organization based on data from the Stanford Militants Mapping Project:

Mapping Militant Organizations, Stanford University, last modified February 28, 2016,
http://web.stanford.edu/group/mappingmilitants/cgi-bin/.

Setting Up the Demo
-------------------

Copy (clone) this structural-imbalance-demo repository to your local machine.

In the root directory of your copy of this repository, execute one of the following two commands:

Install as package:

.. code-block:: bash

   pip install .

or, install requirements:

.. code-block:: bash

   pip install -r requirements.txt

Note: access to a D-Wave system must be configured, as described in the
`dwave-cloud-client <http://dwave-cloud-client.readthedocs.io/en/latest/reference/intro.html#configuration>`_ documentation.
Only API endpoint and API token are required. The first available DW_2000Q solver will be used by default.

Running the Demo
----------------

To run the demo, execute one of the following two commands:

A. Local CPU Execution
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python demo.py cpu

B. D-Wave System Execution
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python demo.py qpu

The demo fetches data from the Stanford Militants Mapping Project, calculates the networks,
and saves PNG-formatted graphic files and CSV-formatted files in the root directory of your
copy of the demo repository and in a Results subdirectory.

Note that this CLI command runs the entire demo and can take a few minutes to complete. You can
easily modify the code to run just parts of the demo from within a Python interpreter.

License
-------

See LICENSE file.
