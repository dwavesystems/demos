import dwave_qbsolv as qbsolv

import dwave_networkx as dnx

try:
    import dwave_sapi2
    import dwave_sapi_dimod as sapi
    from sapi_token import url, token, solver_name
    _sapi = True
except ImportError:
    _sapi = False

import dwave_structural_imbalance_demo as sbdemo


def maps():
    Global = sbdemo.global_signed_social_network()

    # The Syria subregion
    syria_groups = set()
    for v, data in Global.nodes(data=True):
        if 'map' not in data:
            continue
        if data['map'] in {'Syria', 'Aleppo'}:
            syria_groups.add(v)
    Syria = Global.subgraph(syria_groups)

    # The Iraq subregion
    iraq_groups = set()
    for v, data in Global.nodes(data=True):
        if 'map' not in data:
            continue
        if data['map'] == 'Iraq':
            iraq_groups.add(v)
    Iraq = Global.subgraph(iraq_groups)

    return Global, Syria, Iraq

if __name__ == '__main__':
    # get a sampler
    sampler = qbsolv.QBSolv()

    _sapi=False
    if _sapi:
        print("Running on the QPU")
        subsolver = sapi.EmbeddingComposite(sapi.SAPISampler(solver_name, url, token))
    else:
        print("Running classically")
        subsolver = None

    # get the graphs
    Global, Syria, Iraq = maps()

    # calculate the imbalance of Global
    imbalance, bicoloring = dnx.structural_imbalance(Global, sampler, solver=subsolver)

    # draw the Global graph
    sbdemo.draw('syria_imbalance.png', Global, imbalance, bicoloring)
