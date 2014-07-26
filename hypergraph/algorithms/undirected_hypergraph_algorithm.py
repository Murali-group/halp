"""
.. module:: mincut_algorithm
   :synopsis: Defines several functions for doing random walk,
   finding the stationary distribution, and finding the mincut
   for a hypergraph.
"""
import random
import numpy as np
from scipy import sparse
from scipy.sparse import linalg
from hypergraph.undirected_hypergraph import UndirectedHypergraph


def getIncidenceMatrix(hypergraph):
    """Creates the 'Incidence Matrix' as a sparse matrix using the
    approach that is explained in the paper:
    (http://pages.cs.wisc.edu/~shuchi/courses/787-F09/scribe-notes/lec15.pdf)

    This algorithm finds the H matrix as explained in the above paper

    :param hypergraph: the hypergraph to find the W matrix on it.
    :returns: sparse.csc_matrix -- The Incidence Matrix as a sparse matrix
    :raises: TypeError -- Algorithm only applicable to undirected hypergraphs
    """
    if not isinstance(hypergraph, UndirectedHypergraph):
        raise TypeError("Algorithm only applicable to undirected hypergraphs")
    nodeNumber = len(hypergraph.get_node_set())
    edgeNumber = len(hypergraph.get_hyperedge_id_set())
    rows = []
    cols = []
    nodeidList2nodeset, nodeset2nodeid = get_nodeset2nodeid(hypergraph)
    for hyperedge_id in hypergraph.hyperedge_id_iterator():
        for node in hypergraph.get_hyperedge_nodes(hyperedge_id):
            # get the mapping btw node and its id
            rows.append(nodeset2nodeid.get(node))
            # since it starts with e, like e31
            cols.append(int(hyperedge_id[1:])-1)
    values = np.ones(len(rows), dtype=int)
    return sparse.csc_matrix((values, (rows, cols)),
                             shape=(len(set(rows)),
                             len(set(cols))))


def getDiagonalWeightMatrix(hypergraph):
    """Creates the 'Diagonal Edge Weight Matrix' as a sparse matrix using the
    approach that is explained in the paper:
    (http://pages.cs.wisc.edu/~shuchi/courses/787-F09/scribe-notes/lec15.pdf)

    This algorithm finds the W matrix as explained in the above paper

    :param hypergraph: the hypergraph to find the W matrix on it.
    :returns: sparse.csc_matrix -- The Diagonal Edge Weight Matrix as a
    sparse matrix
    :raises: TypeError -- Algorithm only applicable to undirected hypergraphs
    """
    if not isinstance(hypergraph, UndirectedHypergraph):
        raise TypeError("Algorithm only applicable to undirected hypergraphs")
    edgeNumber = len(hypergraph.get_hyperedge_id_set())
    hyperedgeWeight = get_hyperedge_weight(hypergraph)
    edgeWeightVector = []
    for i in range(edgeNumber):
        edgeWeightVector.append(hyperedgeWeight.get(str(i)))
    return sparse.diags([edgeWeightVector], [0])


def getDiagonalNodeMatrix(hypergraph):
    """Creates the 'Diagonal Node Matrix' as a sparse matrix using the
    approach that is explained in the paper:
    (http://pages.cs.wisc.edu/~shuchi/courses/787-F09/scribe-notes/lec15.pdf)

    This algorithm finds the D_v matrix as explained in the above paper.
    It returns a diagonal matrix containing the node degrees which
    is basically the summation of the weights of each node's incident edges

    :param hypergraph: the hypergraph to find the D_v matrix on it.
    :returns: sparse.csc_matrix -- The Diagonal Node Matrix as a sparse matrix
    :raises: TypeError -- Algorithm only applicable to undirected hypergraphs
    """
    if not isinstance(hypergraph, UndirectedHypergraph):
        raise TypeError("Algorithm only applicable to undirected hypergraphs")
    incidenceMatrix = getIncidenceMatrix(hypergraph)
    W = getDiagonalWeightMatrix(hypergraph)
    return sparse.diags([incidenceMatrix * W.diagonal()], [0])


def getDiagonalEdgeMatrix(hypergraph):
    """Creates the 'Diagonal Edge Degree Matrix' as a sparse matrix using the
    approach that is explained in the paper:
    (http://pages.cs.wisc.edu/~shuchi/courses/787-F09/scribe-notes/lec15.pdf)

    This algorithm finds the D_e matrix as explained in the above paper

    :param hypergraph: the hypergraph to find the D_e matrix on it.
    :returns: sparse.csc_matrix -- The Diagonal Edge Degree Matrix
    as a sparse matrix
    :raises: TypeError -- Algorithm only applicable to undirected hypergraphs
    """
    if not isinstance(hypergraph, UndirectedHypergraph):
        raise TypeError("Algorithm only applicable to undirected hypergraphs")
    edgeNumber = len(hypergraph.get_hyperedge_id_set())
    incidenceMatrix = getIncidenceMatrix(hypergraph)
    degrees = incidenceMatrix.sum(0)
    new_degree = []
    degrees = degrees.transpose()
    for degree in degrees:
        new_degree.append(int(degree[0:]))

    return sparse.diags([new_degree], [0])


