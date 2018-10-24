from __future__ import print_function

from bisect import bisect_right

import dwavebinarycsp as dbc


def sum_to_one(*args):
    return sum(args) == 1


class Task():
    def __init__(self, job, position, machine, duration):
        self.job = job
        self.position = position
        self.machine = machine
        self.duration = duration

    def __str__(self):
        # TODO: could do better a differentiating strings and numbers
        job = "job: " + str(self.job)
        position = "position: " + str(self.position)
        machine = "machine: " + str(self.machine)
        duration = "duration: " + str(self.duration)
        task_str = ", ".join([job, position, machine, duration])

        return "{" + task_str + "}"


class KeyList():
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


# TODO: put asserts to validate jobs
class JobShopScheduler():
    def __init__(self, job_dict, max_time=None):
        self.tasks = []
        self.max_time = max_time
        self.csp = dbc.ConstraintSatisfactionProblem(dbc.BINARY)

        # Populates self.tasks and self.max_time
        self._process_data(job_dict)

    def _process_data(self, jobs):
        """Process user input into a format that is more convenient for JobShopScheduler functions.
        """
        # Create and concatenate Task objects
        tasks = []
        total_time = 0  # total time of all jobs
        for job_name, job_tasks in jobs.items():
            for i, (machine, time_span) in enumerate(job_tasks):
                tasks.append(Task(job_name, i, machine, time_span))
                total_time += time_span

        # Update values
        self.tasks = tasks
        #if self.max_time is None or self.max_time > total_time:  #TODO: check if I should overwrite user input
        if self.max_time is None:  #TODO: check if I should overwrite user input
            self.max_time = total_time

    def _get_label(self, task, time):
        """Creates a standardized name for variables in the constraint satisfaction problem, self.csp.
        """
        name = str(task.job) + "_" + str(task.position)
        return name + "," + str(time)

    def _add_one_start_constraint(self):
        """self.csp gets the constraint: A task can start once and only once
        """
        for task in self.tasks:
            task_times = {self._get_label(task, t) for t in range(self.max_time)}
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
                current_label = self._get_label(current_task, t)

                for tt in range(min(t + current_task.duration, self.max_time)):
                    next_label = self._get_label(next_task, tt)
                    self.csp.add_constraint(valid_edges, {current_label, next_label})

    def _add_share_machine_constraint(self):
        """self.csp gets the constraint: At most one task per machine per time
        """
        sorted_tasks = sorted(self.tasks, key=lambda x: x.machine)
        wrapped_tasks = KeyList(sorted_tasks, lambda x: x.machine)  # Key wrapper

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
                        current_label = self._get_label(task, t)

                        for tt in range(t, min(t + task.duration, self.max_time)):
                            self.csp.add_constraint(valid_values, {current_label, self._get_label(other_task, tt)})

    def _remove_absurd_times(self):
        """Sets impossible task times in self.csp to 0.
        """
        # TODO: deal with overlaps in time
        for task in self.tasks:
            # Times that are too early for task
            for t in range(task.position):
                label = self._get_label(task, t)
                self.csp.fix_variable(label, 0)

            # Times that are too late for task to complete
            for t in range(task.duration - 1):  # -1 to ignore duration==1
                label = self._get_label(task, (self.max_time - 1) - t)  # -1 for zero-indexed time
                self.csp.fix_variable(label, 0)

    def get_bqm(self):
        """Returns a BQM to the Job Shop Scheduling problem.
        """
        # Apply constraints to self.csp
        self._add_one_start_constraint()
        self._add_precedence_constraint()
        self._add_share_machine_constraint()
        self._remove_absurd_times()

        # Get BQM
        bqm = dbc.stitch(self.csp)

        # Edit BQM
        base = len(self.tasks) + 1     # Base for exponent
        for task in self.tasks:
            for t in range(self.max_time):
                end_time = t + task.duration

                # Check task's end time; do not add in absurd times
                if end_time > self.max_time:
                    continue

                # Add bias to variable
                bias = 2 * base**(end_time - self.max_time)
                print(bias, end_time, self.max_time)
                label = self._get_label(task, t)
                bqm.add_variable(label, bias)

        return bqm