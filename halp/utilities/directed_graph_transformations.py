"""
.. module:: directed_graph_transformations
   :synopsis: Defines several functions for transforming directed hypergraphs
            into various representations of graphs (where an edge connects
            exactly one node in the tail to one node in the head).

"""
import copy

from halp.directed_hypergraph import DirectedHypergraph


def to_graph_decomposition(H):
    """Returns a DirectedHypergraph object that has the same nodes (and
    corresponding attributes) as the given hypergraph, except that for all
    hyperedges in the given hypergraph, each node in the tail of the hyperedge
    is pairwise connected to each node in the head of the hyperedge in the
    new hypergraph.
    Said another way, each of the original hyperedges are decomposed in the
    new hypergraph into fully-connected bipartite components.

    :param H: the hypergraph to decompose into a graph.
    :returns: DirectedHypergraph -- the decomposed hypergraph.
    :raises: TypeError -- Transformation only applicable to
            directed hypergraphs

    """
    if not isinstance(H, DirectedHypergraph):
        raise TypeError("Transformation only applicable to \
                        directed hypergraphs")

    G = DirectedHypergraph()

    nodes = [(node, H.get_node_attributes(node_attributes))
             for node in G.node_iterator()]
    G.add_nodes(nodes)

    edges = [([tail_node], [head_node])
             for hyperedge_id in H.hyperedge_id_iterator()
             for tail_node in H.get_hyperedge_tail(hyperedge_id)
             for head_node in H.get_hyperedge_head(hyperedge_id)]
    G.add_hyperedges(edges)

    return G


def to_networkx_digraph(H):
    """Returns a NetworkX DiGraph object that is the graph decomposition of
    the given hypergraph.
    See "to_graph_decomposition()" for more details.

    :param H: the hypergraph to decompose into a graph.
    :returns: nx.DiGraph -- NetworkX DiGraph object representing the
            decomposed hypergraph.
    :raises: TypeError -- Transformation only applicable to
            directed hypergraphs

    """
    import networkx as nx

    if not isinstance(H, DirectedHypergraph):
        raise TypeError("Transformation only applicable to \
                        directed hypergraphs")

    G = to_graph_decomposition(H)

    nx_graph = nx.DiGraph()

    for node in G.node_iterator():
        nx_graph.add_node(node, G.get_node_attributes(node))

    for hyperedge_id in G.hyperedge_id_iterator():
        tail_node = G.get_hyperedge_tail(hyperedge_id).pop()
        head_node = G.get_hyperedge_head(hyperedge_id).pop()
        edge_attributes = G.get_hyperedge_attributes(hyperedge_id)
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

    G = DirectedHypergraph()

    for node in nx_digraph.nodes_iter():
        G.add_node(node, copy.copy(nx_digraph.node[node]))

    for edge in nx_digraph.edges_iter():
        tail_node = edge[0]
        head_node = edge[1]
        G.add_hyperedge(tail_node,
                        head_node,
                        copy.copy(nx_digraph[tail_node][head_node]))

    return G
