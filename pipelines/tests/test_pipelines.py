import os
import subprocess
import unittest

# /tests/test_demo.py
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestDemo(unittest.TestCase):
    def test_smoke(self):
        """run pipelines.py and check that nothing crashes"""

        demo_file = os.path.join(project_dir, 'pipelines.py')
        subprocess.check_output(["python", demo_file])

