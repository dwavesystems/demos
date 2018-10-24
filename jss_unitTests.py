import unittest

from dimod import ExactSolver
from jobShopScheduler import JobShopScheduler
from neal import SimulatedAnnealingSampler


def fill_with_zeros(expected_solution_dict, job_dict, max_time):
    """Fills the 'missing' expected_solution_dict keys with a value of 0.
    args:
        expected_solution_dict: a dictionary.  {taskName: taskValue, ..}
        job_dict: a dictionary. {jobName: [(machineVal, taskTimeSpan), ..], ..}
        max_time: integer. Max time for the schedule
    """
    for job, tasks in job_dict.items():
        for pos in range(len(tasks)):
            prefix = str(job) + "_" + str(pos)

            for t in range(max_time):
                key = prefix + "," + str(t)

                if key not in expected_solution_dict:
                    expected_solution_dict[key] = 0


class TestIndividualJSSConstraints(unittest.TestCase):
    def test_oneStartConstraint(self):
        jobs = {"car": [("key", 2), ("gas", 1)],
                "stove": [("gas", 4)]}
        jss = JobShopScheduler(jobs, 3)
        jss._add_one_start_constraint()

        # Tasks only start once
        one_start_solution = {"car_0,0": 1, "car_0,1": 0, "car_0,2": 0,
                              "car_1,0": 0, "car_1,1": 1, "car_1,2": 0,
                              "stove_0,0": 1, "stove_0,1": 0, "stove_0,2": 0}

        # Task car_1 starts twice; it starts on times 0 and 1
        multi_start_solution = {"car_0,0": 1, "car_0,1": 0, "car_0,2": 0,
                                "car_1,0": 0, "car_1,1": 1, "car_1,2": 0,
                                "stove_0,0": 1, "stove_0,1": 1, "stove_0,2": 0}

        self.assertTrue(jss.csp.check(one_start_solution))
        self.assertFalse(jss.csp.check(multi_start_solution))

    def test_precedenceConstraint(self):
        jobs = {0: [("m1", 2), ("m2", 1)]}
        max_time = 4
        jss = JobShopScheduler(jobs, max_time)
        jss._add_precedence_constraint()

        # Task 0_0 starts after task 0_1
        backward_solution = {"0_0,3": 1, "0_1,0": 1}
        fill_with_zeros(backward_solution, jobs, max_time)

        # Tasks start at the same time
        same_start_solution = {"0_0,1": 1, "0_1,1": 1}
        fill_with_zeros(same_start_solution, jobs, max_time)

        # Task 0_1 starts before 0_0 has completed
        overlap_solution = {"0_0,1": 1, "0_1,2": 1}
        fill_with_zeros(overlap_solution, jobs, max_time)

        # Tasks follows correct order and respects task duration
        ordered_solution = {"0_0,0": 1, "0_1,2": 1}
        fill_with_zeros(ordered_solution, jobs, max_time)

        self.assertFalse(jss.csp.check(backward_solution))
        self.assertFalse(jss.csp.check(same_start_solution))
        self.assertFalse(jss.csp.check(overlap_solution))
        self.assertTrue(jss.csp.check(ordered_solution))

    def test_shareMachineConstraint(self):
        jobs = {"movie": [("pay", 1), ("watch", 3)],
                "tv": [("watch", 1)],
                "netflix": [("watch", 3)]}
        max_time = 7
        jss = JobShopScheduler(jobs, max_time)
        jss._add_share_machine_constraint()

        # All jobs 'watch' at the same time
        same_start_solution = {"movie_0,0": 1, "movie_1,1": 1,
                               "tv_0,1": 1,
                               "netflix_0,1": 1}
        fill_with_zeros(same_start_solution, jobs, max_time)

        # 'movie' does not obey precedence, but respects machine sharing
        bad_order_share_solution = {"movie_0,4": 1, "movie_1,0": 1,
                                    "tv_0,3": 1,
                                    "netflix_0,4": 1}
        fill_with_zeros(bad_order_share_solution, jobs, max_time)

        self.assertFalse(jss.csp.check(same_start_solution))
        self.assertTrue(jss.csp.check(bad_order_share_solution))

    def test_absurdTimesAreRemoved(self):
        pass


