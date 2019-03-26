# Copyright 2019 D-Wave Systems Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# =============================================================================
"""This example is based on a project by Booz Allen Hamilton researchers
[#btkrd]. See also link_.

The problem is to choose k sub-constellations of m satellites such that the
sum of the average coverage within each constellation is maximized.

.. _link: https://www.dwavesys.com/sites/default/files/QuantumForSatellitesQubits-4.pdf

.. [#btkrd] G. Bass, C. Tomlin, V. Kumar, P. Rihaczek, J. Dulny III.
    Heterogeneous Quantum Computing for Satellite Constellation Optimization:
    Solving the Weighted K-Clique Problem. 2018 Quantum Sci. Technol. 3 024010.
    https://arxiv.org/abs/1709.05381

"""
import itertools
import random

import dimod
import neal
import networkx as nx

# we wish to divide 12 satellites into 4 constellations of 3 satellites each.
num_satellites = 12
num_constellations = 4

constellation_size = num_satellites // num_constellations


# each of the 12 satellites (labelled 0-11) has a coverage score. This could be
# calculated as the percentage of time that the Earth region is in range of the
# satellite
coverage = {0: 0.90,
            1: 0.36,
            2: 0.79,
            3: 0.78,
            4: 0.46,
            5: 0.27,
            6: 0.86,
            7: 0.52,
            8: 0.78,
            9: 0.99,
            10: 0.25,
            11: 0.91}

# don't consider constellations with average score less than score_threshold
score_threshold = .4

bqm = dimod.BinaryQuadraticModel.empty(dimod.BINARY)

# first we want to favor combinations with a high score
for constellation in itertools.combinations(range(num_satellites), constellation_size):
    # the score is the average coverage for a constellation
    score = sum(coverage[v] for v in constellation) / constellation_size

    # to make it smaller, throw out the combinations with a score below
    # a set threshold
    if score < score_threshold:
        continue

    # we subtract the score because we want to minimize the energy
    bqm.add_variable(frozenset(constellation), -score)

# next we want to penalize pairs that share a satellite. We choose 2 because
# because we don't want it to be advantageous to pick both in the case that
# they both have 100% coverage
for c0, c1 in itertools.combinations(bqm.variables, 2):
    if c0.isdisjoint(c1):
        continue
    bqm.add_interaction(c0, c1, 2)

# finally we wish to choose num_constellations variables. We pick strength of 1
# because we don't want it to be advantageous to violate the constraint by
# picking more variables
bqm.update(dimod.generators.combinations(bqm, num_constellations, strength=1))

# sample from the bqm using simulated annealing
sampleset = neal.Neal().sample(bqm, num_reads=100).aggregate()

constellations = [constellation
                  for constellation, chosen in sampleset.first.sample.items()
                  if chosen]

print(constellations)
