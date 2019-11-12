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
        pass


