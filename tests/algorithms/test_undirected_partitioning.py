from hypergraph.undirected_hypergraph import UndirectedHypergraph
from hypergraph.algorithms import undirected_partitioning as partitioning


def test_init():
    H = UndirectedHypergraph()
    H.read('./tests/data/Undirectedhypergraph.txt')

    W = partitioning._get_hyperedge_weight_matrix(H)
    nl = partitioning._compute_normalized_laplacian(H)

    partition = partitioning.normalized_hypergraph_cut(H, 0)
    assert len(partition) == 2
