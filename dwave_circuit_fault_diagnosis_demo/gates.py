import itertools

import networkx as nx
import penaltymodel as pm

GATES = {}

GATES['AND'] = (('in1', 'in2', 'out'),
                {(-1, -1, -1): 0.,
                 (-1, +1, -1): 0.,
                 (+1, -1, -1): 0.,
                 (+1, +1, +1): 0., })

GATES['OR'] = (('in1', 'in2', 'out'),
               {(-1, -1, -1): 0.,
                (-1, +1, +1): 0.,
                (+1, -1, +1): 0.,
                (+1, +1, +1): 0., })

GATES['XOR'] = (('in1', 'in2', 'out'),
                {(-1, -1, -1): 0.,
                 (-1, +1, +1): 0.,
                 (+1, -1, +1): 0.,
                 (+1, +1, -1): 0., })

GATES['HALF_ADD'] = (('augend', 'addend', 'sum', 'carry_out'),
                     {(-1, -1, -1, -1): 0.,
                      (-1, +1, +1, -1): 0.,
                      (+1, -1, +1, -1): 0.,
                      (+1, +1, -1, +1): 0.})

GATES['FULL_ADD'] = (('augend', 'addend', 'carry_in', 'sum', 'carry_out'),
                     {(-1, -1, -1, -1, -1): 0.,
                      (-1, -1, +1, +1, -1): 0.,
                      (-1, +1, -1, +1, -1): 0.,
                      (-1, +1, +1, -1, +1): 0.,
                      (+1, -1, -1, +1, -1): 0.,
                      (+1, -1, +1, -1, +1): 0.,
                      (+1, +1, -1, -1, +1): 0.,
                      (+1, +1, +1, +1, +1): 0.})


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


def fault_model(gate_type):
    labels, configurations = GATES[gate_type]
    configurations = fault_gate(configurations, FAULT_GAP)
    size = len(next(iter(configurations)))
    while True:
        G = nx.complete_graph(size)
        nx.relabel_nodes(G, dict(enumerate(labels)), copy=False)
        spec = pm.Specification(G, labels, configurations, pm.SPIN)
        try:
            pmodel = pm.get_penalty_model(spec)
            if pmodel:
                print("penalty model fits on K{}".format(size))
            else:
                raise LookupError("failed to get penalty model from factory")
            break
        except pm.ImpossiblePenaltyModel:
            print("penalty model does not fit on K{}".format(size))
            size += 1

    print('h: {}'.format(pmodel.model.linear))
    print('J: {}\n'.format(pmodel.model.quadratic))
    return pmodel
