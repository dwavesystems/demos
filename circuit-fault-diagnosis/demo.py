import sys

import pandas as pd

from dwave_circuit_fault_diagnosis_demo import three_bit_multiplier, GATES

try:
    from dwave.system.samplers import DWaveSampler
    from dwave.system.composites import EmbeddingComposite
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
    bqm, labels = three_bit_multiplier()

    ####################################################################################################
    # get input from user
    ####################################################################################################

    fixed_variables = {}

    print("Enter the test conditions")

    A = sanitised_input("multiplier", "A", range(2**3))
    fixed_variables.update(zip(('a2', 'a1', 'a0'), "{:03b}".format(A)))

    B = sanitised_input("multiplicand", "B", range(2**3))
    fixed_variables.update(zip(('b2', 'b1', 'b0'), "{:03b}".format(B)))

    P = sanitised_input("product", "P", range(2**6))
    fixed_variables.update(zip(('p5', 'p4', 'p3', 'p2', 'p1', 'p0'), "{:06b}".format(P)))

    print("\nA   =    {:03b}".format(A))
    print("B   =    {:03b}".format(B))
    print("A*B = {:06b}".format(A * B))
    print("P   = {:06b}\n".format(P))

    fixed_variables = {var: 1 if x == '1' else -1 for (var, x) in fixed_variables.items()}

    # fix variables
    for var, value in fixed_variables.items():
        bqm.fix_variable(var, value)
    # 'aux1' becomes disconnected, so needs to be fixed
    bqm.fix_variable('aux1', 1)  # don't care value

    if _qpu:
        # find embedding and put on system
        print("Running using QPU\n")
        sampler = EmbeddingComposite(DWaveSampler())
        response = sampler.sample_ising(bqm.linear, bqm.quadratic, num_reads=NUM_READS)
    else:
        # if no qpu access, use qbsolv's tabu
        print("Running using qbsolv's classical tabu search\n")
        sampler = qbsolv.QBSolv()
        response = sampler.sample_ising(bqm.linear, bqm.quadratic)

    ####################################################################################################
    # output results
    ####################################################################################################

    # responses are sorted in order of increasing energy, so the first energy is the minimum
    min_energy = next(response.data()).energy

    best_samples = [dict(datum.sample) for datum in response.data() if datum.energy == min_energy]
    for sample in best_samples:
        for variable in list(sample.keys()):
            if 'aux' in variable:
                sample.pop(variable)
        sample.update(fixed_variables)

    best_results = []
    for sample in best_samples:
        result = {}
        for gate_type, gates in sorted(labels.items()):
            _, configurations = GATES[gate_type]
            for gate_name, gate in sorted(gates.items()):
                result[gate_name] = 'valid' if tuple(sample[var] for var in gate) in configurations else 'fault'
        best_results.append(result)
    best_results = pd.DataFrame(best_results)

    # at this point, our filtered "best results" all have the same number of faults, so just grab the first one
    num_faults = next(best_results.itertuples()).count('fault')

    # num_ground_samples = len(best_results)
    # best_results = best_results.groupby(best_results.columns.tolist(), as_index=False).size().reset_index().set_index(0)
    best_results = best_results.drop_duplicates().reset_index(drop=True)
    num_ground_states = len(best_results)

    print("The minimum fault diagnosis found is {} faulty component(s)".format(num_faults))
    # print("Out of {} samples, the following {} ground states were returned a total of {} times:".format(
    #     NUM_READS, num_ground_states, num_ground_samples))
    print("{} distinct fault state(s) with this many faults observed".format(num_ground_states))

    # verbose output
    if len(sys.argv) == 2 and sys.argv[1] == '--verbose':
        pd.set_option('display.width', 120)
        print(best_results)
