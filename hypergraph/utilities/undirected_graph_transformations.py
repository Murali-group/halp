"""
.. module:: undirected_graph_transformations
   :synopsis: Defines several functions for transforming undirected hypergraphs
            into various representations of graphs (where an edge connects
            exactly two nodes together).

"""
import copy

from hypergraph.undirected_hypergraph import UndirectedHypergraph


def to_graph_decomposition(H):
    """Returns an UndirectedHypergraph object that has the same nodes (and
    corresponding attributes) as the given hypergraph, except that for all
    hyperedges in the given hypergraph, each node in the hyperedge is pairwise
    connected to every other node also in that hyperedge in the new hypergraph.
    Said another way, each of the original hyperedges are decomposed in the
    new hypergraph into cliques (aka the "2-section" or "clique graph").

    :param H: the hypergraph to decompose into a graph.
    :returns: UndirectedHypergraph -- the decomposed hypergraph.
    :raises: TypeError -- Transformation only applicable to
            undirected hypergraphs

    """
    if not isinstance(H, UndirectedHypergraph):
        raise TypeError("Transformation only applicable to \
                        undirected hypergraphs")

    G = UndirectedHypergraph()

    nodes = [(node, H.get_node_attributes(node_attributes))
             for node in G.node_iterator()]
    G.add_nodes(nodes)

    edges = [(node_a, node_b)
             for hyperedge_id in H.hyperedge_id_iterator()
             for node_a in H.get_hyperedge_nodes(hyperedge_id)
             for node_b in H.get_hyperedge_nodes(hyperedge_id)
             if node_a != node_b]

    G.add_hyperedges(edges)

    return G


def to_networkx_graph(H):
    """Returns a NetworkX Graph object that is the graph decomposition of
    the given hypergraph.
    See "to_graph_decomposition()" for more details.

    :param H: the hypergraph to decompose into a graph.
    :returns: nx.Graph -- NetworkX Graph object representing the
            decomposed hypergraph.
    :raises: TypeError -- Transformation only applicable to
            undirected hypergraphs

    """
    import networkx as nx

    if not isinstance(H, UndirectedHypergraph):
        raise TypeError("Transformation only applicable to \
                        undirected hypergraphs")

    G = to_graph_decomposition(H)

    nx_graph = nx.Graph()

    for node in G.node_iterator():
        nx_graph.add_node(node, G.get_node_attributes(node))

    for hyperedge_id in G.hyperedge_id_iterator():
        edge_nodes = G.get_hyperedge_nodes(hyperedge_id)
        edge_attributes = G.get_hyperedge_attributes(hyperedge_id)
        nx_graph.add_edge(edge_nodes[0], edge_nodes[1], edge_attributes)

    return nx_graph


def from_networkx_graph(nx_graph):
    """Returns an UndirectedHypergraph object that is the graph equivalent of
    the given NetworkX Graph object.

    :param nx_graph: the NetworkX undirected graph object to transform.
    :returns: UndirectedHypergraph -- hypergraph object equivalent to the
            NetworkX undirected graph.
    :raises: TypeError -- Transformation only applicable to undirected
            NetworkX graphs

    """
    import networkx as nx

    if not isinstance(nx_graph, nx.Graph):
        raise TypeError("Transformation only applicable to undirected \
                        NetworkX graphs")

    G = UndirectedHypergraph()

    for node in nx_graph.nodes_iter():
        G.add_node(node, copy.copy(nx_graph.node[node]))

    for edge in nx_graph.edges_iter():
        G.add_hyperedge([edge[0], edge[1]],
                        copy.copy(nx_graph[edge[0]][edge[1]]))

    return G
