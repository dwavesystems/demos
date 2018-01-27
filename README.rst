Demo for Circuit Fault Diagnosis
================================

How to run the demo
-------------------

```
>>> pip install -r requirements.txt
>>> python demo.py
```

Note that one of the requirements, penaltymodelmaxgap_, will not function without smt solvers installed.
The solvers are accessed through the pysmt_ package.
See the accompanying pysmt documentation for installing smt solvers.

Access to a D-Wave system needs to be set up with a dwrc_ file.

The demo will construct a Binary Quadratic Model for a three-bit multiplier and embed it on the system.
The user will be prompted for 3 integers:
 * multiplier     ( 0 <= A <=  7)
 * multiplicand   ( 0 <= B <=  7)
 * product        ( 0 <= P <= 63)

The system will find a minimum fault diagnosis and output for each gate whether it is valid or faulty.

Interesting cases to try
------------------------

There are four cases (two isomorphic sets due to the commutative property of multiplication) in which only one faulty
gate leads to five of the six bits in the product being incorrect:
 * `A = 6; B = 5; P = 32`
 * `A = 5; B = 6; P = 32`
 * `A = 7; B = 4; P = 34`
 * `A = 4; B = 7; P = 34`

There are four cases (where the product is one more than the above examples due to the least significant bit being
solely determined by an AND gate disconnected from the rest of the circuit) in which only two faulty gates lead to all
six bits in the product being incorrect:
 * `A = 6; B = 5; P = 33`
 * `A = 5; B = 6; P = 33`
 * `A = 7; B = 4; P = 35`
 * `A = 4; B = 7; P = 35`

The maximum number of faulty gates in a minimum fault diagnosis for this circuit is four.
Many of these cases only lead to four of the six bits in the product being incorrect.
One such case is: `A = 7; B = 6; P = 1`.

In general, the number of incorrect bits in the product is greater than or equal to the number of faulty gates.

License
-------

See LICENSE file.

.. _penaltymodelmaxgap: https://github.com/dwavesystems/penaltymodel_maxgap
.. _pysmt: https://github.com/pysmt/pysmt
.. _dwrc: http://dwave-micro-client.readthedocs.io/en/latest/#configuration
