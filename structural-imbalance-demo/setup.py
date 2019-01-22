from __future__ import absolute_import

import sys
import os
from setuptools import setup

_PY2 = sys.version_info.major == 2

# Change directories so this works when called from other locations. Useful in build systems that build from source.
setup_folder_loc = os.path.dirname(os.path.abspath(__file__))
os.chdir(setup_folder_loc)

# Add __version__, __author__, __authoremail__, __description__ to this namespace
path_to_package_info = os.path.join('.', 'dwave_structural_imbalance_demo', 'package_info.py')
if _PY2:
    execfile(path_to_package_info)
else:
    exec(open(path_to_package_info).read())

# These should be minimal requirements for the package to work, and avoid pinning dependencies unless required. See
# https://packaging.python.org/discussions/install-requires-vs-requirements/
install_requires = ['networkx>=2.0,<3.0',
                    'dwave_networkx>=0.6.2,<0.7.0',
                    'matplotlib>=2.2.2,<3.0.0',
                    'scipy>=1.1.0,<2.0.0',
                    'dwave-system>=0.6.0,<0.7.0',
                    'dwave-neal>=0.4.0,<0.5.0']

# The packages in this repo that are to be installed. Either list these explictly, or use setuptools.find_packages. If
# the latter, take care to filter unwanted packages (e.g. tests)
packages = ['dwave_structural_imbalance_demo', 'dwave_structural_imbalance_demo.mmp_network']

setup(
    name='structural-imbalance-demo',
    version=__version__,
    author=__author__,
    author_email=__authoremail__,
    description=__description__,
    long_description=open('README.rst').read(),
    url='https://github.com/dwavesystems/structural-imbalance-demo',
    license='Apache 2.0',
    packages=packages,
    install_requires=install_requires,
    include_package_data=True
)
