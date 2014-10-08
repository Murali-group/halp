"""
.. module:: directed_matrices
   :synopsis: Provides various methods for tranforming a hypergraph
            (or its components) into useful corresponding matrix
            representations.
"""
import numpy as np
from scipy import sparse

from halp.directed_hypergraph import DirectedHypergraph


def get_node_mapping(H):
    """Generates mappings between the set of nodes and integer indices (where
    every node corresponds to exactly 1 integer index).

    :param H: the hypergraph to find the node mapping on.
    :returns: dict -- for each integer index, maps the index to the node.
              dict -- for each node, maps the node to the integer index.

    """
    node_set = H.get_node_set()
    nodes_to_indices, indices_to_nodes = {}, {}

    node_index = 0
    for node in node_set:
        nodes_to_indices.update({node: node_index})
        indices_to_nodes.update({node_index: node})
        node_index += 1

    return indices_to_nodes, nodes_to_indices


def get_hyperedge_id_mapping(H):
    """Generates mappings between the set of hyperedge IDs and integer indices
    (where every hyperedge ID corresponds to exactly 1 integer index).

    :param H: the hypergraph to find the hyperedge ID mapping on.
    :returns: dict -- for each integer index, maps the index to the hyperedge
                ID.
              dict -- for each hyperedge ID, maps the hyperedge ID to the
                integer index.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    if not isinstance(H, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    indices_to_hyperedge_ids, hyperedge_ids_to_indices = {}, {}
    hyperedge_index = 0
    for hyperedge_id in H.hyperedge_id_iterator():
        hyperedge_ids_to_indices.update({hyperedge_id: hyperedge_index})
        indices_to_hyperedge_ids.update({hyperedge_index: hyperedge_id})
        hyperedge_index += 1

    return indices_to_hyperedge_ids, hyperedge_ids_to_indices


def get_tail_incidence_matrix(H, nodes_to_indices, hyperedge_ids_to_indices):
    """Creates the incidence matrix of the tail nodes of the given
    hypergraph as a sparse matrix.

    :param H: the hypergraph for which to create the incidence matrix of.
    :param nodes_to_indices: for each node, maps the node to its
                            corresponding integer index.
    :param hyperedge_ids_to_indices: for each hyperedge ID, maps the hyperedge
                                    ID to its corresponding integer index.
    :returns: sparse.csc_matrix -- the incidence matrix as a sparse matrix.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    if not isinstance(H, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    rows, cols = [], []
    for hyperedge_id, hyperedge_index in hyperedge_ids_to_indices.items():
        for node in H.get_hyperedge_tail(hyperedge_id):
            # get the mapping between the node and its ID
            rows.append(nodes_to_indices.get(node))
            cols.append(hyperedge_index)

    values = np.ones(len(rows), dtype=int)
    node_count = len(H.get_node_set())
    hyperedge_count = len(H.get_hyperedge_id_set())

    return sparse.csc_matrix((values, (rows, cols)),
                             shape=(node_count, hyperedge_count))


def get_head_incidence_matrix(H, nodes_to_indices, hyperedge_ids_to_indices):
    """Creates the incidence matrix of the head nodes of the given
    hypergraph as a sparse matrix.

    :param H: the hypergraph for which to create the incidence matrix of.
    :param nodes_to_indices: for each node, maps the node to its
                            corresponding integer index.
    :param hyperedge_ids_to_indices: for each hyperedge ID, maps the hyperedge
                                    ID to its corresponding integer index.
    :returns: sparse.csc_matrix -- the incidence matrix as a sparse matrix.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    if not isinstance(H, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    rows, cols = [], []
    for hyperedge_id, hyperedge_index in hyperedge_ids_to_indices.items():
        for node in H.get_hyperedge_head(hyperedge_id):
            # get the mapping between the node and its ID
            rows.append(nodes_to_indices.get(node))
            cols.append(hyperedge_index)

    values = np.ones(len(rows), dtype=int)
    node_count = len(H.get_node_set())
    hyperedge_count = len(H.get_hyperedge_id_set())

    return sparse.csc_matrix((values, (rows, cols)),
                             shape=(node_count, hyperedge_count))


def get_hyperedge_weight_matrix(H, hyperedge_ids_to_indices):
    """Creates the diagonal matrix W of hyperedge weights as a sparse matrix.

    :param H: the hypergraph to find the weights.
    :param hyperedge_weights: the mapping from the indices of hyperedge IDs to
                            the corresponding hyperedge weights.
    :returns: sparse.csc_matrix -- the diagonal edge weight matrix as a
            sparse matrix.

    """
    # Combined 2 methods into 1; this could be written better
    hyperedge_weights = {}
    for hyperedge_id in H.hyperedge_id_iterator():
        hyperedge_weights.update({hyperedge_ids_to_indices[hyperedge_id]:
                                 H.get_hyperedge_weight(hyperedge_id)})

    hyperedge_weight_vector = []
    for i in range(len(hyperedge_weights.keys())):
        hyperedge_weight_vector.append(hyperedge_weights.get(i))

    return sparse.diags([hyperedge_weight_vector], [0])


def get_vertex_degree_matrix(M, W):
    """Creates the diagonal maxtrix D_v of vertex degrees as a sparse matrix,
    where a vertex degree is the sum of the weights of all hyperedges
    in the vertex's star.

    :param M: the incidence matrix of the hypergraph to find the D_v matrix on.
    :param W: the diagonal hyperedge weight matrix of the hypergraph.
    :returns: sparse.csc_matrix -- the diagonal vertex degree matrix as a
            sparse matrix.

    """
    return sparse.diags([M * W.diagonal()], [0])


def get_hyperedge_degree_matrix(M):
    """Creates the diagonal matrix of hyperedge degrees D_e as a sparse matrix,
    where a hyperedge degree is the cardinality of the hyperedge.

    :param M: the incidence matrix of the hypergraph to find the D_e matrix on.
    :returns: sparse.csc_matrix -- the diagonal hyperedge degree matrix as a
            sparse matrix.

    """
    degrees = M.sum(0).transpose()
    new_degree = []
    for degree in degrees:
        new_degree.append(int(degree[0:]))

    return sparse.diags([new_degree], [0])


def fast_inverse(M):
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
