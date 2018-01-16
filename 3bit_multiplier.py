import itertools

import penaltymodel as pm
import networkx as nx
#import dwave_networkx as dnx


# (in1, in2, out): 0.
AND = {(-1, -1, -1): 0., (+1, +1, +1): 0., (-1, +1, -1): 0., (+1, -1, -1): 0.}

# (augend, addend, sum, carry_out): 0.
HALF_ADD = {(-1, -1, -1, -1): -1., (-1, +1, +1, -1): -1., (+1, -1, +1, -1): -1., (+1, +1, -1, +1): -1.}

# (augend, addend, carry_in, sum, carry_out): 0.
FULL_ADD = {(-1, -1, -1, -1, -1): -1., (-1, -1, +1, +1, -1): -1., (-1, +1, -1, +1, -1): -1., (-1, +1, +1, -1, +1): -1.,
            (+1, -1, -1, +1, -1): -1., (+1, -1, +1, -1, +1): -1., (+1, +1, -1, -1, +1): -1., (+1, +1, +1, +1, +1): -1.}


def fault_gate(gate, explicit_gap):
    nV = len(next(iter(gate)))  # Assume all the same length
    fc = {}
    for config in itertools.product((-1, 1), repeat=nV):
        if config in gate:
            fc[config] = 0
        else:
            fc[config] = explicit_gap
    return fc


FAULT_GAP = .5
print('Fault gap:', FAULT_GAP)


def fault_model(gate):
    configurations = fault_gate(gate, FAULT_GAP)
    size = len(next(iter(configurations)))
    while True:
        G = nx.complete_graph(size)
        spec = pm.Specification(G, range(len(next(iter(configurations)))), configurations, pm.SPIN)
        try:
            pmodel = pm.get_penalty_model(spec)
        except pm.ImpossiblePenaltyModel:
            print("penalty model does not fit on K%i" % size)
            size += 1
        else:
            print("penalty model fits on K%i" % size)
            break
    return pmodel


####################################################################################################
# Gates
####################################################################################################
print("AND gate fault model")

pmodel_and = fault_model(AND)

print('h:', pmodel_and.model.linear)
print('J:', pmodel_and.model.quadratic)

#

print("half adder fault model")

pmodel_half_add = fault_model(HALF_ADD)

print('h:', pmodel_half_add.model.linear)
print('J:', pmodel_half_add.model.quadratic)

#

print("full adder fault model")

pmodel_full_add = fault_model(FULL_ADD)

print('h:', pmodel_full_add.model.linear)
print('J:', pmodel_full_add.model.quadratic)

# wire the whole thing up

#                            a2 & b0  a1 & b0  a0 & b0
#                   a2 & b1  a1 & b1  a0 & b1
#          a2 & b2  a1 & b2  a0 & b2
# ────────────────────────────────────────────────────
#    p5       p4       p3       p2       p1       p0

#                      and20  and10  and00
#               and21  and11  and01
#        and22  and12  and02
# ────────────────────────────────────────
#   p5     p4     p3     p2     p1     p0

and00 = pmodel_and.relabel_variables({0: 'a0', 1: 'b0', 2: 'p0'}, copy=True)
and01 = pmodel_and.relabel_variables({0: 'a0', 1: 'b1', 2: 'and01'}, copy=True)
and02 = pmodel_and.relabel_variables({0: 'a0', 1: 'b2', 2: 'and02'}, copy=True)
and10 = pmodel_and.relabel_variables({0: 'a1', 1: 'b0', 2: 'and10'}, copy=True)
and11 = pmodel_and.relabel_variables({0: 'a1', 1: 'b1', 2: 'and11'}, copy=True)
and12 = pmodel_and.relabel_variables({0: 'a1', 1: 'b2', 2: 'and12'}, copy=True)
and20 = pmodel_and.relabel_variables({0: 'a2', 1: 'b0', 2: 'and20'}, copy=True)
and21 = pmodel_and.relabel_variables({0: 'a2', 1: 'b1', 2: 'and21'}, copy=True)
and22 = pmodel_and.relabel_variables({0: 'a2', 1: 'b2', 2: 'and22'}, copy=True)

#                                         and20         and10         and00
#                                           |             |             |
#                           and21         add11──and11  add01──and01    |
#                             |┌───────────┘|┌───────────┘|             |
#             and22         add12──and12  add02──and02    |             |
#               |┌───────────┘|┌───────────┘|             |             |
#             add13─────────add03           |             |             |
#  ┌───────────┘|             |             |             |             |
# p5            p4            p3            p2            p1            p0

add01 = pmodel_half_add.relabel_variables({0: 'and01', 1: 'and10', 2: 'p1', 3: 'carry01'}, copy=True)
add02 = pmodel_full_add.relabel_variables({0: 'and02', 1: 'sum11', 2: 'carry01', 3: 'p2', 4: 'carry02'}, copy=True)
add03 = pmodel_half_add.relabel_variables({0: 'carry02', 1: 'sum12', 2: 'p3', 3: 'carry03'}, copy=True)
add11 = pmodel_half_add.relabel_variables({0: 'and11', 1: 'and20', 2: 'sum11', 3: 'carry11'}, copy=True)
add12 = pmodel_full_add.relabel_variables({0: 'and12', 1: 'and21', 2: 'carry11', 3: 'sum12', 4: 'carry12'}, copy=True)
add13 = pmodel_full_add.relabel_variables({0: 'carry03', 1: 'and22', 2: 'carry12', 3: 'p4', 4: 'p5'}, copy=True)

# COMBINE INTO ONE PENALTY MODEL

# FIND EMBEDDING TO SYSTEM

# PUT ON SYSTEM
