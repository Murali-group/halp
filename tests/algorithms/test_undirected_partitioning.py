from hypergraph.undirected_hypergraph import UndirectedHypergraph
from hypergraph.algorithms import undirected_partitioning as partitioning
from hypergraph.utilities import undirected_matrices as umat
from math import fabs
import numpy as np


def test_laplacian():
    '''
    To test the normalized cut, I wrote the same functions in Matlab
    and compared the result of it with the current library code. In
    this test, I calculated the delta matrix using Matlab and found
    the summation of each column of this matrix and compared that
    summation to the result of our code.
    The following is the matlab snippet that is used for this test:
    M = [1 0 1 0 0 0 0 0 0;1 1 0 0 1 0 0 0 0 ;1 0 1 0 0 0 0 0 0;\
    0 1 0 1 0 0 0 0 0;0 0 0 1 0 0 0 0 0;0 0 0 0 1 1 0 0 0;\
    0 0 0 0 0 1 0 0 1;0 0 0 0 0 1 1 1 0;0 0 0 0 0 0 1 0 0;\
    0 0 0 0 0 0 1 0 0;0 0 0 0 0 0 0 1 1;0 0 0 0 0 0 0 0 1];
    W = diag([9.1 10 1 1 3 2 4 3.5 4.1]);
    d_v = diag(H * diag(W));
    d_e = diag(sum(M));
    d_v_sqrt = sqrtm(d_v);
    d_v_sqrt_inv = inv(d_v_sqrt);
    d_e_inv = inv(d_e);
    M_trans = M';
    theta = d_v_sqrt_inv * H * W * d_e_inv * H_trans * d_v_sqrt_inv
    [n m] = size(M);
    I = eye(n);
    delta = I-theta
    '''
    H = UndirectedHypergraph()
    H.read('./tests/data/basic_undirected_hypergraph.txt')
    indices_to_nodes, nodes_to_indices = \
        umat.get_node_mapping(H)
    indices_to_hyperedge_id, hyperedge_id_to_indices = \
        umat.get_hyperedge_id_mapping(H)

    delta = partitioning._compute_normalized_laplacian(H, nodes_to_indices,
                                                       hyperedge_id_to_indices)
    
    delta_column_sum = np.sum(delta.todense(), axis=0)
    delta_column_sum = np.squeeze(np.asarray(delta_column_sum))

    Matlab_output = {'v1': 0.0973, 'v2': -0.3008, 'v3': 0.0973,
                     'v4': 0.0286, 'v5': 0.3492, 'v7': 0.2065, 'v8': -0.0156,
                     'v9': -0.2176, 'v10': 0.1170, 'v11': 0.1170,
                     'v12': -0.0616, 'v13': 0.1486}

    for key, value in Matlab_output.items():
        index = nodes_to_indices.get(key)
        assert fabs(delta_column_sum[index]-value) < 10e-4


def test_normalized_hypergraph_cut():
    H = UndirectedHypergraph()
    H.read('./tests/data/basic_undirected_hypergraph.txt')
    S, T = partitioning.normalized_hypergraph_cut(H)

    # Correctness tests go here
    assert S
    assert T
    assert not S.intersection(T)

    # Try partitioning an invalid undirected hypergraph
    try:
        S, T = partitioning.normalized_hypergraph_cut("H")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_stationary_distribution():
    H = UndirectedHypergraph()
    H.read('./tests/data/basic_undirected_hypergraph.txt')

    pi = partitioning.stationary_distribution(H)

    # Correctness tests go here
    assert sum(pi)-1.0 < 10e-4
    # Try partitioning an invalid undirected hypergraph
    try:
        pi = partitioning.stationary_distribution("H")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e
