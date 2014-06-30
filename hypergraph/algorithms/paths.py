"""
.. module:: paths
   :synopsis: Defines several functions for executing various
   path/connectivity queries on a directed hypergraph.

"""

try:
    from queue import Queue
    from queue import PriorityQueue
except ImportError:
    from Queue import Queue
    from Queue import PriorityQueue

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

    :param hypergraph: the hypergraph to perform the 'Visit' algorithm on.
    :param source_node: the initial node to begin traversal from.
    :returns: set -- nodes that were visited in this traversal.
              dict -- mapping from each node to the ID of the hyperedge that
                    preceeded it in this traversal; will map a node to None if that
                    node wasn't visited or if that node is the source node.
              dict -- mapping from each hyperedge ID to the node that preceeded
                    it in this traversal.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

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

    :param hypergraph: the hypergraph to check connectedness on.
    :param source_node: the node to check connectedness to.
    :param target_node: the node to check connectedness of.
    :returns: bool -- whether target_node can be visited from source_node.

    """
    visited_nodes, Pv, Pe = visit(hypergraph, source_node)
    return target_node in visited_nodes


def _x_visit(hypergraph, source_node, b_visit):
    """General form of the B-Visit algorithm, extended to also perform
    an implicit F-Visit if the b_visit flag is not set (providing better
    time/memory performance than explcitily taking the hypergraph's
    symmetric image and then performing the B-Visit on that).

    :param hypergraph: the hypergraph to perform the 'B-Visit' algorithm on.
    :param source_node: the initial node to begin traversal from.
    :param b_visit: boolean flag representing whether a B-Visit should
                    be performed.
    :returns: set -- nodes that were x-visited in this traversal.
              dict -- mapping from each node visited to the ID of the hyperedge
                    that preceeded it in this traversal.
              dict -- mapping from each hyperedge ID to the node that preceeded
                    it in this traversal.
              dict -- mapping from each node to an integer representing the
                    cardinality of the path from the source node to that node.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    if not isinstance(hypergraph, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    # If the b_visit flag is set, perform a traditional B-Visit
    if b_visit:
        forward_star = hypergraph.get_forward_star
        hyperedge_tail = hypergraph.get_hyperedge_tail
        hyperedge_head = hypergraph.get_hyperedge_head
    # If the b_visit flag is not set, implicitly perform an F-Visit by
    # implicitly taking the symmetric image (what the 'else' statement
    # is for) and then performing a traditional B-Visit
    else:
        forward_star = hypergraph.get_backward_star
        hyperedge_tail = hypergraph.get_hyperedge_head
        hyperedge_head = hypergraph.get_hyperedge_tail

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
    x_visited_nodes = set(source_node)

    Q = Queue()
    Q.put(source_node)

    while not Q.empty():
        current_node = Q.get()
        # At current_node, we can traverse each hyperedge in its forward star
        for hyperedge_id in forward_star(current_node):
            # Since we're arrived at a new node, we increment
            # k[hyperedge_id] to indicate that we've reached 1 new
            # node in this hyperedge's tail
            k[hyperedge_id] += 1
            # Traverse this hyperedge only when we have reached all the nodes
            # in its tail (i.e., when k[hyperedge_id] == |T(hyperedge_id)|)
            if k[hyperedge_id] == len(hyperedge_tail(hyperedge_id)):
                Pe[hyperedge_id] = current_node
                # Traversing the hyperedge yields the set of head nodes of
                # the hyperedge; B-visit each head node
                for head_node in hyperedge_head(hyperedge_id):
                    if head_node in x_visited_nodes:
                        continue
                    Pv[head_node] = hyperedge_id
                    Q.put(head_node)
                    v[head_node] = v[Pe[hyperedge_id]] + 1
                    x_visited_nodes.add(head_node)

    return x_visited_nodes, Pv, Pe, v


def b_visit(hypergraph, source_node):
    """Executes the 'B-Visit' algorithm described in the paper:
    Giorgio Gallo, Giustino Longo, Stefano Pallottino, Sang Nguyen,
    Directed hypergraphs and applications, Discrete Applied Mathematics,
    Volume 42, Issues 2-3, 27 April 1993, Pages 177-201, ISSN 0166-218X,
    http://dx.doi.org/10.1016/0166-218X(93)90045-P.
    (http://www.sciencedirect.com/science/article/pii/0166218X9390045P)

    :param hypergraph: the hypergraph to perform the 'B-Visit' algorithm on.
    :param source_node: the initial node to begin traversal from.
    :returns: set -- nodes that were B-visited in this traversal.
              dict -- mapping from each node visited to the ID of the hyperedge
                    that preceeded it in this traversal.
              dict -- mapping from each hyperedge ID to the node that preceeded
                    it in this traversal.
              dict -- mapping from each node to an integer representing the
                    cardinality of the path from the source node to that node.

    """
    return _x_visit(hypergraph, source_node, True)


def is_b_connected(hypergraph, source_node, target_node):
    """Checks if a target node is B-connected to a source node.
    A node t is B-connected to a node s iff:
        - t is s, or
        - there exists an edge in the backward star of t such that all nodes in
        the tail of that edge are B-connected to s
    In other words, this method determines if a target node can be B-visited
    from the source node in the sense of the 'B-Visit' algorithm. Refer to
    'B-Visit's documentation for more details.

    :param hypergraph: the hypergraph to check B-connectedness on.
    :param source_node: the node to check B-connectedness to.
    :param target_node: the node to check B-connectedness of.
    :returns: bool -- whether target_node can be visited from source_node.

    """
    b_visited_nodes, Pv, Pe, v = b_visit(hypergraph, source_node)
    return target_node in b_visited_nodes


def f_visit(hypergraph, source_node):
    """Executes the 'F-Visit' algorithm alluded to in the paper:
    Giorgio Gallo, Giustino Longo, Stefano Pallottino, Sang Nguyen,
    Directed hypergraphs and applications, Discrete Applied Mathematics,
    Volume 42, Issues 2-3, 27 April 1993, Pages 177-201, ISSN 0166-218X,
    http://dx.doi.org/10.1016/0166-218X(93)90045-P.
    (http://www.sciencedirect.com/science/article/pii/0166218X9390045P)

    :param hypergraph: the hypergraph to perform the 'F-Visit' algorithm on.
    :param source_node: the initial node to begin traversal from.
    :returns: set -- nodes that were F-visited in this traversal.
              dict -- mapping from each node to the ID of the hyperedge that
                    preceeded it in this traversal.
              dict -- mapping from each hyperedge ID to the node that preceeded
                    it in this traversal.
              dict -- mapping from each node to an integer representing the
                    cardinality of the path from the source node to that node.

    """
    return _x_visit(hypergraph, source_node, False)


def is_f_connected(hypergraph, source_node, target_node):
    """Checks if a target node is F-connected to a source node.
    A node t is F-connected to a node s iff s if B-connected to t.
    Refer to 'B-connected's documentation for more details.

    :param hypergraph: the hypergraph to check F-connectedness on.
    :param source_node: the node to check F-connectedness to.
    :param target_node: the node to check F-connectedness of.
    :returns: bool -- whether target_node can be visited from source_node.

    """
    f_visited_nodes, Pv, Pe, v = f_visit(hypergraph, source_node)
    return target_node in f_visited_nodes


def sum_function(tail_nodes, W):
    """Additive sum function for nodes in the tail of a hyperedge.

    :param tail_nodes: nodes in the tail of a hyperedge that, in conjunction
                    with the weight of the hyperedge, will additively
                    constitute the weight of the head node
    :param W: node weighting function.
    :returns: int -- sum of the weights of tail_nodes.

    """
    return sum(W[node] for node in tail_nodes)


def distance_function(tail_nodes, W):
    """Additive distance function for nodes in the tail of a hyperedge.

    :param tail_nodes: nodes in the tail of a hyperedge that, in conjunction
                    with the weight of the hyperedge, will additively
                    constitute the weight of the head node.
    :param W: node weighting function.
    :returns: int -- max of the weights of tail_nodes.

    """
    return max(W[node] for node in tail_nodes)


def shortest_b_tree(hypergraph, source_node,
                    F=sum_function, valid_ordering=False):
    """Finds a set of minimum weight B-paths from a source node to all
    the nodes y which are B-connected to it, as described in the paper:
    Giorgio Gallo, Giustino Longo, Stefano Pallottino, Sang Nguyen,
    Directed hypergraphs and applications, Discrete Applied Mathematics,
    Volume 42, Issues 2-3, 27 April 1993, Pages 177-201, ISSN 0166-218X,
    http://dx.doi.org/10.1016/0166-218X(93)90045-P.
    (http://www.sciencedirect.com/science/article/pii/0166218X9390045P)

    :param hypergraph: the hypergraph to perform the 'SBT' algorithm on.
    :param source_node: the root of the tree to be found.
    :param F: function pointer to any additive weight function; that is,
            any function that is only a function of the weights of the
            nodes in the tail of a hyperedge.
    :param valid_ordering: a boolean flag to signal whether or not a valid
                        ordering of the nodes should be returned.
    :returns:   dict -- mapping from each node to the ID of the hyperedge that
                     preceeded it in this traversal.
                dict -- mapping from each node to the node's weight.
                list -- [only if valid_ordering argument is passed] a valid
                        ordering of the nodes.

    """
    # TODO: implement generalization for Shortest-F-Tree?
    # Not sure if that's a thing.
    forward_star = hypergraph.get_forward_star
    hyperedge_tail = hypergraph.get_hyperedge_tail
    hyperedge_head = hypergraph.get_hyperedge_head
    hyperedge_weight = hypergraph.get_hyperedge_weight

    node_set = hypergraph.get_node_set()
    # Pv keeps track of the ID of the hyperedge that directely
    # preceeded each node in the traversal
    Pv = {node: None for node in node_set}

    hyperedge_ids = hypergraph.get_hyperedge_id_set()
    # W keeps track of the smallest weight path from the source node
    # to each node
    W = {node: float("inf") for node in node_set}
    W[source_node] = 0

    # k keeps track of how many nodes in the tail of each hyperedge are
    # B-connected (when all nodes in a tail are B-connected, that hyperedge
    # can then be traversed)
    k = {hyperedge_id: 0 for hyperedge_id in hyperedge_ids}

    # List of nodes removed from the priority queue in the order that
    # they were removed
    ordering = []

    Q = PriorityQueue()
    Q.put((W[source_node], source_node))
    # Since PriorityQueue doesn't support "contains" operations we,
    # need another structure to keep track of what is currently in
    # the priority queue Q
    inQ = {source_node: W[source_node]}

    while not Q.empty():
        # At current_node, we can traverse each hyperedge in its forward star
        current_node_weight, current_node = Q.get()
        del inQ[current_node]
        # If node was at an earlier position in the valid ordering,
        # move it to the end of the ordering
        if ordering.count(current_node) != 0:
            ordering.remove(current_node)
        ordering.append(current_node)
        for hyperedge_id in forward_star(current_node):
            # Since we're arrived at a new node, we increment
            # k[hyperedge_id] to indicate that we've reached 1 new
            # node in this hyperedge's tail
            k[hyperedge_id] += 1
            # Traverse this hyperedge only when we have reached all the nodes
            # in its tail (i.e., when k[hyperedge_id] == |T(hyperedge_id)|)
            if k[hyperedge_id] == len(hyperedge_tail(hyperedge_id)):
                f = F(hyperedge_tail(hyperedge_id), W)
                # For each node in the head of the newly-traversed hyperedge,
                # if the previous weight of the node is more than the new
                # weight...
                for head_node in \
                    [node for node in hyperedge_head(hyperedge_id) if
                     W[node] > hyperedge_weight(hyperedge_id) + f]:
                    # If it's not already in the priority queue...
                    if head_node not in inQ:
                        # Add it to the priority queue
                        Q.put((W[head_node], head_node))
                        inQ[head_node] = W[head_node]
                        # If it has been visited before...
                        if W[head_node] < float("inf"):
                            # "Unmark" that node from the outgoing
                            # hyperedges of that node (signal that
                            # are not yet traversable)
                            for head_hyperedge_id in forward_star(head_node):
                                k[head_hyperedge_id] -= 1
                    # Update its weight to the new, smaller weight
                    W[head_node] = hyperedge_weight(hyperedge_id) + f
                    Pv[head_node] = hyperedge_id

    if valid_ordering:
        return Pv, W, ordering
    else:
        return Pv, W
