import unittest
from random import randint

from factoring.interfaces import get_factor_bqm, submit_factor_bqm, postprocess_factor_response


class TestInterfaces(unittest.TestCase):

    def test_factor_output(self):
        P = randint(0, 2**6-1)
        bqm = get_factor_bqm(P)
        response = submit_factor_bqm(bqm)
        output = postprocess_factor_response(response, P)

        self.assertSetEqual(set(output), {'results', 'numberOfReads'})
        for result in output['results']:
            self.assertSetEqual(set(result), {'a', 'b', 'valid', 'numOfOccurrences', 'percentageOfOccurrences'})
            self.assertIsInstance(result['a'], int)
            self.assertIsInstance(result['b'], int)
            self.assertIsInstance(result['valid'], bool)
            self.assertIsInstance(result['numOfOccurrences'], int)
            self.assertIsInstance(result['percentageOfOccurrences'], float)
        self.assertIsInstance(output['numberOfReads'], int)

    def test_factor_invalid(self):
        for P in [-1, 64, 'a']:
            self.assertRaises(ValueError, get_factor_bqm, P)

    @unittest.skip("not robust enough yet")
    def test_factor_validity(self):
        for P in {a*b for a in range(2**3) for b in range(2**3)}:
            bqm = get_factor_bqm(P)
            response = submit_factor_bqm(bqm)
            output = postprocess_factor_response(response, P)

            self.assertTrue(output['results'][0]['valid'])
