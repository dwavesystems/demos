from __future__ import division

from collections import OrderedDict

from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite

from factoring.circuits import three_bit_multiplier
from factoring.gates import GATES


def validate_input(ui, range_):
    start = range_[0]
    stop = range_[-1]

    if not isinstance(ui, int):
        raise ValueError("Input type must be int")

    if ui not in range_:
        raise ValueError("Input must be between {} and {}".format(start, stop))


NUM_READS = 1000


def get_factor_bqm(P):
    validate_input(P, range(2 ** 6))

    # get circuit
    bqm, labels = three_bit_multiplier(False)

    # fix product qubits
    fixed_variables = {}
    fixed_variables.update(zip(('p5', 'p4', 'p3', 'p2', 'p1', 'p0'), "{:06b}".format(P)))
    fixed_variables = {var: 1 if x == '1' else -1 for (var, x) in fixed_variables.items()}
    for var, value in fixed_variables.items():
        bqm.fix_variable(var, value)

    return bqm


def submit_factor_bqm(bqm):
    # find embedding and put on system
    sampler = EmbeddingComposite(DWaveSampler())

    kwargs = {}
    if 'num_reads' in sampler.parameters:
        kwargs['num_reads'] = NUM_READS
    if 'num_spin_reversal_transforms' in sampler.parameters:
        kwargs['num_spin_reversal_transforms'] = 1
    if 'answer_mode' in sampler.parameters:
        kwargs['answer_mode'] = 'histogram'

    response = sampler.sample(bqm, **kwargs)

    return response


def postprocess_factor_response(response, P):
    output = {"results": [],
                #    {
                #        "a": Number,
                #        "b": Number,
                #        "valid": Boolean,
                #        "numOfOccurrences": Number,
                #        "percentageOfOccurrences": Number
                #    }
                "numberOfReads": NUM_READS}

    # we know that three_bit_multiplier has created variables
    a_vars = ['a0', 'a1', 'a2']
    b_vars = ['b0', 'b1', 'b2']

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
            results_dict[(a, b, P)]["percentageOfOccurrences"] = 100 * results_dict[(a, b, P)]["numOfOccurrences"] / total
        else:
            results_dict[(a, b, P)] = {"a": a,
                                       "b": b,
                                       "valid": a * b == P,
                                       "numOfOccurrences": num_occurrences,
                                       "percentageOfOccurrences": 100 * num_occurrences / total}

    output['results'] = list(results_dict.values())

    return output
