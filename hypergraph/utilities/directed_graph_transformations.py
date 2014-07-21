"""
.. module:: directed_graph_transformations
   :synopsis: Defines several functions for transforming directed hypergraphs
            into various representations of graphs (where an edge connects
            exactly one node in the tail to one node in the head).

"""
from hypergraph.directed_hypergraph import DirectedHypergraph


def to_graph_decomposition(hypergraph):
    """Returns a DirectedHypergraph object that has the same nodes as the
    given hypergraph, except that for all hyperedges in the given hypergraph,
    each node in the tail of the hyperedge is pairwise connected to each node
    in the head of the hyperedge in the new hypergraph.
    Said another way, each of the original hyperedges are decomposed in the
    new hypergraph into fully-connected bipartite components.

    :param hypergraph: the hypergraph to decompose into a graph.
    :returns: DirectedHypergraph -- the decomposed hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    if not isinstance(hypergraph, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    graph = DirectedHypergraph()
    edges = [([tail_node], [head_node])
             for hyperedge_id in hypergraph.hyperedge_id_iterator()
             for tail_node in hypergraph.get_hyperedge_tail(hyperedge_id)
             for head_node in hypergraph.get_hyperedge_head(hyperedge_id)]
    graph.add_hyperedges(edges)

    return graph
