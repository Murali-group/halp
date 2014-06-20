"""
.. module:: connectivity
   :synopsis: Defines several functions for executing various connectivity
            queries on a directed hypergraph.

"""

from __future__ import absolute_import
try:
    from queue import Queue
except ImportError:
    from Queue import Queue

from hypergraph.directed_hypergraph import DirectedHypergraph

# TODO-A: consider including target_node (with default value as None) in visit
# and b-visit to allow for early stoppage in an is_connected check and in an
# is_b_connected check
# TODO-B: consider maybe also caching the results from one execution of
# is_connected and is_b_connected to be able to check many node's for
# connectivity in only a single call of either visit or b_visit


def visit(hypergraph, source_node):
    """Executes the 'Visit' algorithm described in the paper:
    Giorgio Gallo, Giustino Longo, Stefano Pallottino, Sang Nguyen,
    Directed hypergraphs and applications, Discrete Applied Mathematics,
    Volume 42, Issues 2-3, 27 April 1993, Pages 177-201, ISSN 0166-218X,
    http://dx.doi.org/10.1016/0166-218X(93)90045-P.
    (http://www.sciencedirect.com/science/article/pii/0166218X9390045P)

    :param hypergraph: the hypergraph to perform the 'Visit' algorithm on
    :param source_node: the initial node to begin traversal from
    :returns: set -- nodes that were visited in this traversal
              dict -- mapping from nodes to the ID hyperedges that preceeded
                    them in this traversal; will map a node to None if that
                    node wasn't visited or if that node is the source node
              dict -- mapping from hyperedge IDs to the nodes that preceeded
                    them in this traversal

    """
    if not isinstance(hypergraph, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    node_set = hypergraph.get_node_set()
    # Pv keeps track of the ID of the hyperedge that directely
    # preceeded each node in the traversal
    Pv = {node: None for node in node_set}

    hyperedge_id_set = hypergraph.get_hyperedge_id_set()
    # Pe keeps track of the node that directedly preceeded
    # each hyperedge in the traversal
    Pe = {hyperedge_id: None for hyperedge_id in hyperedge_id_set}

    # Explicitly tracks the set of visited nodes
    visited_nodes = set(source_node)

    Q = Queue()
    Q.put(source_node)

    while not Q.empty():
        current_node = Q.get()
        # At current_node, we can traverse each hyperedge in its forward star
        for hyperedge_id in hypergraph.get_forward_star(current_node):
            if Pe[hyperedge_id] is not None:
                continue
            Pe[hyperedge_id] = current_node
            # Traversing a hyperedge in current_node's forward star yields
            # the set of head nodes of the hyperedge; visit each head node
            for head_node in hypergraph.get_hyperedge_head(hyperedge_id):
                if head_node in visited_nodes:
                    continue
                Pv[head_node] = hyperedge_id
                Q.put(head_node)
                visited_nodes.add(head_node)

    return visited_nodes, Pv, Pe


def is_connected(hypergraph, source_node, target_node):
    """Checks if a target node is connected to a source node. That is,
    this method determines if a target node can be visited from the source
    node in the sense of the 'Visit' algorithm. Refer to 'Visit's
    documentation for more details.

    :param hypergraph: the hypergraph to check connectedness on
    :param source_node: the node to check connectedness to
    :param target_node: the node to check connectedness of
    :returns: bool -- whether target_node can be visited from source_node

    """
    visited_nodes, Pv, Pe = visit(hypergraph, source_node)
    return target_node in visited_nodes


def b_visit(hypergraph, source_node):
    """Executes the 'B-Visit' algorithm described in the paper:
    Giorgio Gallo, Giustino Longo, Stefano Pallottino, Sang Nguyen,
    Directed hypergraphs and applications, Discrete Applied Mathematics,
    Volume 42, Issues 2-3, 27 April 1993, Pages 177-201, ISSN 0166-218X,
    http://dx.doi.org/10.1016/0166-218X(93)90045-P.
    (http://www.sciencedirect.com/science/article/pii/0166218X9390045P)

    :param hypergraph: the hypergraph to perform the 'B-Visit' algorithm on
    :param source_node: the initial node to begin traversal from
    :returns: set -- nodes that were visited in this traversal
              dict -- mapping from nodes to the ID hyperedges that preceeded
                    them in this traversal
              dict -- mapping from hyperedge IDs to the nodes that preceeded
                    them in this traversal

    """
    if not isinstance(hypergraph, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    node_set = hypergraph.get_node_set()
    # Pv keeps track of the ID of the hyperedge that directely
    # preceeded each node in the traversal
    Pv = {node: None for node in node_set}

    # v keeps track of the cardinality of the path from the source node to
    # any other B-connected node ('inf' cardinality for non-B-connected nodes)
    v = {node: float("inf") for node in node_set}
    v[source_node] = 0

    hyperedge_id_set = hypergraph.get_hyperedge_id_set()
    # Pe keeps track of the node that directedly preceeded
    # each hyperedge in the traversal
    Pe = {hyperedge_id: None for hyperedge_id in hyperedge_id_set}

    # k keeps track of how many nodes in the tail of each hyperedge are
    # B-connected (when all nodes in a tail are B-connected, that hyperedge
    # can then be traversed)
    k = {hyperedge_id: 0 for hyperedge_id in hyperedge_id_set}

    # Explicitly tracks the set of B-visited nodes
    b_visited_nodes = set(source_node)

    Q = Queue()
    Q.put(source_node)

    while not Q.empty():
        current_node = Q.get()
        # At current_node, we can traverse each hyperedge in its forward star
        for hyperedge_id in hypergraph.get_forward_star(current_node):
            # Since we're arrived at a new node, we increment
            # k[hyperedge_id] to indicate that we've reached 1 new
            # node in this hyperedge's tail
            k[hyperedge_id] = k[hyperedge_id] + 1
            # Traverse this hyperedge only when we have reached all the nodes
            # in its tail (i.e., when k[hyperedge_id] == |T(hyperedge_id)|)
            if k[hyperedge_id] == \
               len(hypergraph.get_hyperedge_tail(hyperedge_id)):
                Pe[hyperedge_id] = current_node
                # Traversing the hyperedge yields the set of head nodes of
                # the hyperedge; B-visit each head node
                for head_node in hypergraph.get_hyperedge_head(hyperedge_id):
                    if head_node in b_visited_nodes:
                        continue
                    Pv[head_node] = hyperedge_id
                    Q.put(head_node)
                    v[head_node] = v[Pe[hyperedge_id]] + 1
                    b_visited_nodes.add(head_node)

    return b_visited_nodes, Pv, Pe, v


def is_b_connected(hypergraph, source_node, target_node):
    """Checks if a target node is B-connected to a source node.
    A node t is B-connected to a node s iff:
        - t is s, or
        - there exists an edge in the backward star of t such that all nodes in
        the tail of that edge are B-connected to s
    In other words, this method determines if a target node can be B-visited
    from the source node in the sense of the 'B-Visit' algorithm. Refer to
    'B-Visit's documentation for more details.

    :param hypergraph: the hypergraph to check B-connectedness on
    :param source_node: the node to check B-connectedness to
    :param target_node: the node to check B-connectedness of
    :returns: bool -- whether target_node can be visited from source_node

    """
    b_visited_nodes, Pv, Pe, v = b_visit(hypergraph, source_node)
    return target_node in b_visited_nodes
