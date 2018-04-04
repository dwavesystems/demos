Demo for the Structural Imbalance Project
=========================================

References
----------

Data is from the Stanford Militants Mapping Project

Mapping Militant Organizations, Stanford University, last modified February 28, 2016, http://web.stanford.edu/group/mappingmilitants/cgi-bin/.

Running the Demo
----------------

You can run the demo on classical hardware (a CPU) or on a D-Wave QPU, with the selection made by the pip requirements
file used.

.. code-block:: bash

  pip install -r requirements_cpu.txt                                                     # to run on CPU
  pip install -r requirements_qpu.txt --extra-index-url https://pypi.dwavesys.com/simple  # to run on QPU


To run the demo:

.. code-block:: bash

    python demo.py


License
-------

See LICENSE file.