def fastInverse(M):
    """Finds the inverse of a DIAGONAL only matrix.

    This algorithm find the inverse of a diagonal matrix much faster
    than the built-in method in sparse class, i.e. sparse.linalg.inv() function

    :param hypergraph: the diagonal matrix to find the inverse of it
    :returns: sparse.csc_matrix -- The inverse of the input matrix
    as a sparse matrix
    """
    diags = M.diagonal()
    new_diag = []
    for value in diags:
        new_diag.append(1.0/value)
    return sparse.diags([new_diag], [0])


def randomWalkMatrix(hypergraph):
    """Finds the 'Random Walk Matrix' as described in the paper:
    Zhou, Dengyong, Jiayuan Huang, and Bernhard Scholkopf.
    "Learning with hypergraphs: Clustering, classification, and embedding."
    Advances in neural information processing systems. 2006.
    (http://machinelearning.wustl.edu/mlpapers/paper_files/NIPS2006_630.pdf)

    This algorithm uses the incidence matrix and finds the random walk
    matrix of the hypergraph

    :param hypergraph: the hypergraph to find the 'Random Walk Matrix' on it
    :returns: sparse.csc_matrix -- The Random Walk Matrix as a sparse matrix
    :raises: TypeError -- Algorithm only applicable to undirected hypergraphs
    """

    if not isinstance(hypergraph, UndirectedHypergraph):
        raise TypeError("Algorithm only applicable to undirected hypergraphs")
    H = getIncidenceMatrix(hypergraph)
    D_v = getDiagonalNodeMatrix(hypergraph)
    D_e = getDiagonalEdgeMatrix(hypergraph)
    W = getDiagonalWeightMatrix(hypergraph)
    D_v_inverse = fastInverse(D_v)
    D_e_inverse = fastInverse(D_e)
    H_transpose = H.transpose()
    P = D_v_inverse * H
    P = P * W
    P = P * D_e_inverse
    P = P * H_transpose
    return P


def stationaryDistribution(hypergraph, P=None):
    """Finds the 'Stationary Distribution' using the iterative approach that is
    explained in the paper:
    (http://pages.cs.wisc.edu/~shuchi/courses/787-F09/scribe-notes/lec15.pdf)

    This algorithm uses the random walk matrix of a hypergraph to find the
    stationary distribution of the hypergraph

    :param hypergraph: the hypergraph to find the 'Stationary Distribution'
                       algorithm on.
    :returns: list -- A list containing the probability for all nodes in the
                      hypergraph
    :raises: TypeError -- Algorithm only applicable to undirected hypergraphs
    """
    if not isinstance(hypergraph, UndirectedHypergraph):
        raise TypeError("Algorithm only applicable to undirected hypergraphs")
    if P is None:
        P = randomWalkMatrix(hypergraph)
    nodeNumber = len(hypergraph.get_node_set())
    pi = createRandomStarter(nodeNumber)
    pi_star = createRandomStarter(nodeNumber)
    while not converged(pi_star, pi):
        pi = pi_star
        pi_star = pi * P
    return pi


def normalizedLaplacian(hypergraph):
    """Finds the 'Normalized Laplacian Matrix' as described in the paper:
    Zhou, Dengyong, Jiayuan Huang, and Bernhard Scholkopf.
    "Learning with hypergraphs: Clustering, classification, and embedding."
    Advances in neural information processing systems. 2006.
    (http://machinelearning.wustl.edu/mlpapers/paper_files/NIPS2006_630.pdf)

    This algorithm uses the incidence matrix and finds the normalized
    Laplacian matrix

    :param hypergraph: the hypergraph to perform the 'Normalized Laplacian
    Matrix' algorithm on.
    :returns: sparse.csc_matrix -- The Normalized Laplacian Matrix as a sparse
                                   matrix
    :raises: TypeError -- Algorithm only applicable to undirected hypergraphs
    """

    if not isinstance(hypergraph, UndirectedHypergraph):
        raise TypeError("Algorithm only applicable to undirected hypergraphs")
    nodeNumber = len(hypergraph.get_node_set())
    H = getIncidenceMatrix(hypergraph)
    D_v = getDiagonalNodeMatrix(hypergraph)
    D_e = getDiagonalEdgeMatrix(hypergraph)
    W = getDiagonalWeightMatrix(hypergraph)
    D_v_sqrt = D_v.sqrt()
    D_v_sqrt_inverse = np.real(fastInverse(D_v_sqrt).todense())
    D_v_sqrt_inverse = sparse.csc_matrix(D_v_sqrt_inverse)
    D_e_inverse = fastInverse(D_e)
    H_transpose = H.transpose()
    Theta = D_v_sqrt_inverse * H
    Theta = Theta * W
    Theta = Theta * D_e_inverse
    Theta = Theta * H_transpose
    Theta = Theta * D_v_sqrt_inverse
    I = sparse.eye(nodeNumber)
    Delta = I - Theta
    return Delta


