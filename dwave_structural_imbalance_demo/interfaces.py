from dwave_structural_imbalance_demo.mmp_network import maps

def get_map(subregion='Global', year=None):
    graphs = maps()

    graph = graphs[subregion]

    if year:
        filtered_edges = ((u, v) for u, v, a in graph.edges(data=True) if a['event_date'].year <= year)
        graph = graph.edge_subgraph(filtered_edges)

    return list(graph.edges(data='sign'))
