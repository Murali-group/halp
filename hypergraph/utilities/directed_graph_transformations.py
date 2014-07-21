"""
.. module:: directed_graph_transformations
   :synopsis: Defines several functions for transforming directed hypergraphs
            into various representations of graphs (where an edge connects
            exactly one node in the tail to one node in the head).

"""
import copy

from hypergraph.directed_hypergraph import DirectedHypergraph


def to_graph_decomposition(hypergraph):
    """Returns a DirectedHypergraph object that has the same nodes (and
    corresponding attributes as the given hypergraph, except that for all
    hyperedges in the given hypergraph, each node in the tail of the hyperedge
    is pairwise connected to each node in the head of the hyperedge in the
    new hypergraph.
    Said another way, each of the original hyperedges are decomposed in the
    new hypergraph into fully-connected bipartite components.

    :param hypergraph: the hypergraph to decompose into a graph.
    :returns: DirectedHypergraph -- the decomposed hypergraph.
    :raises: TypeError -- Transformation only applicable to
            directed hypergraphs

    """
    if not isinstance(hypergraph, DirectedHypergraph):
        raise TypeError("Transformation only applicable to \
                        directed hypergraphs")

    graph = DirectedHypergraph()

    nodes = [(node, hypergraph.get_node_attributes(node_attributes))
             for node in graph.node_iterator()]
    graph.add_nodes(nodes)

    edges = [([tail_node], [head_node])
             for hyperedge_id in hypergraph.hyperedge_id_iterator()
             for tail_node in hypergraph.get_hyperedge_tail(hyperedge_id)
             for head_node in hypergraph.get_hyperedge_head(hyperedge_id)]
    graph.add_hyperedges(edges)

    return graph


def to_networkx_digraph(hypergraph):
    """Returns a NetworkX DiGraph object that is the graph decomposition of
    the given hypergraph.
    See "to_graph_decomposition()" for more details.

    :param hypergraph: the hypergraph to decompose into a graph.
    :returns: nx.DiGraph -- NetworkX DiGraph object representing the
            decomposed hypergraph.
    :raises: TypeError -- Transformation only applicable to
            directed hypergraphs

    """
    import networkx as nx

    if not isinstance(hypergraph, DirectedHypergraph):
        raise TypeError("Transformation only applicable to \
                        directed hypergraphs")

    graph = to_graph_decomposition(hypergraph)

    nx_graph = nx.DiGraph()

    for node in graph.node_iterator():
        nx_graph.add_node(node, graph.get_node_attributes(node))

    for hyperedge_id in graph.hyperedge_id_iterator():
        tail_node = graph.get_hyperedge_tail(hyperedge_id).pop()
        head_node = graph.get_hyperedge_head(hyperedge_id).pop()
        edge_attributes = graph.get_hyperedge_attributes(hyperedge_id)
        nx_graph.add_edge(tail_node, head_node, edge_attributes)

    return nx_graph


def from_networkx_digraph(nx_digraph):
    """Returns a DirectedHypergraph object that is the graph equivalent of the
    given NetworkX DiGraph object.

    :param nx_digraph: the NetworkX directed graph object to transform.
    :returns: DirectedHypergraph -- hypergraph object equivalent to the
            NetworkX directed graph.
    :raises: TypeError -- Transformation only applicable to directed
            NetworkX graphs

    """
    import networkx as nx

    if not isinstance(nx_digraph, nx.DiGraph):
        raise TypeError("Transformation only applicable to directed \
                        NetworkX graphs")

    graph = DirectedHypergraph()

    for node in nx_digraph.nodes_iter():
        graph.add_node(node, copy.copy(nx_digraph.node[node]))

    for edge in nx_digraph.edges_iter():
        tail_node = edge[0]
        head_node = edge[1]
        graph.add_hyperedge(tail_node,
                            head_node,
                            copy.copy(nx_digraph[tail_node][head_node]))

    return graph
