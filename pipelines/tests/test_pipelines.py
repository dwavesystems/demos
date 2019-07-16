import unittest
import os
import sys

from dwave.system.samplers import DWaveSampler

# /tests/integration/test_demo.py
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestDemo(unittest.TestCase):
    def test_smoke(self):
        """run pipelines.py and check that nothing crashes"""

        demo_file = os.path.join(project_dir, 'pipelines.py')

        # assume pipelines is on the path
        exit_status = os.system('python {}'.format(demo_file))

        assert isinstance(exit_status, int)
        self.assertFalse(exit_status, "running pipelines.py returned an exit status != 0")
