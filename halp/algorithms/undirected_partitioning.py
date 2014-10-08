"""
.. module:: undirected_partitioning
   :synopsis: Defines several functions for doing random walk, finding
            the stationary distribution, and finding the min-cut for
            an undirected hypergraph.
"""
import numpy as np
from scipy import sparse
from scipy.sparse import linalg
import random

from halp.undirected_hypergraph import UndirectedHypergraph
from halp.utilities import undirected_matrices as umat


def normalized_hypergraph_cut(H, threshold=0):
    """Executes the min-cut algorithm described in the paper:
    Zhou, Dengyong, Jiayuan Huang, and Bernhard Scholkopf.
    "Learning with hypergraphs: Clustering, classification, and embedding."
    Advances in neural information processing systems. 2006.
    (http://machinelearning.wustl.edu/mlpapers/paper_files/NIPS2006_630.pdf)

    This algorithm uses the normalized Laplacian to partition the hypergraph
    into two disjoint components.

    :param H: the hypergraph to perform the hypergraph-cut algorithm on.
    :param threshold: The threshold value for the partitioning algorithm.
                    Typically, the value zero is selected for this purpose.
    :returns: set -- the S set of nodes in the S-T partition
              set -- the T set of nodes in the S-T partition
    :raises: TypeError -- Algorithm only applicable to undirected hypergraphs

    """
    if not isinstance(H, UndirectedHypergraph):
        raise TypeError("Algorithm only applicable to undirected hypergraphs")

    # TODO: make sure that the hypergraph is connected

    # Get index<->node mappings and index<->hyperedge_id mappings for matrices
    indices_to_nodes, nodes_to_indices = \
        umat.get_node_mapping(H)
    indices_to_hyperedge_ids, hyperedge_ids_to_indices = \
        umat.get_hyperedge_id_mapping(H)

    delta = _compute_normalized_laplacian(H,
                                          nodes_to_indices,
                                          hyperedge_ids_to_indices)

    # Since the eigs method in sparse.linalg library doesn't find
    # all the eigenvalues and eigenvectors, it doesn't give us an
    # exact and correct solution. Therefore, we should use the
    # numpy library which works on dense graphs. This might be
    # problematic for large graphs.
    # New note: I think we only need the 2 smallest eigenvalues, which
    # can be found with the sparse solver. Look into this if run-time
    # becomes an issue.

    # eigenvalues,eigenvectors = linalg.eigs(delta,k=numberOfEigenValues)
    eigenvalues, eigenvectors = np.linalg.eig(delta.todense())

    second_min_index = np.argsort(eigenvalues)[1]
    second_eigenvector = eigenvectors[:, second_min_index]
    partition_index = [i for i in range(len(second_eigenvector))
                       if second_eigenvector[i] >= threshold]

    S, T = set(), set()
    for key, value in nodes_to_indices.items():
        if value in partition_index:
            S.add(key)
        else:
            T.add(key)

    return S, T


def _compute_normalized_laplacian(H,
                                  nodes_to_indices,
                                  hyperedge_ids_to_indices):
    """Computes the normalized Laplacian as described in the paper:
    Zhou, Dengyong, Jiayuan Huang, and Bernhard Scholkopf.
    "Learning with hypergraphs: Clustering, classification, and embedding."
    Advances in neural information processing systems. 2006.
    (http://machinelearning.wustl.edu/mlpapers/paper_files/NIPS2006_630.pdf)

    :param H: the hypergraph to compute the normalized Laplacian
                    matrix for.
    :param nodes_to_indices: for each node, maps the node to its
                            corresponding integer index.
    :param hyperedge_ids_to_indices: for each hyperedge ID, maps the hyperedge
                                    ID to its corresponding integer index.
    :returns: sparse.csc_matrix -- the normalized Laplacian matrix as a sparse
            matrix.

    """
    M = umat.get_incidence_matrix(H,
                                  nodes_to_indices, hyperedge_ids_to_indices)
    W = umat.get_hyperedge_weight_matrix(H, hyperedge_ids_to_indices)
    D_v = umat.get_vertex_degree_matrix(M, W)
    D_e = umat.get_hyperedge_degree_matrix(M)

    D_v_sqrt = D_v.sqrt()
    D_v_sqrt_inv = np.real(umat.fast_inverse(D_v_sqrt).todense())
    D_v_sqrt_inv = sparse.csc_matrix(D_v_sqrt_inv)
    D_e_inv = umat.fast_inverse(D_e)
    M_trans = M.transpose()

    theta = D_v_sqrt_inv * M * W * D_e_inv * M_trans * D_v_sqrt_inv

    node_count = len(H.get_node_set())
    I = sparse.eye(node_count)

    delta = I - theta
    return delta


