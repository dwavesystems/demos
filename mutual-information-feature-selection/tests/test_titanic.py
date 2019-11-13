import os
import subprocess
import unittest

import numpy as np

from titanic import (prob, shannon_entropy, conditional_shannon_entropy,
                     mutual_information, conditional_mutual_information)


class TestTitanicFunctions(unittest.TestCase):
    def test_prob(self):
        data = np.array([[True, 0, 4],
                         [True, 2, 3],
                         [True, 1, 2],
                         [False, 0, 1],
                         [False, 0, 1]])
        multidim_prob = prob(data)    # multidimensional probabilities

        # Expected values
        expected_bins = (2, 3, 4)    # number of unique values per data column

        # Check shape
        self.assertEqual(multidim_prob.shape, expected_bins)

        # Check values
        # Note: two items in data are identical and should fall in the same bin,
        #   while the other three items are unique. Hence, we should expect
        #   a probability of 0.4 and three of 0.2.
        # Note2: we're doing an indirect check on the values because I'm not
        #   sure if the histogram will always produce the same binning order per
        #   axis.
        flat_prob = multidim_prob.ravel()
        self.assertEqual(np.sum(flat_prob), 1)   # probabilities sum to 1
        self.assertEqual(np.sum(flat_prob==0.4), 1)
        self.assertEqual(np.sum(flat_prob==0.2), 3)

    def test_shannon_entropy(self):
        prob = np.array([[0.5, 0], [0.3, 0.2]])
        result = shannon_entropy(prob)

        # -0.5*np.log2(0.5) - 0.3*np.log2(0.3) -0.2*np.log2(0.2)
        expected = 1.4854752972273344
        self.assertAlmostEqual(result, expected)

    def test_conditional_shannon_entropy(self):
        p = np.array([[[0.2, 0.0],
                       [0.1, 0.1]],
                      [[0.0, 0.3],
                       [0.25, 0.05]]])

        p_x0 = sum(sum(p[0, :, :]))  # p(x=0)
        p_x1 = sum(sum(p[1, :, :]))  # p(x=1)

        expected = 0
        for y in range(2):
            p_x0_y = sum(p[0, y, :])
            p_x1_y = sum(p[1, y, :])
            expected += (p_x0_y * np.log2(p_x0/p_x0_y))
            expected += (p_x1_y * np.log2(p_x1/p_x1_y))

        for y in range(2):
            p_x0_y = sum(p[0, :, y])
            p_x1_y = sum(p[1, :, y])
            expected += (p_x0_y * np.log2(p_x0/p_x0_y))
            expected += (p_x1_y * np.log2(p_x1/p_x1_y))

        result = conditional_shannon_entropy(p, 1,2)



    def test_mutual_information(self):
        pass

    def test_conditional_mutual_information(self):
        pass


class TestTitanicDemo(unittest.TestCase):
    def test_run_demo(self):
        """Run smoke test on demo code"""
        # /path/to/demos/mutual-information-feature-selection/
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Raise error when return code is nonzero
        demo_file = os.path.join(project_dir, 'titanic.py')
        subprocess.check_output(["python", demo_file])
