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
    """A class encapsulating access to graphs from the Stanford Militants Mapping Project.

    Args:
        qpu (bool, optional):
            Specifies whether structural imblance problems will be solved on the QPU or CPU. Defaults to True if
            dwave-system is installed, False otherwise.

    Examples:
        >>> import dwave_structural_imbalance_demo as sbdemo
        >>> gssn = sbdemo.GlobalSignedSocialNetwork()
        >>> nld_before = gssn.get_node_link_data('Syria', 2013)
        >>> nld_before['nodes'][0]
        {'id': 1, 'map': 'Aleppo'}
        >>> nld_before['links'][0]
        {'event_description': 'Ahrar al-Sham and the Islamic State coordinated an attack on Alawite villages in the Latakia governorate that killed 190 civilians.',
         'event_id': '1821',
         'event_type': 'all',
         'event_year': 2013,
         'sign': 1,
         'source': 1,
         'target': 523}
        >>> nld_after = gssn.solve_structural_imbalance('Syria', 2013)
        >>> nld_after['nodes'][0]
        {'color': 0, 'id': 1, 'map': 'Aleppo'}
        >>> nld_after['links'][0]
        {'event_description': 'Ahrar al-Sham and the Islamic State coordinated an attack on Alawite villages in the Latakia governorate that killed 190 civilians.',
         'event_id': '1821',
         'event_type': 'all',
         'event_year': 2013,
         'frustrated': False,
         'sign': 1,
         'source': 1,
         'target': 523}

    """
    def __init__(self, qpu=_qpu):
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

        self._maps = maps
        self._qpu = qpu
        self._qbsolv = qbsolv.QBSolv()
        if qpu:
            self._embedding_composite = dwcomposites.EmbeddingComposite(dwsamplers.DWaveSampler())
        else:
            self._exact_solver = dimod.ExactSolver()

    def _get_graph(self, subregion='Global', year=None):
        G = self._maps[subregion]
        if year is not None:
            if not isinstance(year, int):
                raise ValueError("year must be int")
            filtered_edges = ((u, v) for u, v, a in G.edges(data=True) if a['event_year'] <= year)
            G = G.edge_subgraph(filtered_edges)
        return G

    def get_node_link_data(self, subregion='Global', year=None):
        """Accessor for Stanford Militants Mapping Project node link data.

        Args:
            subregion (str, optional):
                Filter graph by subregion. One of ['Global', 'Syria', 'Iraq']. Defaults to 'Global' (entire network).
            year (int, optional):
                Filter graph by year. Returns only events in or before year. Defaults to None (no filter applied).

        Returns:
            A dictionary with node-link formatted data. Conforms to dwave_structural_imbalance_demo.json_schema.

        """

        G = self._get_graph(subregion, year)
        return nx.node_link_data(G)

    def solve_structural_imbalance(self, subregion='Global', year=None):
        """Solves specified Stanford Militants Mapping Project structural imbalance problem and returns annotated graph.

        If self._qpu is True (set during object initialization), this function will first attempt to embed the entire
        problem on the hardware graph using EmbeddingComposite. Failing this, it will fallback on QBSolv to decompose
        the problem. If self._qpu is False, this function will use ExactSolver for problems with less than 20 nodes.
        For problems with 20 more more nodes, it will use QBSolv to solve the problem classically.

        Args:
            subregion (str, optional):
                Filter graph by subregion. One of ['Global', 'Syria', 'Iraq']. Defaults to 'Global' (entire network).
            year (int, optional):
                Filter graph by year. Returns only events in or before year. Defaults to None (no filter applied).

        Returns:
            A dictionary with node-link formatted data. Conforms to dwave_structural_imbalance_demo.json_schema.
            Optional property 'color' is set for each item in 'nodes'. Optional property 'frustrated' is set for each
            item in 'links'.

        """

        G = self._get_graph(subregion, year)

        if self._qpu:
            try:
                imbalance, bicoloring = dnx.structural_imbalance(G, self._embedding_composite)
                print("Ran on the QPU using dwave-system's EmbeddingComposite")
            except ValueError:
                imbalance, bicoloring = dnx.structural_imbalance(G, self._qbsolv, solver=self._embedding_composite)
                print("Ran on the QPU using Qbsolv and dwave-system's EmbeddingComposite")
        else:
            if len(G) < 20:
                imbalance, bicoloring = dnx.structural_imbalance(G, self._exact_solver)
                print("Ran classically using dimod's ExactSolver")
            else:
                imbalance, bicoloring = dnx.structural_imbalance(G, self._qbsolv, solver='tabu')
                print("Ran classically using Qbsolv")

        G = G.copy()
        for edge in G.edges:
            G.edges[edge]['frustrated'] = edge in imbalance
        for node in G.nodes:
            G.nodes[node]['color'] = bicoloring[node]

        return nx.node_link_data(G)
