import unittest
import os
import nbformat
import sys

from nbconvert.preprocessors import ExecutePreprocessor
from dwave.system.samplers import DWaveSampler


try:
    DWaveSampler()
    _config_found = True
except ValueError:
    _config_found = False


def run_notebook(path):
    # Set kernel_name based on python version
    kernel_name = "python{0}".format(sys.version_info.major)

    with open(path) as notebook_file:
        print('Running notebook {}'.format(path))
        nb = nbformat.read(notebook_file, nbformat.current_nbformat)
        ep = ExecutePreprocessor(timeout=600, kernel_name=kernel_name, allow_errors=True)
        ep.preprocess(nb, {'metadata': {'path': os.path.dirname(path)}})

        return nb


def _modify_grid_search_cell(nb):
    grid_search_line = 'from helpers import grid_search'
    for cell in nb.cells:
        source = cell.source.split('\n')
        if source[0] == grid_search_line:
            new_source = []
            en_scales_var = 'energy_scales'
            offset_mag_var = 'offset_magnitudes'
            modified_en = False
            modified_offset = False
            for line in source:
                if len(line) >= len(en_scales_var) and line[:len(en_scales_var)] == en_scales_var:
                    new_source.append('{} = [1.]'.format(en_scales_var))
                    modified_en = True
                elif len(line) >= len(offset_mag_var) and line[:len(offset_mag_var)] == offset_mag_var:
                    new_source.append('{} = [.1]'.format(offset_mag_var))
                    modified_offset = True
                else:
                    new_source.append(line)

            cell.source = '\n'.join(new_source)
            assert modified_en and modified_offset, "Failed to modify grid_search cell. Can't continue test"

    return nb


def extract_errors(notebook):
    errors = []
    for i, cell in enumerate(notebook.cells):
        for output in cell.get('outputs', []):
            if output.output_type == "error":
                errors.append((i, output))

    return errors


class TestNotebook(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('Running modified notebook...')

        notebook_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'demo.ipynb')
        kernel_name = "python{0}".format(sys.version_info.major)

        with open(notebook_path) as notebook_file:
            cls.notebook = nbformat.read(notebook_file, nbformat.current_nbformat)
            cls.notebook = _modify_grid_search_cell(cls.notebook)
            ep = ExecutePreprocessor(timeout=600, kernel_name=kernel_name, allow_errors=True)
            ep.preprocess(cls.notebook, {'metadata': {'path': os.path.dirname(notebook_path)}})

    def test_no_errors(self):
        self.assertListEqual(extract_errors(self.notebook), [])


if __name__ == '__main__':
    unittest.main()
