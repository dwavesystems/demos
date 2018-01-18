import pandas as pd
import dimod


def verifygate(pmodel, vars):
    es = dimod.ExactSolver()
    resp = es.sample_ising(pmodel.model.linear, pmodel.model.quadratic)
    resp = resp.as_binary()

    df = pd.DataFrame([dict(data['sample'], **{'energy': data['energy']}) for data in resp.data()])

    return df.groupby(vars).energy.agg(min)
