import os
import subprocess
import unittest

example_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestSmoke(unittest.TestCase):
    # test that the example runs without failing
    def test_smoke(self):
        cmd = 'python ' + os.path.join(example_dir, 'satellite.py')

        value = subprocess.check_output(cmd, shell=True)

        for constellation in eval(value):
            self.assertIsInstance(constellation, frozenset)
