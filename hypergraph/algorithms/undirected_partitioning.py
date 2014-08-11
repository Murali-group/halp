"""
.. module:: undirected_partitioning
   :synopsis: Defines several functions for doing random walk, finding
            the stationary distribution, and finding the min-cut for
            an undirected hypergraph.
"""
import random
import numpy as np
from scipy import sparse
from scipy.sparse import linalg

from hypergraph.undirected_hypergraph import UndirectedHypergraph
import hypergraph.utilities.undirected_graph_transformations as ugt


def normalized_hypergraph_cut(H, threshold=0):
    """Executes the min-cut algorithm described in the paper:
    Zhou, Dengyong, Jiayuan Huang, and Bernhard Scholkopf.
    "Learning with hypergraphs: Clustering, classification, and embedding."
    Advances in neural information processing systems. 2006.
    (http://machinelearning.wustl.edu/mlpapers/paper_files/NIPS2006_630.pdf)

    This algorithm uses the normalized Laplacian to partition the hypergraph
    into two disjoint components.

    :param H: the hypergraph to perform the 'min-cut' algorithm on.
    :param threshold: The threshold value for the partitioning algorithm.
                    Typically, the value zero is selected for this purpose.
    :returns: set -- the S set of nodes in the S-T partition
              set -- the T set of nodes in the S-T partition
    :raises: TypeError -- Algorithm only applicable to undirected hypergraphs

    """
    if not isinstance(H, UndirectedHypergraph):
        raise TypeError("Algorithm only applicable to undirected hypergraphs")

    # TODO: make sure that the hypergraph is connected

    delta = _compute_normalized_laplacian(H)
    eigenvalues, eigenvectors = np.linalg.eig(delta.todense())

    # Since the eigs method in sparse.linalg library doesn't find
    # all the eigenvalues and eigenvectors, it doesn't give us an
    # exact and correct solution. Therefore, we should use the
    # numpy library which works on dense graphs. This might be
    # problematic for large graphs.

    # eigenvalues,eigenvectors = linalg.eigs(delta,k=numberOfEigenValues)
    second_min_index = np.argsort(eigenvalues)[1]
    second_eigenvector = eigenvectors[:, second_min_index]

    nodeid2nodeset, nodeset2nodeid = ugt.get_nodeset2nodeid(H)
    partition_index = [i for i in range(len(second_eigenvector))
                       if second_eigenvector[i] >= threshold]
    S, T = set(), set()
    for (key, value) in list(nodeset2nodeid.items()):
        if value in partition_index:
            S.add(key)
        else:
            T.add(key)

    return S, T


def stationary_distribution(H, P=None):
    """Computes the stationary distribution of a random walk on the given
    hypergraph using the iterative approach explained in the paper:
    (http://pages.cs.wisc.edu/~shuchi/courses/787-F09/scribe-notes/lec15.pdf)

    :param H: the hypergraph to find the 'Stationary Distribution'
                    algorithm on.
    :returns: list -- list of the stationary probabilities for all nodes
            in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to undirected hypergraphs

    """
    if not isinstance(H, UndirectedHypergraph):
        raise TypeError("Algorithm only applicable to undirected hypergraphs")

    if P is None:
        P = _compute_transition_matrix(H)

    node_number = len(H.get_node_set())
    pi = _create_random_starter(node_number)
    pi_star = _create_random_starter(node_number)
    while not _has_converged(pi_star, pi):
        pi = pi_star
        pi_star = pi * P

    return pi


def _create_incidence_matrix(H):
    """Creates the 'Incidence Matrix' as a sparse matrix using the
    approach that is explained in the paper:
    (http://pages.cs.wisc.edu/~shuchi/courses/787-F09/scribe-notes/lec15.pdf)

    This algorithm finds the H matrix as explained in the above paper

    :param H: the H to find the W matrix on it.
    :returns: sparse.csc_matrix -- The Incidence Matrix as a sparse matrix
    :raises: TypeError -- Algorithm only applicable to undirected Hypergraphs
    """
    if not isinstance(H, UndirectedHypergraph):
        raise TypeError("Algorithm only applicable to undirected Hypergraphs")
    nodeNumber = len(H.get_node_set())
    edgeNumber = len(H.get_hyperedge_id_set())
    rows = []
    cols = []
    _, hyperedgename2hyperedgeid = ugt.get_hyperedgename2hyperedgeid(H)
    _, nodeset2nodeid = ugt.get_nodeset2nodeid(H)
    for (hyperedge_name, hyperedge_id) in \
    hyperedgename2hyperedgeid.iteritems():
        for node in H.get_hyperedge_nodes(hyperedge_name):
            # get the mapping btw node and its id
            rows.append(nodeset2nodeid.get(node))
            cols.append(hyperedge_id)
    values = np.ones(len(rows), dtype=int)
    return sparse.csc_matrix((values, (rows, cols)),
                             shape=(len(set(rows)),
                             len(set(cols))))


def _create_hyperedge_weight_matrix(H):
    """Creates the diagonal matrix of hyperedge weights as a sparse matrix.

    :param H: the hypergraph to find the W matrix on it.
    :returns: sparse.csc_matrix -- the diagonal edge weight matrix as a
            sparse matrix.

    """
    number_of_edges = len(H.get_hyperedge_id_set())
    hyperedge_weight = _get_hyperedge_weight_mapping(H)
    hyperedge_weight_vector = []

    for i in range(number_of_edges):
        hyperedge_weight_vector.append(hyperedge_weight.get(str(i)))

    return sparse.diags([hyperedge_weight_vector], [0])


