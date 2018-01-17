import numpy as np
import dimod


def verifygate(pmodel, aux, func):
    """
    pmodel
    aux - index to start of variables to rollup (SHOULD BE NAMED INSTEAD OF NUMBERED)
    func - what to evaluate to determine validity of combination
    """
    es = dimod.ExactSolver()
    resp = es.sample_ising(pmodel.model.linear, pmodel.model.quadratic)
    resp = resp.as_binary()

    num = len(pmodel.model.linear)

    arr = labels = np.empty(shape=(2,) * num)
    for data in resp.data():
        arr[tuple(data['sample'].values())] = data['energy']
    rollup = np.min(arr, axis=tuple(range(aux, num)))
    for data in resp.data():
        args = tuple(data['sample'].values())[:aux]
        labels[args] = func(*args)

    return rollup, labels
