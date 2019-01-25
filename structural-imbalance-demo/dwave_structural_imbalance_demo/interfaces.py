from collections import OrderedDict

import networkx as nx

import dwave_networkx as dnx

from neal import SimulatedAnnealingSampler
from dwave.system.composites import EmbeddingComposite
from dwave.system.samplers import DWaveSampler
import dwave.cloud.exceptions

from dwave_structural_imbalance_demo.mmp_network import global_signed_social_network

# compatibility for python 2/3
if dnx._PY2:
    def iteritems(d): return d.iteritems()
else:
    def iteritems(d): return d.items()


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

    def __init__(self, qpu):
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
        self._init_sampler()

    def _init_sampler(self):
        """Allows for re-init in case a solver goes offline."""

        if self._qpu:
            # select the first available sampler in the `DW_2000Q` class
            self._sampler = EmbeddingComposite(DWaveSampler(solver=dict(qpu=True)))
        else:
            self._sampler = SimulatedAnnealingSampler()

        self._sampler_args = {}
        if 'num_reads' in self._sampler.parameters:
            self._sampler_args['num_reads'] = 50
        if 'answer_mode' in self._sampler.parameters:
            self._sampler_args['answer_mode'] = 'histogram'
        if 'chain_strength' in self._sampler.parameters:
            self._sampler_args['chain_strength'] = 2.0

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
        return {"results": [nx.node_link_data(G)]}

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

        G_in = self._get_graph(subregion, year)
        if len(G_in) == 0:
            raise ValueError("Filtered network has no nodes to solve problem on")

        h, J = dnx.social.structural_imbalance_ising(G_in)

        # <10% of the time it will fail to find an embedding, so keep trying
        while True:
            try:
                # use the sampler to find low energy states
                response = self._sampler.sample_ising(h, J, **self._sampler_args)
                break
            except ValueError:
                pass
            except dwave.cloud.exceptions.SolverOfflineError:
                # if solver goes offline while sampling (or while in queue),
                # retry with another (online) solver
                self._init_sampler()

        # histogram answer_mode should return counts for unique solutions
        if 'num_occurrences' not in response.data_vectors:
            response.data_vectors['num_occurrences'] = [1] * len(response)

        # should equal num_reads
        total = sum(response.data_vectors['num_occurrences'])

        results_dict = OrderedDict()

        for sample, num_occurrences in response.data(['sample', 'num_occurrences']):
            # spins determine the color
            colors = {v: (spin + 1) // 2 for v, spin in iteritems(sample)}

            key = tuple(colors.values())
            if key in results_dict:
                results_dict[key].graph["numOfOccurrences"] += num_occurrences
                results_dict[key].graph["percentageOfOccurrences"] = 100 * \
                    results_dict[key].graph["numOfOccurrences"] / total
            else:
                G = G_in.copy()
                # frustrated edges are the ones that are violated
                frustrated_edges = {}
                for u, v, data in G.edges(data=True):
                    sign = data['sign']
                    if sign > 0 and colors[u] != colors[v]:
                        frustrated_edges[(u, v)] = data
                    elif sign < 0 and colors[u] == colors[v]:
                        frustrated_edges[(u, v)] = data
                    # else: not frustrated or sign == 0, no relation to violate
                for edge in G.edges:
                    G.edges[edge]['frustrated'] = edge in frustrated_edges
                for node in G.nodes:
                    G.nodes[node]['color'] = colors[node]
                G.graph['numOfOccurrences'] = num_occurrences
                G.graph['percentageOfOccurrences'] = 100 * num_occurrences / total
                results_dict[key] = G

        output = {'results': [nx.node_link_data(result) for result in results_dict.values()], 'numberOfReads': total}
        if 'timing' in response.info:
            output['timing'] = {"actual": {"qpuProcessTime": response.info['timing']['qpu_access_time']}}
        return output