def _create_vertex_degree_matrix(H):
    """Creates the diagonal maxtrix of vertex degrees as a sparse matrix,
    where a vertex degree is the sum of the weights of all hyperedges
    in the vertex's star.

    :param H: the hypergraph to find the vertex degree matrix on.
    :returns: sparse.csc_matrix -- the diagonal vertex degree matrix as a
            sparse matrix.

    """
    incidence_matrix = _create_incidence_matrix(H)
    W = _create_hyperedge_weight_matrix(H)

    return sparse.diags([incidence_matrix * W.diagonal()], [0])


def _create_hyperedge_degree_matrix(H):
    """Creates the diagonal matrix of hyperedge degrees as a sparse matrix,
    where a hyperedge degree is the cardinality of the hyperedge.

    :param H: the hypergraph to find the D_e matrix on.
    :returns: sparse.csc_matrix -- the diagonal hyperedge degree matrix as a
            sparse matrix.

    """
    number_of_edges = len(H.get_hyperedge_id_set())
    incidence_matrix = _create_incidence_matrix(H)
    degrees = incidence_matrix.sum(0).transpose()
    new_degree = []

    for degree in degrees:
        new_degree.append(int(degree[0:]))

    return sparse.diags([new_degree], [0])


def _fast_inverse(M):
    """Computes the inverse of a diagonal matrix.

    :param H: the diagonal matrix to find the inverse of.
    :returns: sparse.csc_matrix -- the inverse of the input matrix as a
            sparse matrix.

    """
    diags = M.diagonal()
    new_diag = []
    for value in diags:
        new_diag.append(1.0/value)

    return sparse.diags([new_diag], [0])


def _compute_transition_matrix(H):
    """Computes the transition matrix for a random walk on the given
    hypergraph as described in the paper:
    Zhou, Dengyong, Jiayuan Huang, and Bernhard Scholkopf.
    "Learning with hypergraphs: Clustering, classification, and embedding."
    Advances in neural information processing systems. 2006.
    (http://machinelearning.wustl.edu/mlpapers/paper_files/NIPS2006_630.pdf)

    :param H: the hypergraph to find the transition matrix of.
    :returns: sparse.csc_matrix -- the transition matrix as a sparse matrix.

    """
    inc_H = _create_incidence_matrix(H)
    D_v = _create_vertex_degree_matrix(H)
    D_e = _create_hyperedge_degree_matrix(H)
    W = _create_hyperedge_weight_matrix(H)
    D_v_inv = _fast_inverse(D_v)
    D_e_inv = _fast_inverse(D_e)
    inc_H_trans = inc_H.transpose()

    P = D_v_inv * inc_H * W * D_e_inv * inc_H_trans

    return P


def _compute_normalized_laplacian(H):
    """Computes the normalized Laplacian as described in the paper:
    Zhou, Dengyong, Jiayuan Huang, and Bernhard Scholkopf.
    "Learning with hypergraphs: Clustering, classification, and embedding."
    Advances in neural information processing systems. 2006.
    (http://machinelearning.wustl.edu/mlpapers/paper_files/NIPS2006_630.pdf)

    :param H: the hypergraph to compute the normalized Laplacian
                    matrix for.
    :returns: sparse.csc_matrix -- the normalized Laplacian matrix as a sparse
            matrix.

    """
    inc_H = _create_incidence_matrix(H)
    D_v = _create_vertex_degree_matrix(H)
    D_e = _create_hyperedge_degree_matrix(H)
    W = _create_hyperedge_weight_matrix(H)
    D_v_sqrt = D_v.sqrt()
    D_v_sqrt_inv = np.real(_fast_inverse(D_v_sqrt).todense())
    D_v_sqrt_inv = sparse.csc_matrix(D_v_sqrt_inv)
    D_e_inv = _fast_inverse(D_e)
    inc_H_trans = inc_H.transpose()

    theta = D_v_sqrt_inv * inc_H * W * D_e_inv * inc_H_trans * D_v_sqrt_inv

    node_number = len(H.get_node_set())
    I = sparse.eye(node_number)

    delta = I - theta
    return delta


def _get_hyperedge_weight_mapping(H):
    """Computes the weight of each hyperedge.

    :param H: the hypergraph to find the weights.
    :returns: dict -- The mapping from edgeid to its weight

    """
    hyperedge_weight = {}
    for hyperedge_id in H.hyperedge_id_iterator():
        hyperedge_weight.update({str(int(hyperedge_id[1:])-1):
                                H.get_hyperedge_weight(hyperedge_id)})

    return hyperedge_weight


def _create_random_starter(n):
    """Creates the random starter for the random walk.

    :param n: number of nodes to create the random vector.
    :returns: list -- list of starting probabilities for each node.

    """
    pi = np.zeros(n, dtype=float)
    for i in range(n):
        pi[i] = random.random()
    summation = np.sum(pi)
    for i in range(n):
        pi[i] = pi[i] / summation

    return pi


def _has_converged(pi_star, pi):
    """Checks if the random walk has converged.

    :param pi_star: the new vector
    :param pi: the old vector
    :returns: bool-- True iff pi has converged.

    """
    node_number = pi.shape[0]
    EPS = 10e-6
    for i in range(node_number):
        if pi[i] - pi_star[i] > EPS:
            return False

    return True
