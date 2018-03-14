import sys
import re

import pandas as pd

from dwave_circuit_fault_diagnosis_demo import three_bit_multiplier, GATES


def validate_input(ui, range_):
    start = range_[0]
    stop = range_[-1]

    if not isinstance(ui, int):
        raise ValueError("Input type must be int")

    if ui not in range_:
        raise ValueError("Input must be between {} and {}".format(start, stop))


NUM_READS = 1000


def factor(P, _qpu=True):
    output = {"status": "pending",  # "pending", "in progress", "completed", "failed", or "canceled"
               "results": [],
               #    {
               #        "a": Number,
               #        "b": Number,
               #        "valid": Boolean,
               #        "numOfOccurrences": Number,
               #        "percentageOfOccurances": Number
               #    }
               "errors": [],
               #    {
               #        "exception": String,
               #        "message": String
               #    },
               "timing": {
                   "estimate": {
                       "min": None,   # milliseconds
                       "max": None,   # milliseconds
                   },
                   "actual": {
                       "qpuProcessTime": None,  # milliseconds
                       "queueTime": None  # milliseconds
                   }
               },
               "numberOfReads": NUM_READS}

    try:
        validate_input(P, range(2 ** 6))
    except ValueError as e:
        error = {"exception": e.__class__(), "message": e.__str__()}
        output['errors'].append(error)
        output['status'] = "failed"
        return output

    ####################################################################################################
    # get circuit
    ####################################################################################################
    bqm, labels = three_bit_multiplier(False)

    ####################################################################################################
    # fix product qubits
    ####################################################################################################

    fixed_variables = {}
    fixed_variables.update(zip(('p5', 'p4', 'p3', 'p2', 'p1', 'p0'), "{:06b}".format(P)))
    fixed_variables = {var: 1 if x == '1' else -1 for (var, x) in fixed_variables.items()}

    # fix variables
    for var, value in fixed_variables.items():
        bqm.fix_variable(var, value)

    ####################################################################################################
    # run problem
    ####################################################################################################

    output['status'] = "in progress"

    if _qpu:
        import dwave_micro_client_dimod as system
        # find embedding and put on system
        sampler = system.EmbeddingComposite(system.DWaveSampler())
        response = sampler.sample_ising(bqm.linear, bqm.quadratic, num_reads=NUM_READS)
    else:
        import dwave_qbsolv as qbsolv
        # if no qpu access, use qbsolv's tabu
        sampler = qbsolv.QBSolv()
        response = sampler.sample_ising(bqm.linear, bqm.quadratic)

    output['status'] = "completed"

    ####################################################################################################
    # output results
    ####################################################################################################

    for sample in response.samples():
        for variable in list(sample.keys()):
            if not (re.match('[ab]\d', variable)):
                sample.pop(variable)

    for datum in response.data():
        A = B = 0
        for key, value in sorted(datum['sample'].items(), reverse=True):
            if 'a' in key:
                A = (A << 1) | (1 if value == 1 else 0)
            elif 'b' in key:
                B = (B << 1) | (1 if value == 1 else 0)
        result = {}
        result['a'] = A
        result['b'] = B
        #result['energy'] = datum['energy']
        result['valid'] = (A * B == P)
        #result['numOfOccurrences'] = datum['num_occurences']
        output['results'].append(result)

    results = pd.DataFrame(output['results'])
    results = results.groupby(results.columns.tolist()).size().to_frame('numOfOccurrences').reset_index()
    results['percentageOfOccurances'] = results.numOfOccurrences / results.numOfOccurrences.sum() * 100
    output['results'] = results.to_dict('records')

    return output
