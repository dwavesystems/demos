import networkx as nx
import matplotlib.pyplot as plt


def visualize_map(nodes, edges, sample, node_positions=None):
    # Set up graph
    G = nx.Graph(edges)

    lone_nodes = set(nodes) - set(G.nodes)  # nodes without edges
    for lone_node in lone_nodes:
        G.add_node(lone_node)

    # Grab the colours selected by sample
    colour_labels = [k for k, v in sample.items() if v == 1]

    # Get colour order to match that of the graph nodes
    for label in colour_labels:
        name, colour = label.split("_")
        G.nodes[name]["colour"] = colour
    colour_map = [colour for name, colour in G.nodes(data="colour")]

    # Draw graph
    nx.draw_networkx(G, pos=node_positions, with_labels=True,
                     node_color=colour_map, font_color="w", node_size=400)

    # Save graph
    filename = "graph.png"
    plt.savefig(filename)
    print("The graph is saved in '{}'.".format(filename))
