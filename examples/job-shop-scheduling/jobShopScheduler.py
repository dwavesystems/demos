# Copyright 2019 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

from bisect import bisect_right

import dwavebinarycsp


def get_jss_bqm(job_dict, max_time=None):
    """Returns a BQM to the Job Shop Scheduling problem.

    Args:
        job_dict: A dict. Contains the jobs we're interested in scheduling. (See Example below.)
        max_time: An integer. The upper bound on the amount of time the schedule can take.

    Returns:
        A dimod.BinaryQuadraticModel. Note: The nodes in the BQM are labelled in the format,
          <job_name>_<task_number>,<time>. (See Example below)

    Example:
        'jobs' dict describes the jobs we're interested in scheduling. Namely, the dict key is the
         name of the job and the dict value is the ordered list of tasks that the job must do.

        It follows the format:
          {"job_name": [(machine_name, time_duration_on_machine), ..],
           "another_job_name": [(some_machine, time_duration_on_machine), ..]}

        >>> # Create BQM
        >>> jobs = {"a": [("mixer", 2), ("oven", 1)],
                   "b": [("mixer", 1)],
                   "c": [("oven", 2)]}
        >>> max_time = 4	  # Put an upperbound on how long the schedule can be
        >>> bqm = get_jss_bqm(jobs, max_time)

        >>> # May need to tweak the chain strength and the number of reads
        >>> sampler = EmbeddingComposite(DWaveSampler(solver={'qpu':True}))
        >>> sampleset = sampler.sample(bqm, chain_strength=2, num_reads=1000)

        >>> # Results
        >>> # Note: Each node follows the format <job_name>_<task_number>,<time>.
        >>> print(sampleset)
        c_0,0  b_0,1  c_0,1  b_0,3  c_0,2  b_0,0  b_0,2  a_1,2  a_1,3  a_1,1  a_0,0  a_1,0  a_0,1  a_0,2
            1      0      0      0      0      0      1      1      0      0      1      0      0      0

        Interpreting Results:
          Consider the node, "b_0,2" with a value of 1.
          - "b_0,2" is interpreted as job b, task 0, at time 2
          - Job b's 0th task is ("mixer", 1)
          - Hence, at time 2, Job b's 0th task is turned on

          Consider the node, "a_1,0" with a value of 0.
          - "a_1,0" is interpreted as job a, task 1, at time 0
          - Job a's 1st task is ("oven", 1)
          - Hence, at time 0, Job a's 1st task is not run
    """
    scheduler = JobShopScheduler(job_dict, max_time)
    return scheduler.get_bqm()


def sum_to_one(*args):
    return sum(args) == 1


def get_label(task, time):
    """Creates a standardized name for variables in the constraint satisfaction problem,
    JobShopScheduler.csp.
    """
    return "{task.job}_{task.position},{time}".format(**locals())


class Task:
    def __init__(self, job, position, machine, duration):
        self.job = job
        self.position = position
        self.machine = machine
        self.duration = duration

    def __repr__(self):
        return ("{{job: {job}, position: {position}, machine: {machine}, duration:"
                " {duration}}}").format(**vars(self))


class KeyList:
    """A wrapper to an array. Used for passing the key of a custom object to the bisect function.

    Note: bisect function does not let you choose an arbitrary key, hence this class was created.
    """

    def __init__(self, array, key_function):
        self.array = array  # An iterable
        self.key_function = key_function  # Function for grabbing the key of a given item

    def __len__(self):
        return len(self.array)

    def __getitem__(self, index):
        item = self.array[index]
        key = self.key_function(item)
        return key


