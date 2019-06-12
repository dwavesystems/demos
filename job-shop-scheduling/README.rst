Job Shop Scheduling Demo
========================
A demo on how to optimally schedule jobs using a quantum computer.

Given a set of jobs and a finite number of machines, how should you schedule
your jobs on those machines such that all your jobs are completed at the
earliest possible time? This question is the Job Shop Scheduling Problem!

Each of our jobs can be broken down into smaller machine-specific tasks. For
example, the job of making pancakes can be broken down into several
machine-specific tasks: mixing ingredients in a *mixer* and cooking the batter
on the *stove*. There is an order to these tasks (ex. you can't bake the batter
before you mix the ingredients) and there is a time associated with each task
(ex. 5 minutes on the mixer, 2 minutes to cook on the stove). Now supposing
that you have multiple jobs with only a set number of machines, how do we
schedule our tasks onto those machines so that our jobs complete as early
as possible?

Here is a breakfast example with making pancakes and frying some eggs:
::

  {"pancakes": [("mixer", 5), ("stove", 2)],
   "eggs": [("stove", 3)]}

Bad schedule: make pancakes and then make eggs. Jobs will complete after 10
minutes (5 + 2 + 3 = 10).

Good schedule: while mixing pancake ingredients, make eggs. Jobs will complete
after 7 minutes (5 + 2 = 7; making eggs happens during the 5 minutes the
pancakes are being mixed).


Usage
-----
To run the demo:
::
  python demo.py

Code Overview
-------------
Most of the Job Shop Scheduling magic happens in `job_shop_scheduler.py`, so
the following overview is on that code.

Constraints:

* Each task starts only once
* Each task within the job must follow a particular order
* At most, one task can run on a machine at a given time
* Remove impossible task times

Code Specifics
--------------
As mentioned before, core code for Job Shop Scheduling lives in
`job_shop_scheduler.py`, so the following sections will be describing that code.

Inputs
~~~~~~
'jobs' dict describes the jobs we're interested in scheduling. Namely, the dict
key is the name of the job and the dict value is the ordered list of tasks that
the job must do.

It follows the format:
::

  {"job_a": [(machine_name, time_duration_on_machine), ..],
   "job_b": [(some_machine, time_duration_on_machine), ..],
   ..
   "job_n": [(machine_name, time_duration_on_machine), ..]}

For example,
::

  {"pancakes": [("mixer", 5), ("stove", 2)],
   "eggs": [("stove", 3)]}


References
----------
D. Venturelli, D. Marchand, and G. Rojo,
"Quantum Annealing Implementation of Job-Shop Scheduling",
`arXiv:1506.08479v2 <https://arxiv.org/abs/1506.08479v2>`_
