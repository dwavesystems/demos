from __future__ import division

import time
import logging

from collections import OrderedDict

from dwave.system.samplers import DWaveSampler
import minorminer
import dimod

from factoring.circuits import three_bit_multiplier
from factoring.gates import GATES

log = logging.getLogger(__name__)


def validate_input(ui, range_):
    start = range_[0]
    stop = range_[-1]

    if not isinstance(ui, int):
        raise ValueError("Input type must be int")

    if ui not in range_:
        raise ValueError("Input must be between {} and {}".format(start, stop))


def factor(P, use_saved_embedding=True):
    validate_input(P, range(2 ** 6))

    # get circuit
    construction_start_time = time.time()
    bqm, labels = three_bit_multiplier()

    # we know that three_bit_multiplier has created variables
    p_vars = ['p0', 'p1', 'p2', 'p3', 'p4', 'p5']

    # fix product qubits
    fixed_variables = dict(zip(reversed(p_vars), "{:06b}".format(P)))
    fixed_variables = {var: int(x) for (var, x) in fixed_variables.items()}
    for var, value in fixed_variables.items():
        bqm.fix_variable(var, value)
    log.debug('bqm construction time: %s', time.time() - construction_start_time)

    # find embedding and put on system
    sampler = DWaveSampler()

    kwargs = {}
    if 'num_reads' in sampler.parameters:
        kwargs['num_reads'] = 50
    if 'num_spin_reversal_transforms' in sampler.parameters:
        kwargs['num_spin_reversal_transforms'] = 1
    if 'answer_mode' in sampler.parameters:
        kwargs['answer_mode'] = 'histogram'

    sample_time = time.time()
    # apply the embedding to the given problem to map it to the child sampler
    _, target_edgelist, target_adjacency = sampler.structure

    if use_saved_embedding:
        from factoring.embedding import embedding
    else:
        # get the embedding
        embedding = minorminer.find_embedding(bqm.quadratic, target_edgelist)

        if bqm and not embedding:
            raise ValueError("no embedding found")

        # this should change in later versions
        if isinstance(embedding, list):
            embedding = dict(enumerate(embedding))

    bqm_embedded = dimod.embed_bqm(bqm, embedding, target_adjacency, 3.0)

    response = sampler.sample(bqm_embedded, **kwargs)

    response = dimod.unembed_response(response, embedding, source_bqm=bqm)
    logging.debug('embedding and sampling time: %s', time.time() - sample_time)

    output = {
        "results": [],
        #    {
        #        "a": Number,
        #        "b": Number,
        #        "valid": Boolean,
        #        "numOfOccurrences": Number,
        #        "percentageOfOccurrences": Number
        #    }
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
        "numberOfReads": None
    }

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
            a = (a << 1) | sample[lbl]
        for lbl in reversed(b_vars):
            b = (b << 1) | sample[lbl]

        if (a, b, P) in results_dict:
            results_dict[(a, b, P)]["numOfOccurrences"] += num_occurrences
            results_dict[(a, b, P)]["percentageOfOccurrences"] = 100 * \
                results_dict[(a, b, P)]["numOfOccurrences"] / total
        else:
            results_dict[(a, b, P)] = {"a": a,
                                       "b": b,
                                       "valid": a * b == P,
                                       "numOfOccurrences": num_occurrences,
                                       "percentageOfOccurrences": 100 * num_occurrences / total}

    output['results'] = list(results_dict.values())
    output['numberOfReads'] = total

    if 'timing' in response.info:
        output['timing']['actual']['qpuProcessTime'] = response.info['timing']['run_time_chip']

    return output
