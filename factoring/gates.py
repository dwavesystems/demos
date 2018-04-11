import itertools

import networkx as nx
import penaltymodel as pm

GATES = {}

GATES['AND'] = (('in1', 'in2', 'out'),
                {(0, 0, 0): 0.,
                 (0, 1, 0): 0.,
                 (1, 0, 0): 0.,
                 (1, 1, 1): 0., })

GATES['OR'] = (('in1', 'in2', 'out'),
               {(0, 0, 0): 0.,
                (0, 1, 1): 0.,
                (1, 0, 1): 0.,
                (1, 1, 1): 0., })

GATES['XOR'] = (('in1', 'in2', 'out'),
                {(0, 0, 0): 0.,
                 (0, 1, 1): 0.,
                 (1, 0, 1): 0.,
                 (1, 1, 0): 0., })

GATES['HALF_ADD'] = (('augend', 'addend', 'sum', 'carry_out'),
                     {(0, 0, 0, 0): 0.,
                      (0, 1, 1, 0): 0.,
                      (1, 0, 1, 0): 0.,
                      (1, 1, 0, 1): 0.})

GATES['FULL_ADD'] = (('augend', 'addend', 'carry_in', 'sum', 'carry_out'),
                     {(0, 0, 0, 0, 0): 0.,
                      (0, 0, 1, 1, 0): 0.,
                      (0, 1, 0, 1, 0): 0.,
                      (0, 1, 1, 0, 1): 0.,
                      (1, 0, 0, 1, 0): 0.,
                      (1, 0, 1, 0, 1): 0.,
                      (1, 1, 0, 0, 1): 0.,
                      (1, 1, 1, 1, 1): 0.})


def gate_model(gate_type):
    labels, configurations = GATES[gate_type]
    size = len(next(iter(configurations)))
    while True:
        G = nx.complete_graph(size)
        nx.relabel_nodes(G, dict(enumerate(labels)), copy=False)
        spec = pm.Specification(G, labels, configurations, 'BINARY')
        try:
            pmodel = pm.get_penalty_model(spec)
            if not pmodel:
                raise LookupError("failed to get penalty model from factory")
            break
        except pm.ImpossiblePenaltyModel:
            size += 1

    return pmodel
