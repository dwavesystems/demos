from __future__ import division

import sys
import re
from collections import OrderedDict

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
               #        "percentageOfOccurrences": Number
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
    a_vars = ['a0', 'a1', 'a2']
    b_vars = ['b0', 'b1', 'b2']

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
        from dwave.system.samplers import DWaveSampler
        from dwave.system.composites import EmbeddingComposite
        # find embedding and put on system
        sampler = EmbeddingComposite(DWaveSampler())

        kwargs = {}
        if 'num_reads' in sampler.parameters:
            kwargs['num_reads'] = NUM_READS
        if 'num_spin_reversal_transforms' in sampler.parameters:
            kwargs['num_spin_reversal_transforms'] = 1
        if 'answer_mode' in sampler.parameters:
            kwargs['answer_mode'] = 'histogram'

        response = sampler.sample_ising(bqm.linear, bqm.quadratic, **kwargs)
    else:
        import dwave_qbsolv as qbsolv
        # if no qpu access, use qbsolv's tabu
        sampler = qbsolv.QBSolv()
        response = sampler.sample_ising(bqm.linear, bqm.quadratic)

    output['status'] = "completed"

    ####################################################################################################
    # output results
    ####################################################################################################

    # we know that three_bit_multiplier has created variables

    if 'num_occurrences' not in response.data_vectors:
        response.data_vectors['num_occurrences'] = [1] * len(response)

    results_dict = OrderedDict()

    total = sum(response.data_vectors['num_occurrences'])

    for sample, num_occurrences in response.data(['sample', 'num_occurrences']):
        a = b = 0

        for lbl in reversed(a_vars):
            a = (a << 1) | (1 if sample[lbl] > 0 else 0)
        for lbl in reversed(b_vars):
            b = (b << 1) | (1 if sample[lbl] > 0 else 0)

        if (a, b, P) in results_dict:
            results_dict[(a, b, P)]["numOfOccurrences"] += num_occurrences
            results_dict[(a, b, P)]["percentageOfOccurrences"] = results_dict[(a, b, P)]["numOfOccurrences"] / total
        else:
            results_dict[(a, b, P)] = {"a": a,
                                       "b": b,
                                       "valid": a * b == P,
                                       "numOfOccurrences": num_occurrences,
                                       "percentageOfOccurrences": num_occurrences / total}

    output['results'] = list(results_dict.values())

    if 'timing' in response.info:
        output['timing']['actual']['qpuProcessTime'] = response.info['timing']['run_time_chip']

    return output
