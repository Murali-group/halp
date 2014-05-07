__version__ = '0.1.0'
__author__ = 'Jose Cadena'
__email__ = 'jcadena@vbi.vt.edu'

from copy import deepcopy

from hypergraph.directedHyperGraph import DirectedBHyperGraph
from hypergraph.directedHyperGraph import DirectedHyperGraph
from hypergraph.node import Node
from hypergraph.hyperedge import HyperEdge


class InvalidArgumentError(Exception):
    pass


class OutOfRangeError(Exception):
    pass


# To be replaced by someone else's implementation
def FS(G, n):
    return [e for e in G.hyperedges if n in e.tail]


def sum_function(e, W):
    return sum(W[v] for v in e.tail)


def dummy_SBT(G, s, F=sum_function, valid_ordering=False):
    nodes = G.nodes
    hyperedges = G.hyperedges

    W = {i: 100000 for i in nodes}
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
                c = [n for n in e.head if W[n] > e.weight + f]
                for y in [n for n in e.head if W[n] > e.weight + f]:
                    if y not in Q:
                        Q.append(y)
                        if W[y] < 100000:
                            for eh in FS(G, y):
                                k[eh] -= 1
                        W[y] = e.weight + f
                        P[y] = e

    if valid_ordering:
        return P, ordering
    else:
        return P


def get_hyperpath_from_hypertree(T, s, t):
    '''
        Given a predecessor function,
        get the shortest B-hyperpath from s and t
    '''
    # check that T is a valid predecessor function:
    # It must be a map from Nodes to HyperEdges
    # with exactly one Node mapping to None
    if type(T) != dict:
        raise InvalidArgumentError(
            "T must be a map from nodes to hyperedges. %s received" % T)
    noneCounter = 0
    for node, hyperedge in T.items():
        if (not isinstance(node, Node) or
                not (isinstance(hyperedge, HyperEdge) or hyperedge is None)):
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

    G = DirectedHyperGraph(nodes=set(), hyperedges=set())

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


def get_hyperpath_weight_from_hypertree(T, s, t):
    '''
        Given a predecessor function,
        get weight of shortest B-hyperpath from s and t
    '''
    return


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
    # container for the candidate paths. Every item is a 3-tuple:
    # subgraph, lower bound on shortest hyperpath weight, shortest hypertree
    candidates = []

    shortestHypertree, ordering = dummy_SBT(G, s, valid_ordering=True)
    shortestHyperpath = None

    candidates.append((G, 0, shortestHypertree))
    for i in range(k):
        if not candidates:
            break
        ind = candidates.index(min(candidates, key=lambda x: x[1]))
        kShortest = candidates.pop(ind)
        if kShortest[2]:
            paths.append(get_hyperpath_from_hypertree(kShortest[2], s, t))
            # do branching step
        else:
            # compute shortest hypertree for kShortest[0] and lower bound
            # reinsert into candidates
            pass
    return paths
