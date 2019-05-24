# Import networkx for graph tools
import networkx as nx

# Import dwave_networkx for d-wave functions
import dwave_networkx as dnx

# Import matplotlib.pyplot to draw graphs on screen
import matplotlib.pyplot as plt

# Set the solver we're going to use
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite

sampler = EmbeddingComposite(DWaveSampler())

# Create empty graph
G = nx.Graph()

# Add edges to graph - this also adds the nodes
G.add_edges_from([(1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5), (4, 6), (5, 6), (6, 7)])

# Find the maximum independent set, S
S = dnx.maximum_independent_set(G, sampler=sampler, num_reads=10)

# Print the solution for the user
print('Maximum independent set size found is', len(S))
print(S)

# TODO: add indices to the plotted nodes
# Visualize the results
#   Red nodes are in the set, blue nodes are not
k = G.subgraph(S)
notS = list(set(G.nodes()) - set(S))
othersubgraph = G.subgraph(notS)
pos = nx.spring_layout(G)
plt.figure()
nx.draw(G, pos=pos)
nx.draw(k, pos=pos, node_color='r')
nx.draw(othersubgraph, pos=pos, node_color='b')

# Save plot
plot_name = "antenna_plot.png"
plt.savefig(plot_name, bbox_inches='tight')
print("Your plot has been saved to {}".format(plot_name))
