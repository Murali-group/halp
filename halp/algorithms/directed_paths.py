"""
.. module:: directed_paths
   :synopsis: Defines several functions for executing various
            path/connectivity queries on a directed hypergraph.

"""
try:
    from queue import Queue
except ImportError:
    from Queue import Queue

from halp.directed_hypergraph import DirectedHypergraph
from halp.utilities.priority_queue import PriorityQueue

# TODO-A: consider including target_node (with default value as None) in visit
# and b-visit to allow for early stoppage in an is_connected check and in an
# is_b_connected check
# TODO-B: consider maybe also caching the results from one execution of
# is_connected and is_b_connected to be able to check many node's for
# connectivity in only a single call of either visit or b_visit


def visit(H, source_node):
    """Executes the 'Visit' algorithm described in the paper:
    Giorgio Gallo, Giustino Longo, Stefano Pallottino, Sang Nguyen,
    Directed hypergraphs and applications, Discrete Applied Mathematics,
    Volume 42, Issues 2-3, 27 April 1993, Pages 177-201, ISSN 0166-218X,
    http://dx.doi.org/10.1016/0166-218X(93)90045-P.
    (http://www.sciencedirect.com/science/article/pii/0166218X9390045P)

    The Visit algorithm begins from a source node and traverses a hyperedge
    after any node in the hyperedge's tail has been reached.

    :param H: the hypergraph to perform the 'Visit' algorithm on.
    :param source_node: the initial node to begin traversal from.
    :returns: set -- nodes that were visited in this traversal.
              dict -- mapping from each node to the ID of the hyperedge that
              preceeded it in this traversal; will map a node to None
              if that node wasn't visited or if that node is the source
              node.
              dict -- mapping from each hyperedge ID to the node that preceeded
              it in this traversal.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    if not isinstance(H, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    node_set = H.get_node_set()
    # Pv keeps track of the ID of the hyperedge that directely
    # preceeded each node in the traversal
    Pv = {node: None for node in node_set}

    hyperedge_id_set = H.get_hyperedge_id_set()
    # Pe keeps track of the node that directedly preceeded
    # each hyperedge in the traversal
    Pe = {hyperedge_id: None for hyperedge_id in hyperedge_id_set}

    # Explicitly tracks the set of visited nodes
    visited_nodes = set([source_node])

    Q = Queue()
    Q.put(source_node)

    while not Q.empty():
        current_node = Q.get()
        # At current_node, we can traverse each hyperedge in its forward star
        for hyperedge_id in H.get_forward_star(current_node):
            if Pe[hyperedge_id] is not None:
                continue
            Pe[hyperedge_id] = current_node
            # Traversing a hyperedge in current_node's forward star yields
            # the set of head nodes of the hyperedge; visit each head node
            for head_node in H.get_hyperedge_head(hyperedge_id):
                if head_node in visited_nodes:
                    continue
                Pv[head_node] = hyperedge_id
                Q.put(head_node)
                visited_nodes.add(head_node)

    return visited_nodes, Pv, Pe


def is_connected(H, source_node, target_node):
    """Checks if a target node is connected to a source node. That is,
    this method determines if a target node can be visited from the source
    node in the sense of the 'Visit' algorithm.

    Refer to 'visit's documentation for more details.

    :param H: the hypergraph to check connectedness on.
    :param source_node: the node to check connectedness to.
    :param target_node: the node to check connectedness of.
    :returns: bool -- whether target_node can be visited from source_node.

    """
    visited_nodes, Pv, Pe = visit(H, source_node)
    return target_node in visited_nodes


def _x_visit(H, source_node, b_visit):
    """General form of the B-Visit algorithm, extended to also perform
    an implicit F-Visit if the b_visit flag is not set (providing better
    time/memory performance than explcitily taking the hypergraph's
    symmetric image and then performing the B-Visit on that).

    Refer to 'b_visit's or 'f_visit's documentation for more details.

    :param H: the hypergraph to perform the 'B-Visit' algorithm on.
    :param source_node: the initial node to begin traversal from.
    :param b_visit: boolean flag representing whether a B-Visit should
                    be performed (vs an F-Visit).
    :returns: set -- nodes that were x-visited in this traversal.
              dict -- mapping from each node visited to the ID of the hyperedge
                    that preceeded it in this traversal.
              dict -- mapping from each hyperedge ID to the node that preceeded
                    it in this traversal.
              dict -- mapping from each node to an integer representing the
                    cardinality of the path from the source node to that node.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    if not isinstance(H, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    # If the b_visit flag is set, perform a traditional B-Visit
    if b_visit:
        forward_star = H.get_forward_star
        hyperedge_tail = H.get_hyperedge_tail
        hyperedge_head = H.get_hyperedge_head
    # If the b_visit flag is not set, implicitly perform an F-Visit by
    # implicitly taking the symmetric image (what the 'else' statement
    # is for) and then performing a traditional B-Visit
    else:
        forward_star = H.get_backward_star
        hyperedge_tail = H.get_hyperedge_head
        hyperedge_head = H.get_hyperedge_tail

    node_set = H.get_node_set()
    # Pv keeps track of the ID of the hyperedge that directely
    # preceeded each node in the traversal
    Pv = {node: None for node in node_set}

    # v keeps track of the cardinality of the path from the source node to
    # any other B-connected node ('inf' cardinality for non-B-connected nodes)
    v = {node: float("inf") for node in node_set}
    v[source_node] = 0

    hyperedge_id_set = H.get_hyperedge_id_set()
    # Pe keeps track of the node that directedly preceeded
    # each hyperedge in the traversal
    Pe = {hyperedge_id: None for hyperedge_id in hyperedge_id_set}

    # k keeps track of how many nodes in the tail of each hyperedge are
    # B-connected (when all nodes in a tail are B-connected, that hyperedge
    # can then be traversed)
    k = {hyperedge_id: 0 for hyperedge_id in hyperedge_id_set}

    # Explicitly tracks the set of B-visited nodes
    x_visited_nodes = set([source_node])

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


def b_visit(H, source_node):
    """Executes the 'B-Visit' algorithm described in the paper:
    Giorgio Gallo, Giustino Longo, Stefano Pallottino, Sang Nguyen,
    Directed hypergraphs and applications, Discrete Applied Mathematics,
    Volume 42, Issues 2-3, 27 April 1993, Pages 177-201, ISSN 0166-218X,
    http://dx.doi.org/10.1016/0166-218X(93)90045-P.
    (http://www.sciencedirect.com/science/article/pii/0166218X9390045P)

    The B-Visit algorithm begins from a source node and traverses a hyperedge
    after all nodes in the hyperedge's tail have been reached.

    :param H: the hypergraph to perform the 'B-Visit' algorithm on.
    :param source_node: the initial node to begin traversal from.
    :returns: set -- nodes that were B-visited in this traversal.
              dict -- mapping from each node visited to the ID of the hyperedge
              that preceeded it in this traversal.
              dict -- mapping from each hyperedge ID to the node that preceeded
              it in this traversal.
              dict -- mapping from each node to an integer representing the
              cardinality of the path from the source node to that node.

    """
    return _x_visit(H, source_node, True)


def is_b_connected(H, source_node, target_node):
    """Checks if a target node is B-connected to a source node.

    A node t is B-connected to a node s iff:
        - t is s, or
        - there exists an edge in the backward star of t such that all nodes in
            the tail of that edge are B-connected to s

    In other words, this method determines if a target node can be B-visited
    from the source node in the sense of the 'B-Visit' algorithm. Refer to
    'b_visit's documentation for more details.

    :param H: the hypergraph to check B-connectedness on.
    :param source_node: the node to check B-connectedness to.
    :param target_node: the node to check B-connectedness of.
    :returns: bool -- whether target_node can be visited from source_node.

    """
    b_visited_nodes, Pv, Pe, v = b_visit(H, source_node)
    return target_node in b_visited_nodes


def f_visit(H, source_node):
    """Executes the 'F-Visit' algorithm alluded to in the paper:
    Giorgio Gallo, Giustino Longo, Stefano Pallottino, Sang Nguyen,
    Directed hypergraphs and applications, Discrete Applied Mathematics,
    Volume 42, Issues 2-3, 27 April 1993, Pages 177-201, ISSN 0166-218X,
    http://dx.doi.org/10.1016/0166-218X(93)90045-P.
    (http://www.sciencedirect.com/science/article/pii/0166218X9390045P)

    The F-Visit algorithm performs a B-Visit on the hypergraph's symmetric
    image, beginning at the source node. Refer to 'b_visit's documentation
    for more details.

    :param H: the hypergraph to perform the 'F-Visit' algorithm on.
    :param source_node: the initial node to begin traversal from.
    :returns: set -- nodes that were F-visited in this traversal.
              dict -- mapping from each node to the ID of the hyperedge that
              preceeded it in this traversal.
              dict -- mapping from each hyperedge ID to the node that preceeded
              it in this traversal.
              dict -- mapping from each node to an integer representing the
              cardinality of the path from the source node to that node.

    """
    return _x_visit(H, source_node, False)


def is_f_connected(H, source_node, target_node):
    """Checks if a target node is F-connected to a source node.

    A node t is F-connected to a node s iff s if B-connected to t.
    Refer to 'f_visit's or 'is_b_connected's documentation for more details.

    :param H: the hypergraph to check F-connectedness on.
    :param source_node: the node to check F-connectedness to.
    :param target_node: the node to check F-connectedness of.
    :returns: bool -- whether target_node can be visited from source_node.

    """
    f_visited_nodes, Pv, Pe, v = f_visit(H, source_node)
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
    """Additive distance (max) function for nodes in the tail of a hyperedge.
    Also commonly referred to as the 'rank' function.

    :param tail_nodes: nodes in the tail of a hyperedge that, in conjunction
                    with the weight of the hyperedge, will additively
                    constitute the weight of the head node.
    :param W: node weighting function.
    :returns: int -- max of the weights of tail_nodes.

    """
    return max(W[node] for node in tail_nodes)


def gap_function(tail_nodes, W):
    """Additive min function for nodes in the tail of a hyperedge.

    :param tail_nodes: nodes in the tail of a hyperedge that, in conjunction
                    with the weight of the hyperedge, will additively
                    constitute the weight of the head node
    :param W: node weighting function
    :returns: int -- max of the weights of tail_nodes

    """
    return min(W[node] for node in tail_nodes)


def _shortest_x_tree(H, source_node, b_tree,
                     F=sum_function, valid_ordering=False):
    """General form of the Shorest B-Tree algorithm, extended to also
    perform the implicit Shortest F-Tree procedure if the b_tree flag is
    not set (providing better time/memory performance than explcitily taking
    the hypergraph's symmetric image and then performing the SBT procedure
    on that).
    Uses priority queue to achieve O(size(H)*lg(n)) runtime.

    Refer to 'shorest_b_tree's or 'shorest_f_tree's documentation for
    more details.

    :param H: the H to perform the 'SXT' algorithm on.
    :param source_node: the root of the tree to be found.
    :param b_tree: boolean flag representing whether the Shortest B-Tree
                algorithm should be executed (vs the Shortest F-Tree).
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
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    if not isinstance(H, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    if b_tree:
        forward_star = H.get_forward_star
        hyperedge_tail = H.get_hyperedge_tail
        hyperedge_head = H.get_hyperedge_head
    else:
        forward_star = H.get_backward_star
        hyperedge_tail = H.get_hyperedge_head
        hyperedge_head = H.get_hyperedge_tail
    hyperedge_weight = H.get_hyperedge_weight

    node_set = H.get_node_set()
    # Pv keeps track of the ID of the hyperedge that directely
    # preceeded each node in the traversal
    Pv = {node: None for node in node_set}

    hyperedge_ids = H.get_hyperedge_id_set()
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
    Q.add_element(W[source_node], source_node)

    while not Q.is_empty():
        # At current_node, we can traverse each hyperedge in its forward star
        current_node = Q.get_top_priority()
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
                    # Update its weight to the new, smaller weight
                    W[head_node] = hyperedge_weight(hyperedge_id) + f
                    Pv[head_node] = hyperedge_id
                    # If it's not already in the priority queue...
                    if not Q.contains_element(head_node):
                        # Add it to the priority queue
                        Q.add_element(W[head_node], head_node)
                    else:
                        # Otherwise, decrease it's key in the priority queue
                        Q.reprioritize(W[head_node], head_node)

    if valid_ordering:
        return Pv, W, ordering
    else:
        return Pv, W


def shortest_b_tree(H, source_node,
                    F=sum_function, valid_ordering=False):
    """Executes the Shortest B-Tree (SBT) algorithm described in the paper:
    Giorgio Gallo, Giustino Longo, Stefano Pallottino, Sang Nguyen,
    Directed hypergraphs and applications, Discrete Applied Mathematics,
    Volume 42, Issues 2-3, 27 April 1993, Pages 177-201, ISSN 0166-218X,
    http://dx.doi.org/10.1016/0166-218X(93)90045-P.
    (http://www.sciencedirect.com/science/article/pii/0166218X9390045P)

    SBT finds a set of minimum weight B-paths from a source node to all
    the nodes y which are B-connected to it (when additive weight functions
    are used). Refer to 'is_b_connected's documentation for more details.

    :param H: the hypergraph to perform the 'SBT' algorithm on.
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
    return _shortest_x_tree(H, source_node, True, F, valid_ordering)


def shortest_f_tree(H, source_node,
                    F=sum_function, valid_ordering=False):
    """Executes the Shortest F-Tree algorithm, which is simply an execution
    of the Shorest B-Tree procedure from the source node on the hypergraph's
    symmetric image. Refer to 'shortest_b_tree's documentation for more
    details.

    :param hypergraph: the hypergraph to perform the 'SFT' algorithm on.
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
    return _shortest_x_tree(H, source_node, False, F, valid_ordering)


def get_hypertree_from_predecessors(H, Pv, source_node,
                                    node_weights=None, attr_name="weight"):
    """Gives the hypertree (i.e., the subhypergraph formed from the union of
    the set of paths from an execution of, e.g., the SBT algorithm) defined by
    Pv beginning at a source node. Returns a dictionary mapping each node to
    the ID of the hyperedge that preceeded it in the path (i.e., a Pv vector).
    Assigns the node weights (if provided) as attributes of the nodes (e.g.,
    the rank of that node in a specific instance of the SBT algorithm, or the
    cardinality of that node in a B-Visit traversal, etc.).

    :note: The IDs of the hyperedges in the subhypergraph returned may be
        different than those in the original hypergraph (even though the
        tail and head sets are identical).

    :param H: the hypergraph which the path algorithm was executed on.
    :param Pv: dictionary mapping each node to the ID of the hyperedge that
            preceeded it in the path.
    :param source_node: the root of the executed path algorithm.
    :param node_weights: [optional] dictionary mapping each node to some weight
                        measure.
    :param attr_name: key into the nodes' attribute dictionaries for their
                    weight values (if node_weights is provided).
    :returns: DirectedHypergraph -- subhypergraph induced by the path
            algorithm specified by the predecessor vector (Pv) from a
            source node.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    if not isinstance(H, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    sub_H = DirectedHypergraph()

    # If node weights are not provided, simply collect all the nodes that are
    # will be in the hypertree
    if node_weights is None:
        nodes = [node for node in Pv.keys() if Pv[node] is not None]
        nodes.append(source_node)
    # If node weights are provided, collect all the nodes that will be in the
    # tree and pair them with their corresponding weights
    else:
        nodes = [(node, {attr_name: node_weights[node]})
                 for node in Pv.keys() if Pv[node] is not None]
        nodes.append((source_node, {attr_name: node_weights[source_node]}))
    # Add the collected elements to the hypergraph
    sub_H.add_nodes(nodes)

    # Add all hyperedges, specified by Pv, to the hypergraph
    hyperedges = [(H.get_hyperedge_tail(hyperedge_id),
                   H.get_hyperedge_head(hyperedge_id),
                   H.get_hyperedge_attributes(hyperedge_id))
                  for hyperedge_id in Pv.values() if hyperedge_id is not None]
    sub_H.add_hyperedges(hyperedges)

    return sub_H


def get_hyperpath_from_predecessors(H, Pv, source_node, destination_node,
                                    node_weights=None, attr_name="weight"):
    """Gives the hyperpath (DirectedHypergraph) representing the shortest
    B-hyperpath from the source to the destination, given a predecessor
    function and source and destination nodes.

    :note: The IDs of the hyperedges in the subhypergraph returned may be
        different than those in the original hypergraph (even though the
        tail and head sets are identical).

    :param H: the hypergraph which the path algorithm was executed on.
    :param Pv: dictionary mapping each node to the ID of the hyperedge that
            preceeded it in the path.
    :param source_node: the source node of the path.
    :param destination_node: the destination node of the path.
    :returns: DirectedHypergraph -- shortest B-hyperpath from source_node to
            destination_node.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs
    :raises: KeyError -- Node key in predecessor is not in H
    :raises: KeyError -- Hyperedge key in predecessor is not in H
    :raises: ValueError -- Multiple nodes without predecessor
    :raises: ValueError -- Hypertree does not have source node

    """
    if not isinstance(H, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    # Check that Pv is a valid predecessor function:
    # - keys must be nodes in H mapping to hyperedges in H
    # - exactly one node must map to None (i.e., only one node
    #   without predecessor)
    nodes_without_predecessor = 0
    for node, hyperedge_id in Pv.items():
        if not H.has_node(node):
            raise KeyError(
                "Node key %s in predecessor is not in H" % node)

        if hyperedge_id is None:
            nodes_without_predecessor += 1
        elif not H.has_hyperedge_id(hyperedge_id):
            raise KeyError(
                "Hyperedge key %s in predecessor is not in H" % hyperedge_id)

    if nodes_without_predecessor > 1:
        raise ValueError(
            "Multiple nodes without predecessor. %s received" % Pv)
    elif nodes_without_predecessor == 0:
        raise ValueError(
            "Hypertree does not have source node. %s received" % Pv)

    path = DirectedHypergraph()

    # keep track of which nodes are or have been processed
    processedOrInQueue = {n: False for n in Pv}
    nodesToProcess = [destination_node]
    processedOrInQueue[destination_node] = True
    while nodesToProcess:
        node = nodesToProcess.pop(0)
        hyperedge_id = Pv[node]
        if hyperedge_id:
            for n in H.get_hyperedge_tail(hyperedge_id):
                if not processedOrInQueue[n]:
                    nodesToProcess.append(n)
                    processedOrInQueue[n] = True
            path.add_hyperedge(H.get_hyperedge_tail(hyperedge_id),
                               H.get_hyperedge_head(hyperedge_id),
                               weight=H.get_hyperedge_weight(
                               hyperedge_id))
        elif not path.has_node(node):
            path.add_node(node)

    return path
