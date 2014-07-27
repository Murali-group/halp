"""
.. module k_shortest_hyperpaths
  :synopsis: Algorithm to compute the k-shortest hyperpaths in B hypergraphs
"""
__version__ = '0.1.0'
__author__ = 'Jose Cadena'
__email__ = 'jcadena@vbi.vt.edu'

from hypergraph.directed_hypergraph import DirectedHypergraph
from hypergraph.algorithms.directed_paths import sum_function, shortest_b_tree
from hypergraph.algorithms.directed_paths import \
    get_hyperpath_from_predecessors


def k_shortest_hyperpaths(H, source, destination, k, F=sum_function):
    '''
        Computes the k shortest hyperpaths from a source node to every other
        node in the hypergraph. This algorithm is only applicable to
        directed B-hypergraphs. The algorithm is described in the paper
        "Finding the K shortest hyperpaths" by Lars Nielsen, Kim Andersen, and
        Daniele Pretolani

    :param H: the hypergraph for which the function will compute the shortest
              hyperpaths
    :param source: a source node in H for the path computation
    :param destination: a destination node in H for the path computation
    :param k: positive integer indicating how many paths to compute
    :param F: [optional] function used for the shortest path computation.
              See algorithms.directed_paths module for expected format of
              function
    :returns: a list containing at most k hyperpaths (DirectedHypergraph) from
              source to destination in ascending order of path length.
    '''
    try:
        if not H.is_B_hypergraph():
            raise TypeError("Input graph must be a B-hypergraph")
    except AttributeError:
        raise TypeError("Input graph must be a B-hypergraph")
    if not H.has_node(source):
        raise ValueError("source must be a node in H. %s received" % source)
    if not H.has_node(destination):
        raise ValueError(
            "destination must be a node in H. %s received" % destination)
    if type(k) != int:
        raise TypeError("k must be an integer. %s received" % k)
    if k <= 0:
        raise ValueError("k must be a positive integer. %s received" % k)

    # container for the k-shortest hyperpaths
    paths = []
    # container for the candidate paths. Every item is a 4-tuple:
    # 1) subgraph G'
    # 2) lower bound on shortest hyperpath weight
    # 3) predecessor function of shortest hypertree rootes at s on G'
    # 4) valid ordering of the nodes in G'

    candidates = []

    shortestHypertree, W, ordering = shortest_b_tree(
        H, source, F=F, valid_ordering=True)
    # check if there is source-destination hyperpath
    # if there isn't the for loop below
    # will break immediately and the function returns an empty list
    if W[destination] != float('inf'):
        candidates.append((H, W, shortestHypertree, ordering))
    i = 1
    while i <= k:
        if not candidates:
            break
        ind = candidates.index(
            min(candidates, key=lambda x: x[1][destination]))
        kShortest = candidates[ind]
        if kShortest[2]:
            candidates.pop(ind)
            path = get_hyperpath_from_predecessors(kShortest[0], kShortest[2],
                                                   source, destination)
            pathPredecessor = {node: edge
                               for node, edge in kShortest[2].items()
                               if node in path.get_node_set()}
            pathOrdering = [node for node in kShortest[3]
                            if node in pathPredecessor]
            paths.append(path)
            # check if we are done
            if len(paths) == k:
                break

            branches = _branching_step(kShortest[0], pathPredecessor,
                                       pathOrdering)
            for j, branch in enumerate(branches):
                lb = _compute_lower_bound(branch, j, kShortest[2],
                                          pathOrdering, kShortest[1],
                                          destination, F)
                if lb < float('inf'):
                    candidates.append((branch, {destination: lb}, None, None))
            i += 1
        else:
            # compute shortest hypertree for kShortest[0] and exact bound
            # reinsert into candidates
            G_sub = kShortest[0]
            tree_sub, W_sub, ordering_sub = shortest_b_tree(
                G_sub, source,
                valid_ordering=True)
            candidates[ind] = (G_sub, W_sub, tree_sub, ordering_sub)
    return paths


def _branching_step(H, predecessor, ordering):
    '''
        Performs the branching step of the k-shortest hyperpaths
        algorithm
        Input:
        G: graph on which to do the branching step
        predecessor: predecessor function of s-t hyperpath in G
        ordering: a valid ordering of the nodes in the s-t
                  hyperpath
        Returns:
        a list of q-1 hypergraphs, where q is the size
        of the ordering in the subproblem
    '''
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
    '''
        Computes a lower bound on the weight of the
        shortest s-t hyperpath as described in Section 3.2 of
        Nielsen et al.\
        Input:
        G_i: branch of the subproblem for which we'll compute the bound
        i: zero-based index of the branch relative to the ordering
        predecessor: predecessor function of the unbranched hypergraph
        ordering: valid ordering of the nodes in the shortest s-t
                  hyperpath of the unbranched hypergraph
        W: the weight vector of the shortest s-t hyperpath for which
           the k-shortest hyperpaths procedure was called
        t: destination node in the unbranched graph
        F = additive weight function
        Returns:
        a positive real number, the lower bound of the weight of
        the shortest s-t hyperpath in G
    '''
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