def stationary_distribution(H, pi=None, P=None):
    """Computes the stationary distribution of a random walk on the given
    hypergraph using the iterative approach explained in the paper:
    (http://pages.cs.wisc.edu/~shuchi/courses/787-F09/scribe-notes/lec15.pdf)

    :param H: the hypergraph to find the stationary distribution on.
    :param pi: the initial distribution over the nodes. If not provided,
            it will be created with a random distribution.
    :param P: the transition matrix for the hypergraph. If not provided,
            it will be created.
    :returns: list -- list of the stationary probabilities for all nodes
            in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to undirected hypergraphs

    """
    if not isinstance(H, UndirectedHypergraph):
        raise TypeError("Algorithm only applicable to undirected hypergraphs")

    indices_to_nodes, nodes_to_indices = \
        umat.get_node_mapping(H)
    indices_to_hyperedge_ids, hyperedge_ids_to_indices = \
        umat.get_hyperedge_id_mapping(H)

    if P is None:
        P = _compute_transition_matrix(H,
                                       nodes_to_indices,
                                       hyperedge_ids_to_indices)

    node_count = len(H.get_node_set())
    if pi is None:
        pi = _create_random_starter(node_count)
    pi_star = _create_random_starter(node_count)
    while not _has_converged(pi_star, pi):
        pi = pi_star
        pi_star = pi * P

    return pi


def _compute_transition_matrix(H,
                               nodes_to_indices,
                               hyperedge_ids_to_indices):
    """Computes the transition matrix for a random walk on the given
    hypergraph as described in the paper:
    Zhou, Dengyong, Jiayuan Huang, and Bernhard Scholkopf.
    "Learning with hypergraphs: Clustering, classification, and embedding."
    Advances in neural information processing systems. 2006.
    (http://machinelearning.wustl.edu/mlpapers/paper_files/NIPS2006_630.pdf)

    :param H: the hypergraph to find the transition matrix of.
    :param nodes_to_indices: for each node, maps the node to its
                            corresponding integer index.
    :param hyperedge_ids_to_indices: for each hyperedge ID, maps the hyperedge
                                    ID to its corresponding integer index.
    :returns: sparse.csc_matrix -- the transition matrix as a sparse matrix.

    """
    M = umat.get_incidence_matrix(H,
                                  nodes_to_indices, hyperedge_ids_to_indices)
    W = umat.get_hyperedge_weight_matrix(H, hyperedge_ids_to_indices)
    D_v = umat.get_vertex_degree_matrix(M, W)
    D_e = umat.get_hyperedge_degree_matrix(M)

    D_v_inv = umat.fast_inverse(D_v)
    D_e_inv = umat.fast_inverse(D_e)
    M_trans = M.transpose()

    P = D_v_inv * M * W * D_e_inv * M_trans

    return P


def _create_random_starter(node_count):
    """Creates the random starter for the random walk.

    :param node_count: number of nodes to create the random vector.
    :returns: list -- list of starting probabilities for each node.

    """
    pi = np.zeros(node_count, dtype=float)
    for i in range(node_count):
        pi[i] = random.random()
    summation = np.sum(pi)
    for i in range(node_count):
        pi[i] = pi[i] / summation

    return pi


def _has_converged(pi_star, pi):
    """Checks if the random walk has converged.

    :param pi_star: the new vector
    :param pi: the old vector
    :returns: bool-- True iff pi has converged.

    """
    node_count = pi.shape[0]
    EPS = 10e-6
    for i in range(node_count):
        if pi[i] - pi_star[i] > EPS:
            return False

    return True
