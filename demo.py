import dwave_micro_client_dimod as system

from dwave_circuit_fault_diagnosis_demo import *  # TODO


def sanitised_input(description, variable, range_):
    while True:
        ui = input("Input {0:15}({2.start:2} <= {1:1} < {2.stop:2}): ".format(description, variable, range_))

        try:
            ui = int(ui)
        except ValueError:
            print("Input type must be int")
            continue

        if ui not in range_:
            print("Input must be between {0.start} and {0.stop}".format(range_))
            continue

        return ui


if __name__ == '__main__':
    bqm, labels = three_bit_multiplier()

    # get input from user
    fixed_variables = {}

    A = sanitised_input("multiplier", "A", range(2**3))
    fixed_variables.update(zip(('a2', 'a1', 'a0'), "{:03b}".format(A)))

    B = sanitised_input("multiplicand", "B", range(2**3))
    fixed_variables.update(zip(('b2', 'b1', 'b0'), "{:03b}".format(B)))

    P = sanitised_input("product", "P", range(2**6))
    fixed_variables.update(zip(('p5', 'p4', 'p3', 'p2', 'p1', 'p0'), "{:06b}".format(P)))

    print("A   =    {:03b}".format(A))
    print("B   =    {:03b}".format(B))
    print("A*B = {:06b}".format(A * B))
    print("P   = {:06b}".format(P))
    print()

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
            if res in configurations:
                print('{} - valid {}'.format(gate_name, res))
            else:
                print('{} - fault {}'.format(gate_name, res))
