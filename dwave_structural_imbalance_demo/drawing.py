import networkx as nx
import matplotlib.pyplot as plt


def draw(filename, S, imbalance, coloring, position=None):
    """Plot the given signed social network.

    Args:
        filename: The name of the file to be generated.
        S: The network
        imbalance: The set of frustrated edges.
        coloring: A two-coloring of the network
        position (optional): The position for the nodes.

    """

    if position is None:
        position = nx.circular_layout(S)

    # we need a consistent ordering of the edges
    edgelist = S.edges()
    nodelist = S.nodes()

    # get the colors assigned to each edge based on friendly/hostile
    sign_edge_color = [-S[u][v]['sign'] for u, v in edgelist]
    sign_node_color = [0 for __ in nodelist]
    sign_edge_style = ['solid' if S[u][v]['sign'] > 0 else 'dotted' for u, v in edgelist]

    # get the colors assigned to each node by coloring
    coloring_node_color = [-2 * coloring[v] + 1 for v in nodelist]

    # get the colors of the violated edges
    c1 = 1  # grey
    c2 = .61  # ochre
    coloring_edge_color = [c2 if (u, v) in imbalance else c1 for u, v in edgelist]
    edge_violation_style = ['dotted' if (u, v) in imbalance else 'solid' for u, v in edgelist]

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
            edge_color=coloring_edge_color,
            edge_cmap=plt.get_cmap('nipy_spectral'),
            )

    plt.savefig(filename, facecolor='white', dpi=500)
    plt.clf()