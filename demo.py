import dwave_qbsolv as qbsolv

import dwave_networkx as dnx

try:
    import dwave_sapi2
    import dwave_sapi_dimod as sapi
    url = ''
    token = ''
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

    # get the graphs
    Global, Syria, Iraq = maps()

    # calculate the imbalance of Syria
    if _sapi:
        # use the QPU
        imbalance, bicoloring = dnx.structural_imbalance(Syria, sampler,
                                                         solver=sapi.SAPISampler, url=url, token=token)
    else:
        # use QBSolv in classical mode
        imbalance, bicoloring = dnx.structural_imbalance(Syria, sampler)

    # draw the syria graph
    sbdemo.draw('syria_imbalance.png', Syria, imbalance, bicoloring)
