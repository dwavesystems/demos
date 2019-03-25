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

# we wish to divide 9 satellites into 3 constellations of 3 satellites each.
num_satellites = 9
num_constellations = 3

constellation_size = num_satellites // num_constellations

# don't consider constellations with average score less than score_threshold
score_threshold = .4

# for this example we will randomly assign a coverage score to each satellite
coverage = {v: random.uniform(.25, 1) for v in range(num_satellites)}

bqm = dimod.BinaryQuadraticModel.empty(dimod.BINARY)

# first we want to favor combinations with a high score
for constellation in itertools.combinations(range(num_satellites), constellation_size):
    # the score is the average coverage for a constellation
    score = sum(coverage[v] for v in constellation) / len(constellation)

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
