"""
.. module k_shortest_hyperpaths
  :synopsis: Algorithm to compute the k-shortest hyperpaths in a B-hypergraph.

"""
__version__ = '0.1.0'
__author__ = 'Jose Cadena'
__email__ = 'jcadena@vbi.vt.edu'

from halp.directed_hypergraph import DirectedHypergraph
from halp.algorithms.directed_paths import sum_function, shortest_b_tree
from halp.algorithms.directed_paths import get_hyperpath_from_predecessors


def k_shortest_hyperpaths(H, source_node, destination_node, k, F=sum_function):
    """Computes the k shortest hyperpaths from a source node to every other
    node in the hypergraph.
    This algorithm is only applicable to directed B-hypergraphs.
    The algorithm is described in the paper:
    Lars Relund Nielsen, Kim Allan Andersen, Daniele Pretolani,
    Finding the K shortest hyperpaths, Computers & Operations Research,
    Volume 32, Issue 6, June 2005, Pages 1477-1497, ISSN 0305-0548,
    http://dx.doi.org/10.1016/j.cor.2003.11.014.
    (http://www.sciencedirect.com/science/article/pii/S0305054803003459)

    :param H: the hypergraph for which the function will compute the shortest
              hyperpaths.
    :param source_node: the source node in H for the path computation.
    :param destination_node: the destination node in H for the path
                        computation.
    :param k: a positive integer indicating how many paths to compute.
    :param F: [optional] function used for the shortest path computation.
              See algorithms.directed_paths module for expected format of
              function.
    :returns: a list containing at most k hyperpaths (DirectedHypergraph) from
              source to destination in ascending order of path length.
    :raises: TypeError -- Input hypergraph must be a B-hypergraph
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs
    :raises: ValueError -- source_node must be a node in H
    :raises: ValueError -- destination_node must be a node in H
    :raises: TypeError -- k must be an integer
    :raises: ValueError -- k must be a positive integer

    """
    try:
        if not H.is_B_hypergraph():
            raise TypeError("Input graph must be a B-hypergraph")
    except AttributeError:
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    if not H.has_node(source_node):
        raise ValueError("source_node must be a node in H. \
                         %s received" % source_node)

    if not H.has_node(destination_node):
        raise ValueError("destination_node must be a node in H. \
                         %s received" % destination_node)

    if type(k) != int:
        raise TypeError("k must be an integer. %s received" % k)

    if k <= 0:
        raise ValueError("k must be a positive integer. %s received" % k)

    # Container for the k-shortest hyperpaths
    paths = []

    # Container for the candidate paths. Every item is a 4-tuple:
    # 1) subgraph H'
    # 2) lower bound on shortest hyperpath weight
    # 3) predecessor function of shortest hypertree rootes at s on H'
    # 4) valid ordering of the nodes in H'
    candidates = []

    shortest_hypertree, W, ordering = \
        shortest_b_tree(H, source_node, F=F, valid_ordering=True)
    # Check if there is source-destination hyperpath
    # if there isn't the for loop below
    # will break immediately and the function returns an empty list
    if W[destination_node] != float('inf'):
        candidates.append((H, W, shortest_hypertree, ordering))

    i = 1
    while i <= k and candidates:
        ind = candidates.index(
            min(candidates, key=lambda x: x[1][destination_node]))
        kShortest = candidates[ind]
        if kShortest[2]:
            candidates.pop(ind)
            path = \
                get_hyperpath_from_predecessors(kShortest[0], kShortest[2],
                                                source_node, destination_node)
            pathPredecessor = \
                {node: edge for node, edge in kShortest[2].items()
                 if node in path.get_node_set()}
            pathOrdering = \
                [node for node in kShortest[3] if node in pathPredecessor]
            paths.append(path)

            # check if we are done
            if len(paths) == k:
                break

            branches = _branching_step(kShortest[0], pathPredecessor,
                                       pathOrdering)
            for j, branch in enumerate(branches):
                lb = _compute_lower_bound(branch, j, kShortest[2],
                                          pathOrdering, kShortest[1],
                                          destination_node, F)
                if lb < float('inf'):
                    candidates.append((branch,
                                      {destination_node: lb},
                                      None, None))
            i += 1
        else:
            # Compute shortest hypertree for kShortest[0] and exact bound
            # reinsert into candidates
            H_sub = kShortest[0]
            tree_sub, W_sub, ordering_sub = \
                shortest_b_tree(H_sub, source_node, valid_ordering=True)
            candidates[ind] = (H_sub, W_sub, tree_sub, ordering_sub)

    return paths


def _branching_step(H, predecessor, ordering):
    """Performs the branching step of the k-shortest hyperpaths
    algorithm.

    :param H: the hypergraph on which to do the branching step.
    :param predecessor: predecessor function of s-t hyperpath in H.
    :param ordering: a valid ordering of the nodes in the s-t hyperpath.
    :returns: list -- list of q-1 hypergraphs, where q is the size
            of the ordering in the subproblem.

    """
    branches = []
    for i in range(len(ordering) - 1):
        branch = H.copy()
        for j in range(i + 2, len(ordering)):
            node = ordering[j]
            for hyperedge in branch.get_backward_star(node):
                if hyperedge != predecessor[node]:
                    branch.remove_hyperedge(hyperedge)
        branch.remove_hyperedge(predecessor[ordering[i + 1]])
        branches.append(branch)

    return branches


def _compute_lower_bound(H_i, i, predecessor, ordering,
                         W, t, F=sum_function):
    """Computes a lower bound on the weight of the
    shortest s-t hyperpath as described in Section 3.2 of
    Nielsen et al.

    :param H_i: the branch of the subproblem for which we'll compute the bound.
    :param i: the [zero-based] index of the branch relative to the ordering.
    :param predecessor: predecessor function of the unbranched hypergraph.
    :param ordering: a valid ordering of the nodes in the shortest s-t
                hyperpath of the unbranched hypergraph.
    :param W: the weight vector of the shortest s-t hyperpath for which the
            k-shortest hyperpaths procedure was called.
    :param t: the destination node in the unbranched graph.
    :param F: [optional] a weight function.
    :returns: float -- a positive real number that is the lower bound of the
            weight of the shortest s-t hyperpath in H.

    """
    # Initialize the weight vector for the nodes in the branched graph
    W_bar = {node: weight for node, weight in W.items()}
    backstar = H_i.get_backward_star(ordering[i + 1])

    # There is no s-t path left in this branch
    # return infinity
    if not backstar:
        return float('inf')

    W_bar[ordering[i + 1]] = min([F(H_i.get_hyperedge_tail(e), W) +
                                  H_i.get_hyperedge_weight(e)
                                  for e in backstar])

    for j in range(i + 2, len(ordering)):
        p_j = predecessor[ordering[j]]
        W_bar[ordering[j]] = (F(H_i.get_hyperedge_tail(p_j), W_bar) +
                              H_i.get_hyperedge_weight(p_j))

    return W_bar[t]
