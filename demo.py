import sys
import re

import pandas as pd

from factoring import three_bit_multiplier, GATES

try:
    import dwave_micro_client_dimod as system
    _qpu = True
except ImportError:
    import dwave_qbsolv as qbsolv
    _qpu = False

_PY2 = sys.version_info.major == 2
if _PY2:
    input = raw_input


def sanitised_input(description, variable, range_):
    start = range_[0]
    stop = range_[-1]

    while True:
        ui = input("Input {:15}({:2} <= {:1} <= {:2}): ".format(description, start, variable, stop))

        try:
            ui = int(ui)
        except ValueError:
            print("Input type must be int")
            continue

        if ui not in range_:
            print("Input must be between {} and {}".format(start, stop))
            continue

        return ui


NUM_READS = 1000

if __name__ == '__main__':
    ####################################################################################################
    # get circuit
    ####################################################################################################
    bqm, labels = three_bit_multiplier(False)

    ####################################################################################################
    # get input from user
    ####################################################################################################

    fixed_variables = {}

    print("Enter the test conditions")

    P = sanitised_input("product", "P", range(2**6))
    fixed_variables.update(zip(('p5', 'p4', 'p3', 'p2', 'p1', 'p0'), "{:06b}".format(P)))

    fixed_variables = {var: 1 if x == '1' else -1 for (var, x) in fixed_variables.items()}

    # fix variables
    for var, value in fixed_variables.items():
        bqm.fix_variable(var, value)

    if _qpu:
        # find embedding and put on system
        print("Running using QPU\n")
        sampler = system.EmbeddingComposite(system.DWaveSampler())
        response = sampler.sample_ising(bqm.linear, bqm.quadratic, num_reads=NUM_READS)
    else:
        # if no qpu access, use qbsolv's tabu
        print("Running using qbsolv's classical tabu search\n")
        sampler = qbsolv.QBSolv()
        response = sampler.sample_ising(bqm.linear, bqm.quadratic)

    ####################################################################################################
    # output results
    ####################################################################################################

    for sample in response.samples():
        for variable in list(sample.keys()):
            if not (re.match('[ab]\d', variable)):
                sample.pop(variable)

    results = []
    for datum in response.data():
        A = B = 0
        for key, value in sorted(datum['sample'].items(), reverse=True):
            if 'a' in key:
                A = (A << 1) | (1 if value == 1 else 0)
            elif 'b' in key:
                B = (B << 1) | (1 if value == 1 else 0)
        result = {}
        result['A'] = A
        result['B'] = B
        result['A*B'] = A * B
        result['P'] = P
        result['energy'] = datum['energy']
        result['valid'] = (A * B == P)
        results.append(result)

    results = pd.DataFrame(results)
    results = results.groupby(results.columns.tolist()).size().reset_index().sort_values('energy')
    columns = results.columns.tolist()
    columns[-1] = 'count'
    results.columns = columns
    results = results.sort_values('energy').set_index('count')

    pd.set_option('display.width', 120)
    print(results)
