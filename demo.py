# # HACK TO FIX NUMPY IMPORT ERROR
# # https://stackoverflow.com/questions/48168482/keyerror-path-on-numpy-import
# import os
# os.environ.setdefault('PATH', '')
# #################################

import dwave_micro_client_dimod as system

from dwave_circuit_fault_diagnosis_demo import circuits

if __name__ == '__main__':
    bqm = circuits.three_bit_multiplier()

    # TODO: get input from user
    # fix variables
    # A == 7
    bqm.fix_variable('a0', 1)
    bqm.fix_variable('a1', 1)
    bqm.fix_variable('a2', 1)
    # B == 7
    bqm.fix_variable('b0', 1)
    bqm.fix_variable('b1', 1)
    bqm.fix_variable('b2', 1)
    # P == 49
    bqm.fix_variable('p0', 1)
    bqm.fix_variable('p1', -1)
    bqm.fix_variable('p2', -1)
    bqm.fix_variable('p3', -1)
    bqm.fix_variable('p4', 1)
    bqm.fix_variable('p5', 1)
    # 'aux1' becomes disconnected, so needs to be fixed
    bqm.fix_variable('aux1', 1)  # don't care value

    # find embedding and put on system
    sampler = system.EmbeddingComposite(system.DWaveSampler(permissive_ssl=True))
    response = sampler.sample_ising(bqm.linear, bqm.quadratic, num_reads=1000)

    # TODO: verify gates
    # output results
    print(next(response.data()))