class TestCombinedJSSConstraints(unittest.TestCase):
    # TODO: test job with no tasks
    # TODO: test no jobs
    # TODO: test non-integer durations
    # TODO: insufficient max_time
    def test_denseSchedule(self):
        jobs = {"a": [(1, 2), (2, 2), (3, 2)],
                "b": [(3, 3), (2, 1), (1, 1)],
                "c": [(2, 2), (1, 3), (2, 1)]}
        max_time = 6
        jss = JobShopScheduler(jobs, max_time)
        jss.get_bqm()   # Run job shop scheduling constraints

        # Solution that obeys all constraints
        good_solution = {"a_0,0": 1, "a_1,2": 1, "a_2,4": 1,
                         "b_0,0": 1, "b_1,4": 1, "b_2,5": 1,
                         "c_0,0": 1, "c_1,2": 1, "c_2,5": 1}
        fill_with_zeros(good_solution, jobs, max_time)

        # Tasks a_1 and b_1 overlap in time on machine 2
        overlap_solution = {"a_0,0": 1, "a_1,2": 1, "a_2,4": 1,
                            "b_0,0": 1, "b_1,3": 1, "b_2,5": 1,
                            "c_0,0": 1, "c_1,2": 1, "c_2,5": 1}
        fill_with_zeros(overlap_solution, jobs, max_time)

        self.assertTrue(jss.csp.check(good_solution))
        self.assertFalse(jss.csp.check(overlap_solution))

    def test_relaxedSchedule(self):
        jobs = {"breakfast": [("cook", 2), ("eat", 1)],
                "music": [("play", 2)]}
        max_time = 7
        jss = JobShopScheduler(jobs, max_time)
        jss.get_bqm()   # Run job shop scheduling constraints

        # Solution obeys all constraints
        good_solution = {"breakfast_0,0": 1, "breakfast_1,4": 1,
                         "music_0,3": 1}
        fill_with_zeros(good_solution, jobs, max_time)

        # 'breakfast' tasks are out of order
        bad_order_solution = {"breakfast_0,1": 1, "breakfast_1,0": 1,
                              "music_0,0": 1}
        fill_with_zeros(bad_order_solution, jobs, max_time)

        self.assertTrue(jss.csp.check(good_solution))
        self.assertFalse(jss.csp.check(bad_order_solution))


class TestJSSResponse(unittest.TestCase):
    def compare(self, response, expected):
        """Comparing response to expected results
        """
        # Comparing variables found in sample and expected
        expected_keys = set(expected.keys())
        sample_keys = set(response.keys())
        common_keys = expected_keys & sample_keys
        different_keys = expected_keys - sample_keys  # expected_keys is a superset

        # Check that common variables match
        for key in common_keys:
            self.assertEqual(response[key], expected[key])

        # Check that non-existent 'sample' variables are 0
        for key in different_keys:
            self.assertEqual(expected[key], 0)

    def test_tinySchedule(self):
        jobs = {"a": [(1, 1), (2, 1)],
                "b": [(2, 1)]}
        max_time = 2

        # Get exact sample from Job Shop Scheduler BQM
        jss = JobShopScheduler(jobs, max_time)
        bqm = jss.get_bqm()
        response = ExactSolver().sample(bqm)
        response_sample = next(response.samples())

        # Verify that response_sample obeys constraints
        self.assertTrue(jss.csp.check(response_sample))

        # Create expected solution
        expected = {"a_0,0": 1, "a_1,1": 1, "b_0,0": 1}
        fill_with_zeros(expected, jobs, max_time)

        # Compare variable values
        self.compare(response_sample, expected)

    def test_largerSchedule(self):
        jobs = {'small1': [(1, 1)],
                'small2': [(2, 2)],
                'longJob': [(0, 1), (1, 1), (2, 1)]}
        max_time = 4

        # Get exact sample from Job Shop Scheduler BQM
        jss = JobShopScheduler(jobs, max_time)
        bqm = jss.get_bqm()
        response = ExactSolver().sample(bqm)
        response_sample = next(response.samples())

        # Verify that response_sample obeys constraints
        self.assertTrue(jss.csp.check(response_sample))

        # Create expected solution
        expected = {"small1_0,0": 1,
                    "small2_0,0": 1,
                    "longJob_0,0": 1, "longJob_1,1": 1, "longJob_2,2": 1}
        fill_with_zeros(expected, jobs, max_time)

        # Compare variable values
        self.compare(response_sample, expected)


class TestDemo(unittest.TestCase):
    def demo(self):
        # Solve JSS
        # Assumes that there are no tasks with non-positive processing times.
        jobs = {"j0": [(1, 2), (2, 2), (3, 2)],
                "j1": [(3, 3), (2, 1), (1, 1)],
                "j2": [(2, 2), (1, 3), (2, 1)]}
        max_time = 6

        # Sample for a JSS solution
        scheduler = JobShopScheduler(jobs, max_time)
        bqm = scheduler.get_bqm()
        response = SimulatedAnnealingSampler().sample(bqm, num_reads=1000)
        response_sample = next(response.samples())

        # Expected
        expected = {"j0_0,0": 1, "j0_1,2": 1, "j0_2,4": 1,
                    "j1_0,0": 1, "j1_1,4": 1, "j1_2,5": 1,
                    "j2_0,0": 1, "j2_1,2": 1, "j2_2,5": 1}

        # Print response
        print("check: ", scheduler.csp.check(response_sample))
        print("response_sample: ", response_sample)

    def demo2(self):
        # Solve JSS
        # Assumes that there are no tasks with non-positive processing times.
        jobs = {"j0": [(0, 1), (3, 1)],
                "j1": [(1, 1)],
                "j2": [(2, 1)],
                "j3": [(3, 1)],
                "j4": [(4, 1)]}
        n_samples = 1
        max_time = 6

        # Sample for a JSS solution
        scheduler = JobShopScheduler(jobs, max_time)
        bqm = scheduler.get_bqm()
        response = SimulatedAnnealingSampler().sample(bqm, num_reads=200)
        response_sample = next(response.samples())

        # Print response
        print("check: ", scheduler.csp.check(response_sample))
        print("response_sample: ", response_sample)


if __name__ == "__main__":
    unittest.main()
