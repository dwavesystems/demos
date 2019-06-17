Job Shop Scheduling Demo
========================
A demo on how to optimally schedule jobs using a quantum computer.

Given a set of jobs and a finite number of machines, how should we schedule
our jobs on those machines such that all our jobs are completed at the
earliest possible time? This question is the job shop scheduling problem!

Now let's go over some details about job shop scheduling. Each of our jobs
can be broken down into smaller machine-specific tasks. For
example, the job of making pancakes can be broken down into several
machine-specific tasks: mixing ingredients in a *mixer* and cooking the batter
on the *stove*. There is an order to these tasks (e.g. we can't bake the batter
before we mix the ingredients) and there is a time associated with each task
(e.g. 5 minutes on the mixer, 2 minutes to cook on the stove). Given that
that we have multiple jobs with only a set number of machines, how do we
schedule our tasks onto those machines so that our jobs complete as early
as possible?

Here is a breakfast example with making pancakes and frying some eggs:
::

  # Note that jobs and tasks in this demo are described in the following format:
  # {"job_name": [("machine_name", duration_on_machine), ..], ..}

  {"pancakes": [("mixer", 5), ("stove", 2)],
   "eggs": [("stove", 3)]}

Bad schedule: make pancakes and then make eggs. The jobs complete after 10
minutes (5 + 2 + 3 = 10).

Good schedule: while mixing pancake ingredients, make eggs. The jobs complete
after 7 minutes (5 + 2 = 7; making eggs happens during the 5 minutes the
pancakes are being mixed).

Usage
-----
To run the demo:
::
  python demo.py

Code Overview
-------------
Most of the Job Shop Scheduling magic happens in ``job_shop_scheduler.py``, so
the following overview is on that code. (Note: the ``job_shop_scheduler``
module gets imported into ``demo.py``.)

In the ``job_shop_scheduler.py``, we describe the Job Shop Scheduling Problem
with the following constraints:

* Each task starts only once
* Each task within the job must follow a particular order
* At most, one task can run on a machine at a given time
* Task times must be possible

Using tools from the D-Wave Ocean, these constraints get converted into a
`BQM <https://docs.ocean.dwavesys.com/en/latest/glossary.html#glossary>`_,
a mathematical model that we can then submit to a solver.
Afterwards, the solver returns a solution that indicates the times in
which the tasks should be scheduled.

Code Specifics
--------------
As mentioned before, the core code for Job Shop Scheduling lives in
``job_shop_scheduler.py``, so the following sections describe that
code.

Input
~~~~~
The jobs dictionary describes the jobs we're interested in scheduling. Namely,
the dictionary key is the name of the job and the dictionary value is the
ordered list of tasks that the job must do.

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
