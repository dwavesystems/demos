import unittest
import os
import sys

# /tests/integration/test_demo.py
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestDemo(unittest.TestCase):
    def test_smoke(self):
        """run demo.py and check that nothing crashes"""

        demo_file = os.path.join(project_dir, 'demo.py')

        # assume qboost is on the path
        exit_status = os.system('python {} --mnist --wisc'.format(demo_file))

        assert isinstance(exit_status, int)
        self.assertFalse(exit_status, "running demo.py returned an exit status != 0")