def minCut(hypergraph, threshold=0):
    """Executes the 'Mincut' algorithm described in the paper:
    Zhou, Dengyong, Jiayuan Huang, and Bernhard Scholkopf.
    "Learning with hypergraphs: Clustering, classification, and embedding."
    Advances in neural information processing systems. 2006.
    (http://machinelearning.wustl.edu/mlpapers/paper_files/NIPS2006_630.pdf)

    This algorithm uses the normalized Laplacian matrix to partition
    the graph to two disjoint components

    :param hypergraph: the hypergraph to perform the 'Mincut' algorithm on.
    :param threshold: The threshold value to do the partitioning algorithm.
                      Usually, the value zero is selected for this purpose.
    :returns: list -- the two entries contain all nodes that belong to the
                      two partitions
    :raises: TypeError -- Algorithm only applicable to undirected hypergraphs
    """

    if not isinstance(hypergraph, UndirectedHypergraph):
        raise TypeError("Algorithm only applicable to undirected hypergraphs")
    '''
    TODO: make sure that the hypergraph is connected
    '''
    Delta = normalizedLaplacian(hypergraph)
    eigenValues, eigenVectors = np.linalg.eig(Delta.todense())
    '''
        since the eigs method in sparse.linalg library doesn't find
        all the eigenvalues and eigenvectors, it doesn't give us an
        exact and correct solution. Therefore, we should use the
        numpy library which works on dense graphs. This might be
        problematic for large graphs.
    '''
    # eigenValues,eigenVectors = linalg.eigs(Delta,k=numberOfEigenValues)
    second_min_index = np.argsort(eigenValues)[1]
    secondEigenVector = eigenVectors[:, second_min_index]

    nodeid2nodeset, nodeset2nodeid = get_nodeset2nodeid(hypergraph)
    partitionIndex = [
        i for i in range(
            len(secondEigenVector)) if secondEigenVector[i] >= threshold]
    Partition = [list() for x in range(2)]
    for (key, value) in list(nodeset2nodeid.items()):
        if value in partitionIndex:
            Partition[0].append(key)
        else:
            Partition[1].append(key)
    return Partition


def get_nodeset2nodeid(hypergraph):
    """Finds the nodeset to nodeid mapping for all the nodes in the
    hypergraph
    :param hypergraph: the hypergraph to find all the mappings.
    :returns: dict -- The mapping from nodeid to nodename
              dict -- The mapping from nodename to nodeid
    """
    nodeSet = hypergraph.get_node_set()
    nodeset2nodeidList = {}
    nodeidList2nodeset = {}
    node_id = 0
    for node in nodeSet:
        nodeset2nodeidList.update({node: node_id})
        nodeidList2nodeset.update({node_id: node})
        node_id += 1
    return nodeidList2nodeset, nodeset2nodeidList


def get_hyperedge_weight(hypergraph):
    """Finds weight of each hyperedge
    :param hypergraph: the hypergraph to find the weights
    :returns: dict -- The mapping from edgeid to its weight
    """
    hyperedgeWeight = {}
    for hyperedge_id in hypergraph.hyperedge_id_iterator():
        hyperedgeWeight.update({str(int(hyperedge_id[1:])-1):
                               hypergraph.get_hyperedge_weight(hyperedge_id)})
    return hyperedgeWeight


def createRandomStarter(n):
    """Creates the random starter for the random walk algorithm
    :param n: number of nodes to create the random vector
    :returns: list -- containing the starting probability for each node
    """
    pi = np.zeros(n, dtype=float)
    for i in range(n):
        pi[i] = random.random()
    summation = np.sum(pi)
    for i in range(n):
        pi[i] = pi[i] / summation
    return pi


def converged(pi_star, pi):
    """Chech whether the random walk converged or not
    :param pi_star: the new vector
           pi: the old vector
    :returns: Boolean -- converged or not
    """
    nodeNumber = pi.shape[0]
    for i in range(nodeNumber):
        if pi[i]-pi_star[i] > 10e-6:
            return False
    return True
