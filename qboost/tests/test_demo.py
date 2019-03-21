import unittest
import os
import sys

from dwave.system.samplers import DWaveSampler

try:
    DWaveSampler()
    _config_found = True
except ValueError:
    _config_found = False

# /tests/integration/test_demo.py
PY2 = sys.version_info.major == 2
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@unittest.skipUnless(_config_found, "no configuration found for accessing the D-Wave System")
class TestDemo(unittest.TestCase):
    def test_smoke(self):
        """run demo.py and check that nothing crashes"""

        demo_file = os.path.join(project_dir, 'demo.py')

        # assume qboost is on the path
        exit_status = os.system('python {} --mnist --wisc'.format(demo_file))

        assert isinstance(exit_status, int)
        self.assertFalse(exit_status, "running demo.py returned an exit status != 0")