class JobShopScheduler:
    def __init__(self, job_dict, max_time=None):
        self.tasks = []
        self.last_task_indices = []
        self.max_time = max_time
        self.csp = dwavebinarycsp.ConstraintSatisfactionProblem(dwavebinarycsp.BINARY)

        # Populates self.tasks and self.max_time
        self._process_data(job_dict)

    def _process_data(self, jobs):
        """Process user input into a format that is more convenient for JobShopScheduler functions.
        """
        # Create and concatenate Task objects
        tasks = []
        last_task_indices = [-1]    # -1 for zero-indexing
        total_time = 0  # total time of all jobs

        for job_name, job_tasks in jobs.items():
            last_task_indices.append(last_task_indices[-1] + len(job_tasks))

            for i, (machine, time_span) in enumerate(job_tasks):
                tasks.append(Task(job_name, i, machine, time_span))
                total_time += time_span

        # Update values
        self.tasks = tasks
        self.last_task_indices = last_task_indices[1:]

        if self.max_time is None:
            self.max_time = total_time

    def _add_one_start_constraint(self):
        """self.csp gets the constraint: A task can start once and only once
        """
        for task in self.tasks:
            task_times = {get_label(task, t) for t in range(self.max_time)}
            self.csp.add_constraint(sum_to_one, task_times)

    def _add_precedence_constraint(self):
        """self.csp gets the constraint: Task must follow a particular order.
         Note: assumes self.tasks are sorted by jobs and then by position
        """
        valid_edges = {(0, 0), (1, 0), (0, 1)}
        for i, current_task in enumerate(self.tasks[:-1]):
            next_task = self.tasks[i + 1]

            if current_task.job != next_task.job:
                continue

            # Forming constraints with the relevant times of the next task
            for t in range(self.max_time):
                current_label = get_label(current_task, t)

                for tt in range(min(t + current_task.duration, self.max_time)):
                    next_label = get_label(next_task, tt)
                    self.csp.add_constraint(valid_edges, {current_label, next_label})

    def _add_share_machine_constraint(self):
        """self.csp gets the constraint: At most one task per machine per time
        """
        sorted_tasks = sorted(self.tasks, key=lambda x: x.machine)
        wrapped_tasks = KeyList(sorted_tasks, lambda x: x.machine) # Key wrapper for bisect function

        head = 0
        valid_values = {(0, 0), (1, 0), (0, 1)}
        while head < len(sorted_tasks):

            # Find tasks that share a machine
            tail = bisect_right(wrapped_tasks, sorted_tasks[head].machine)
            same_machine_tasks = sorted_tasks[head:tail]

            # Update
            head = tail

            # No need to build coupling for a single task
            if len(same_machine_tasks) < 2:
                continue

            # Apply constraint between all tasks for each unit of time
            for task in same_machine_tasks:
                for other_task in same_machine_tasks:
                    if task.job == other_task.job and task.position == other_task.position:
                        continue

                    for t in range(self.max_time):
                        current_label = get_label(task, t)

                        for tt in range(t, min(t + task.duration, self.max_time)):
                            self.csp.add_constraint(valid_values, {current_label,
                                                                   get_label(other_task, tt)})

    def _remove_absurd_times(self):
        """Sets impossible task times in self.csp to 0.
        """
        # TODO: deal with overlaps in time
        for task in self.tasks:
            # Times that are too early for task
            for t in range(task.position):
                label = get_label(task, t)
                self.csp.fix_variable(label, 0)

            # Times that are too late for task to complete
            for t in range(task.duration - 1):  # -1 to ignore duration==1
                label = get_label(task, (self.max_time - 1) - t)  # -1 for zero-indexed time
                self.csp.fix_variable(label, 0)

    def get_bqm(self):
        """Returns a BQM to the Job Shop Scheduling problem.

        Example on usage:
            # 'jobs' dict describes the jobs we're interested in scheduling. Namely,
            # the dict key is the name of the job and the dict value is the ordered
            # list of tasks that the job must do.
            #
            # {"job_name": [(machine_name, time_duration_on_machine), ..],
            #  "another_job_name": [(some_machine, time_duration_on_machine), ..]}

            jobs = {"job_a": [("mach_1", 2), ("mach_2", 2), ("mach_3", 2)],
                    "job_b": [("mach_3", 3), ("mach_2", 1), ("mach_1", 1)],
                    "job_c": [("mach_2", 2), ("mach_1", 3), ("mach_2", 1)]}
            max_time = 6	# Put an upperbound on how long the schedule can be

            jss = JobShopScheduler(jobs, max_time)
            jss.get_bqm()   # Run job shop scheduling constraints
        """
        # Apply constraints to self.csp
        self._add_one_start_constraint()
        self._add_precedence_constraint()
        self._add_share_machine_constraint()
        self._remove_absurd_times()

        # Get BQM
        bqm = dwavebinarycsp.stitch(self.csp)

        # Edit BQM
        base = len(self.last_task_indices) + 1     # Base for exponent
        for i in self.last_task_indices:
            task = self.tasks[i]

            for t in range(self.max_time):
                end_time = t + task.duration

                # Check task's end time; do not add in absurd times
                if end_time > self.max_time:
                    continue

                # Add bias to variable
                bias = 2 * base**(end_time - self.max_time)
                label = get_label(task, t)
                bqm.add_variable(label, bias)

        return bqm

