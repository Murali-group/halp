"""
.. module:: directed_random_walk
   :synopsis: Defines several functions for performing a random walk on
            a directed hypergraph and finding its corresponding stationary
            distribution.
"""
import numpy as np
from scipy import sparse
from scipy.sparse import linalg
import random

from halp.directed_hypergraph import DirectedHypergraph
from halp.utilities import directed_matrices as dmat


def stationary_distribution(H, pi=None, P=None):
    """Computes the stationary distribution of a random walk on the given
    hypergraph using the iterative approach explained in the paper:
    Aurelien Ducournau, Alain Bretto, Random walks in directed hypergraphs and
    application to semi-supervised image segmentation,
    Computer Vision and Image Understanding, Volume 120, March 2014,
    Pages 91-102, ISSN 1077-3142, http://dx.doi.org/10.1016/j.cviu.2013.10.012.
    (http://www.sciencedirect.com/science/article/pii/S1077314213002038)

    :param H: the hypergraph to find the 'Stationary Distribution'
            algorithm on.
    :param pi: the initial distribution over the nodes. If not provided,
            it will be created with a random distribution.
    :param P: the transition matrix for the hypergraph. If not provided,
            it will be created.
    :returns: list -- list of the stationary probabilities for all nodes
            in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to undirected hypergraphs
    :raises: AssertionError -- Each node must have at least 1 outgoing
             hyperedge (even if it's only a self-loop).

    """
    if not isinstance(H, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to undirected hypergraphs")

    for node in H.node_iterator():
        if len(H.get_forward_star(node)) == 0:
            raise AssertionError("Each node must have at least 1 outgoing \
                                  hyperedge (even if it's only a self-loop).")

    indices_to_nodes, nodes_to_indices = \
        dmat.get_node_mapping(H)
    indices_to_hyperedge_ids, hyperedge_ids_to_indices = \
        dmat.get_hyperedge_id_mapping(H)

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
    Aurelien Ducournau, Alain Bretto, Random walks in directed hypergraphs and
    application to semi-supervised image segmentation,
    Computer Vision and Image Understanding, Volume 120, March 2014,
    Pages 91-102, ISSN 1077-3142, http://dx.doi.org/10.1016/j.cviu.2013.10.012.
    (http://www.sciencedirect.com/science/article/pii/S1077314213002038)

    :param H: the hypergraph to find the transition matrix of.
    :param nodes_to_indices: for each node, maps the node to its
                            corresponding integer index.
    :param hyperedge_ids_to_indices: for each hyperedge ID, maps the hyperedge
                                    ID to its corresponding integer index.
    :returns: sparse.csc_matrix -- the transition matrix as a sparse matrix.

    """
    M_out = dmat.get_tail_incidence_matrix(H,
                                           nodes_to_indices,
                                           hyperedge_ids_to_indices)
    M_in = dmat.get_head_incidence_matrix(H,
                                          nodes_to_indices,
                                          hyperedge_ids_to_indices)
    W = dmat.get_hyperedge_weight_matrix(H, hyperedge_ids_to_indices)
    D_v_out = dmat.get_vertex_degree_matrix(M_out, W)
    D_e_in = dmat.get_hyperedge_degree_matrix(M_in)

    D_v_out_inv = dmat.fast_inverse(D_v_out)
    D_e_in_inv = dmat.fast_inverse(D_e_in)
    M_in_trans = M_in.transpose()

    P = D_v_out_inv * M_out * W * D_e_in_inv * M_in_trans

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
