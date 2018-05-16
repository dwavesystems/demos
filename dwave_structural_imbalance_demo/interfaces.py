from dwave_structural_imbalance_demo.mmp_network import global_signed_social_network

import dwave_qbsolv as qbsolv

import dwave_networkx as dnx

try:
    import dwave.system.samplers as dwsamplers
    import dwave.system.composites as dwcomposites
    _qpu = True
except ImportError:
    _qpu = False

import dimod


class GlobalSignedSocialNetwork(object):
    def __init__(self):
        maps = dict()
        maps['Global'] = global_signed_social_network()

        # The Syria subregion
        syria_groups = set()
        for v, data in maps['Global'].nodes(data=True):
            if 'map' not in data:
                continue
            if data['map'] in {'Syria', 'Aleppo'}:
                syria_groups.add(v)
        maps['Syria'] = maps['Global'].subgraph(syria_groups)

        # The Iraq subregion
        iraq_groups = set()
        for v, data in maps['Global'].nodes(data=True):
            if 'map' not in data:
                continue
            if data['map'] == 'Iraq':
                iraq_groups.add(v)
        maps['Iraq'] = maps['Global'].subgraph(iraq_groups)

        self.maps = maps
        self.qbsolv = qbsolv.QBSolv()
        if _qpu:
            self.embedding_composite = dwcomposites.EmbeddingComposite(dwsamplers.DWaveSampler())
        self.exact_solver = dimod.ExactSolver()

    def get_graph(self, subregion='Global', year=None):
        graph = self.maps[subregion]
        if year:
            filtered_edges = ((u, v) for u, v, a in graph.edges(data=True) if a['event_date'].year <= year)
            graph = graph.edge_subgraph(filtered_edges)
        return graph

    def get_weighted_edges(self, subregion='Global', year=None):
        # from networkx import node_link_data
        graph = self.get_graph(subregion, year)
        return list(graph.edges(data='sign'))

    def solve_structural_imbalance(self, subregion='Global', year=None):
        graph = self.get_graph(subregion, year)
        print(subregion,year)
        if _qpu:
            try:
                imbalance, bicoloring = dnx.structural_imbalance(graph, self.embedding_composite)
                print("EmbeddingComposite")
            except ValueError:
                imbalance, bicoloring = dnx.structural_imbalance(graph, self.qbsolv, solver=self.embedding_composite)
                print("QBSolv w/ EmbeddingComposite")
        else:
            if len(graph) < 20:
                imbalance, bicoloring = dnx.structural_imbalance(graph, self.exact_solver)
                print("ExactSolver")
            else:
                imbalance, bicoloring = dnx.structural_imbalance(graph, self.qbsolv, solver='tabu')
                print("QBSolv w/o QPU")
        return {'imbalance': imbalance, 'bicoloring': bicoloring}
