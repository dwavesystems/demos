import itertools

import networkx as nx
import penaltymodel as pm

# (in1, in2, out): 0.
AND = {(-1, -1, -1): 0., (+1, +1, +1): 0., (-1, +1, -1): 0., (+1, -1, -1): 0.}

# (augend, addend, sum, carry_out): 0.
HALF_ADD = {(-1, -1, -1, -1): 0., (-1, +1, +1, -1): 0., (+1, -1, +1, -1): 0., (+1, +1, -1, +1): 0.}

# (augend, addend, carry_in, sum, carry_out): 0.
FULL_ADD = {(-1, -1, -1, -1, -1): 0., (-1, -1, +1, +1, -1): 0., (-1, +1, -1, +1, -1): 0., (-1, +1, +1, -1, +1): 0.,
            (+1, -1, -1, +1, -1): 0., (+1, -1, +1, -1, +1): 0., (+1, +1, -1, -1, +1): 0., (+1, +1, +1, +1, +1): 0.}


def fault_gate(gate, explicit_gap):
    nV = len(next(iter(gate)))  # Assume all the same length
    fc = {}
    for config in itertools.product((-1, 1), repeat=nV):
        if config in gate:
            fc[config] = 0
        else:
            fc[config] = explicit_gap
    return fc


FAULT_GAP = .5  # BRAD try at 1.0 and 1.5
#print('Fault gap:', FAULT_GAP)


def fault_model(gate):
    configurations = fault_gate(gate, FAULT_GAP)
    size = len(next(iter(configurations)))
    while True:
        G = nx.complete_graph(size)
        spec = pm.Specification(G, range(len(next(iter(configurations)))), configurations, pm.SPIN)
        try:
            pmodel = pm.get_penalty_model(spec)
            if pmodel:
                print("penalty model fits on K%i" % size)
            else:
                raise LookupError("failed to get penalty model from factory")
            break
        except pm.ImpossiblePenaltyModel:
            print("penalty model does not fit on K%i" % size)
            size += 1

    print('h:', pmodel.model.linear)
    print('J:', pmodel.model.quadratic)
    return pmodel
