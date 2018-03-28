import unittest
from random import randint

from factoring.interfaces import factor


class TestInterfaces(unittest.TestCase):

    def test_factor_output(self):
        P = randint(0, 2**6-1)
        output = factor(P)

        self.assertSetEqual(set(output), {'status', 'results', 'errors', 'timing', 'numberOfReads'})
        self.assertIsInstance(output['status'], str)
        for result in output['results']:
            self.assertSetEqual(set(result), {'a', 'b', 'valid', 'numOfOccurrences', 'percentageOfOccurrences'})
            self.assertIsInstance(result['a'], int)
            self.assertIsInstance(result['b'], int)
            self.assertIsInstance(result['valid'], bool)
            self.assertIsInstance(result['numOfOccurrences'], int)
            self.assertIsInstance(result['percentageOfOccurrences'], float)
        for error in output['errors']:
            self.assertSetEqual(set(error), {'exception', 'message'})
            self.assertIsInstance(error['exception'], str)
            self.assertIsInstance(error['message'], str)
        self.assertSetEqual(set(output['timing']), {'estimate', 'actual'})
        self.assertSetEqual(set(output['timing']['estimate']), {'min', 'max'})
        # self.assertIsInstance(output['timing']['estimate']['min'], int)
        # self.assertIsInstance(output['timing']['estimate']['max'], int)
        self.assertSetEqual(set(output['timing']['actual']), {'qpuProcessTime', 'queueTime'})
        self.assertIsInstance(output['timing']['actual']['qpuProcessTime'], int)
        # self.assertIsInstance(output['timing']['actual']['queueTime'], int)
        self.assertIsInstance(output['numberOfReads'], int)

    def test_factor_invalid(self):
        for P in [-1, 64, 'a']:
            output = factor(P)
            self.assertEqual(output['status'], 'failed')
            self.assertEqual(len(output['errors']), 1)

    @unittest.skip("not robust enough yet")
    def test_factor_validity(self):
        for P in {a*b for a in range(2**3) for b in range(2**3)}:
            output = factor(P)
            self.assertEqual(output['status'], 'completed')
            self.assertTrue(output['results'][0]['valid'])
