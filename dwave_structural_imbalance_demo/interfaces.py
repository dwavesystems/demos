import networkx as nx

import dwave_networkx as dnx
import dwave_qbsolv as qbsolv

from dwave_structural_imbalance_demo.mmp_network import global_signed_social_network

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

    def _get_graph(self, subregion='Global', year=None):
        G = self.maps[subregion]
        if year:
            filtered_edges = ((u, v) for u, v, a in G.edges(data=True) if a['event_year'] <= year)
            G = G.edge_subgraph(filtered_edges)
        return G

    def get_node_link_data(self, subregion='Global', year=None):
        G = self._get_graph(subregion, year)
        return nx.node_link_data(G)

    def solve_structural_imbalance(self, subregion='Global', year=None):
        G = self._get_graph(subregion, year)

        if _qpu:
            try:
                imbalance, bicoloring = dnx.structural_imbalance(G, self.embedding_composite)
                print("Ran on the QPU using EmbeddingComposite")
            except ValueError:
                imbalance, bicoloring = dnx.structural_imbalance(G, self.qbsolv, solver=self.embedding_composite)
                print("Ran on the QPU using QBSolv w/ EmbeddingComposite")
        else:
            if len(G) < 20:
                imbalance, bicoloring = dnx.structural_imbalance(G, self.exact_solver)
                print("Ran classically using ExactSolver")
            else:
                imbalance, bicoloring = dnx.structural_imbalance(G, self.qbsolv, solver='tabu')
                print("Ran classically using QBSolv")

        G = G.copy()
        for edge in G.edges:
            G.edges[edge]['frustrated'] = edge in imbalance
        for node in G.nodes:
            G.nodes[node]['color'] = bicoloring[node]

        return nx.node_link_data(G)
