from collections import defaultdict
from itertools import product

import networkx as nx


def draw(filename, node_link_data, position=None):
    """Plot the given signed social network.

    Args:
        filename (string):
            The name of the file to be generated.
        node_link_data (dict):
            The network represented as returned by nx.node_link_data(). Each edge is required to have a 'sign'
            attribute. Optionally, edges can have 'frustrated' attributes and nodes can have 'color' attributes.
        position (dict, optional):
            The position for the nodes. If no position is provided, a layout will be calculated. If the nodes have
            'color' attributes, a Kamanda-Kawai layout will be used to group nodes of the same color together.
            Otherwise, a circular layout will be used.

    Returns:
        A dictionary of positions keyed by node.

    Examples:
    >>> import dwave_structural_imbalance_demo as sbdemo
    >>> gssn = sbdemo.GlobalSignedSocialNetwork()
    >>> nld_before = gssn.get_node_link_data('Syria', 2013)
    >>> nld_after = gssn.solve_structural_imbalance('Syria', 2013)
    # draw Global graph before solving; save node layout for reuse
    >>> position = sbdemo.draw('syria.png', nld_before)
    # draw the Global graph; reusing the above layout, and calculating a new grouped layout
    >>> sbdemo.draw('syria_imbalance.png', nld_after, position)
    >>> sbdemo.draw('syria_imbalance_grouped', nld_after)

    """

    import matplotlib.pyplot as plt

    S = nx.node_link_graph(node_link_data)

    # we need a consistent ordering of the edges
    edgelist = S.edges()
    nodelist = S.nodes()

    if position is None:
        try:
            # group bipartition if nodes are colored
            dist = defaultdict(dict)
            for u, v in product(nodelist, repeat=2):
                if u == v: # node has no distance from itself
                    dist[u][v] = 0
                elif nodelist[u]['color'] == nodelist[v]['color']: # make same color nodes closer together
                    dist[u][v] = 1
                else: # make different color nodes further apart
                    dist[u][v] = 2
            position = nx.kamada_kawai_layout(S, dist)
        except KeyError:
            # default to circular layout if nodes aren't colored
            position = nx.circular_layout(S)

    # get the colors assigned to each edge based on friendly/hostile
    sign_edge_color = [S[u][v]['sign'] for u, v in edgelist]

    # get the colors assigned to each node by coloring
    try:
        coloring_node_color = [-2 * nodelist[v]['color'] + 1 for v in nodelist]
    except KeyError:
        coloring_node_color = [0 for __ in nodelist]

    # get the styles of the violated edges
    try:
        edge_violation_style = ['dotted' if S[u][v]['frustrated'] else 'solid' for u, v in edgelist]
    except KeyError:
        edge_violation_style = ['solid' for __ in edgelist]

    # draw the the coloring
    nx.draw(S,
            node_size=100,
            pos=position,
            cmap=plt.get_cmap('bwr'),
            vmin=-1, vmax=1,
            edge_vmin=-1, edge_vmax=1,
            edgelist=edgelist, nodelist=nodelist,
            width=2,
            node_color=coloring_node_color,
            edge_color=sign_edge_color,
            edge_cmap=plt.get_cmap('RdYlGn'),
            edgecolors='black',
            style=edge_violation_style
            )

    plt.savefig(filename, facecolor='white', dpi=500)
    plt.clf()

    return position
