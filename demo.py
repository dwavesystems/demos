# # HACK TO FIX NUMPY IMPORT ERROR
# # https://stackoverflow.com/questions/48168482/keyerror-path-on-numpy-import
# import os
# os.environ.setdefault('PATH', '')
# #################################

import dwave_micro_client_dimod as system

from dwave_circuit_fault_diagnosis_demo import *  # TODO

if __name__ == '__main__':
    bqm, labels = three_bit_multiplier()

    # get input from user
    fixed_variables = {}

    got = False
    while not got:
        A = int(input("Input multiplier A (<=7):"))
        try:
            fixed_variables['a2'], fixed_variables['a1'], fixed_variables['a0'] = "{:03b}".format(A)
            got = True
        except ValueError:
            pass

    got = False
    while not got:
        B = int(input("Input multiplicand B (<=7):"))
        try:
            fixed_variables['b2'], fixed_variables['b1'], fixed_variables['b0'] = "{:03b}".format(B)
            got = True
        except ValueError:
            pass

    got = False
    while not got:
        P = int(input("Input product P (<=63):"))
        try:
            fixed_variables['p5'], fixed_variables['p4'], fixed_variables['p3'], fixed_variables['p2'], fixed_variables['p1'], fixed_variables['p0'] = "{:06b}".format(P)
            got = True
        except ValueError:
            pass

    fixed_variables = {var: 1 if x == '1' else -1 for (var, x) in fixed_variables.items()}

    # fix variables
    for var, value in fixed_variables.items():
        bqm.fix_variable(var, value)
    # 'aux1' becomes disconnected, so needs to be fixed
    bqm.fix_variable('aux1', 1)  # don't care value

    # find embedding and put on system
    sampler = system.EmbeddingComposite(system.DWaveSampler(permissive_ssl=True))
    response = sampler.sample_ising(bqm.linear, bqm.quadratic, num_reads=1000)

    # output results
    best_sample = next(response.samples())
    best_sample.update(fixed_variables)

    for gate_type, gates in labels.items():
        _, configurations = GATES[gate_type]
        for gate_name, gate in gates.items():
            res = tuple(best_sample[var] for var in gate)
            print(res)
            if res in configurations:
                print('%s is good' % gate_name)
            else:
                print('%s is faulty' % gate_name)
