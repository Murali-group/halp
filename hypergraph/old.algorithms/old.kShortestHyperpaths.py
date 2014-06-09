__version__ = '0.1.0'
__author__ = 'Jose Cadena'
__email__ = 'jcadena@vbi.vt.edu'

from copy import deepcopy

from hypergraph.directedHyperGraph import DirectedBHyperGraph
from hypergraph.directedHyperGraph import DirectedHyperGraph
from hypergraph.node import Node
from hypergraph.hyperedge import Hyperedge


class InvalidArgumentError(Exception):
    pass


class OutOfRangeError(Exception):
    pass


# To be replaced by someone else's implementation
def FS(G, n):
    return [e for e in G.hyperedges if n in e.tail]


def BS(G, n):
    return [e for e in G.hyperedges if n in e.head]


def sum_function(e, W):
    return sum(W[v] for v in e.tail)


def dummy_SBT(G, s, F=sum_function, valid_ordering=False):
    nodes = G.nodes
    hyperedges = G.hyperedges

    W = {i: float('inf') for i in nodes}
    P = {i: None for i in nodes}
    k = {e: 0 for e in hyperedges}
    ordering = []

    Q = [s]
    W[s] = 0

    while Q:
        i = Q.index(min(Q, key=lambda node: W[node]))
        u = Q.pop(i)
        ordering.append(u)
        for e in FS(G, u):
            k[e] += 1
            if k[e] == len(e.tail):
                f = F(e, W)
                for y in [n for n in e.head if W[n] > e.weight + f]:
                    if y not in Q:
                        Q.append(y)
                        if W[y] < 100000:
                            for eh in FS(G, y):
                                k[eh] -= 1
                    W[y] = e.weight + f
                    P[y] = e

    if valid_ordering:
        return P, W, ordering
    else:
        return P, W


def get_hyperpath_from_hypertree(T, s, t):
    '''
        Given a predecessor function,
        get the shortest B-hyperpath from s and t
    '''
    # check that T is a valid predecessor function:
    # It must be a map from Nodes to Hyperedges
    # with exactly one Node mapping to None
    if type(T) != dict:
        raise InvalidArgumentError(
            "T must be a map from nodes to hyperedges. %s received" % T)
    noneCounter = 0
    for node, hyperedge in T.items():
        if (not isinstance(node, Node) or
                not (isinstance(hyperedge, Hyperedge) or hyperedge is None)):
            raise InvalidArgumentError(
                "T must be a map from nodes to hyperedges. %s received" % T)
        if hyperedge is None:
            noneCounter += 1
    if noneCounter > 1:
        raise InvalidArgumentError(
            "Multiple nodes without predecessor. %s received" % T)
    elif noneCounter == 0:
        raise InvalidArgumentError(
            "Hypertree does not have root node. %s received" % T)

    G = DirectedBHyperGraph(set(), set())

    # keep track of which nodes are or have been processed
    processedOrInQueue = {n: False for n in T}
    nodesToProcess = [t]
    processedOrInQueue[t] = True
    while nodesToProcess:
        node = nodesToProcess.pop(0)
        hyperedge = T[node]
        if hyperedge:
            for n in hyperedge.tail:
                if not processedOrInQueue[n]:
                    nodesToProcess.append(n)
                    processedOrInQueue[n] = True
            G.add_hyperedgeByNames(set([v.name for v in hyperedge.head]),
                                   set([v.name for v in hyperedge.tail]),
                                   hyperedge.weight)
        elif not G.get_node_by_name(node.name):
            G.add_node(Node(node.name))
    return G


def branching_step(G, predecessor, ordering):
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
        branch = DirectedHyperGraph(set(G.nodes), set(G.hyperedges))
        for j in range(i + 2, len(ordering)):
            node = ordering[j]
            backstar = BS(branch, node)
            for edge in backstar:
                if edge != predecessor[node]:
                    branch.remove_hyperedge(edge)
        branch.remove_hyperedge(predecessor[ordering[i + 1]])
        branches.append(branch)
    return branches


def compute_lower_bound(G_i, i, predecessor, ordering,
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
    backstar = BS(G_i, ordering[i + 1])
    # There is no s-t path left in this branch
    # return infinity
    if not backstar:
        return float('inf')
    W_bar[ordering[i + 1]] = min([F(e, W) + e.weight for e in backstar])

    for j in range(i + 2, len(ordering)):
        p_j = predecessor[ordering[j]]
        W_bar[ordering[j]] = F(p_j, W_bar) + p_j.weight

    return W_bar[t]


def k_shortest_hyperpaths(G, s, t, k, F=sum_function):
    '''
        Computes the k shortest hyperpaths from a given
        node to every other node in the graph.
        Output is a list of hypertrees in ascending order of path length.
        This method only works for directed B-hypergraphs.
    '''
    if G.__class__ != DirectedBHyperGraph:
        raise InvalidArgumentError(
            "G must be a directed B-Hypergraph. Cast if appropriate.")
    if s not in G.nodes:
        raise InvalidArgumentError("s must be a node in G. %s received" % s)
    if t not in G.nodes:
        raise InvalidArgumentError("t must be a node in G. %s received" % t)
    if type(k) != int:
        raise InvalidArgumentError("k must be an integer. %s received" % k)
    if k <= 0:
        raise OutOfRangeError("k must be a positive integer. %s received" % k)

    # container for the k-shortest hyperpaths
    paths = []
    # container for the candidate paths. Every item is a 4-tuple:
    # 1) subgraph G'
    # 2) lower bound on shortest hyperpath weight
    # 3) predecessor function of shortest hypertree rootes at s on G'
    # 4) valid ordering of the nodes in G'

    candidates = []

    shortestHypertree, W, ordering = dummy_SBT(G, s,
                                               valid_ordering=True)
    # check if there is s-t hyperpath
    # if there isn't the for loop below
    # will break immediately and the function returns an empty list
    if W[t] != float('inf'):
        candidates.append((G, W, shortestHypertree, ordering))
    i = 1
    while i <= k:
        if not candidates:
            break
        ind = candidates.index(min(candidates, key=lambda x: x[1][t]))
        kShortest = candidates[ind]
        if kShortest[2]:
            candidates.pop(ind)
            path = get_hyperpath_from_hypertree(kShortest[2], s, t)
            pathPredecessor = {node: edge
                               for node, edge in kShortest[2].items()
                               if node.name in path.get_node_names()}
            pathOrdering = [node for node in kShortest[3]
                            if node in pathPredecessor]
            paths.append(path)
            # check if we are done
            if len(paths) == k:
                break

            branches = branching_step(kShortest[0], pathPredecessor,
                                      pathOrdering)
            for j, branch in enumerate(branches):
                lb = compute_lower_bound(branch, j, kShortest[2],
                                         pathOrdering, kShortest[1], t, F)
                if lb < float('inf'):
                    candidates.append((branch, {t: lb}, None, None))
            i += 1
        else:
            # compute shortest hypertree for kShortest[0] and exact bound
            # reinsert into candidates
            G_sub = kShortest[0]
            tree_sub, W_sub, ordering_sub = dummy_SBT(G_sub, s,
                                                      valid_ordering=True)
            candidates[ind] = (G_sub, W_sub, tree_sub, ordering_sub)
    return paths
