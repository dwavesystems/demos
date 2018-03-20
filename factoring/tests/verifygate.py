import pandas as pd
import dimod


def verifygate(bqm, vars):
    es = dimod.ExactSolver()
    resp = es.sample_ising(bqm.linear, bqm.quadratic)
    resp = resp.as_binary()
    # Q = {(k, k): v for k, v in bqm.linear.items()}
    # Q.update(bqm.quadratic)
    # resp = es.sample_qubo(Q)

    df = pd.DataFrame([dict(data['sample'], **{'energy': data['energy']}) for data in resp.data()])

    return df.groupby(vars).energy.agg(min).reset_index().sort_values('energy')
