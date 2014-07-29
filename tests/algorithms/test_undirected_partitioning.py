from hypergraph.undirected_hypergraph import UndirectedHypergraph
from hypergraph.algorithms import undirected_partitioning as partitioning


def test_normalized_hypergraph_cut():
    H = UndirectedHypergraph()
    H.read('./tests/data/basic_undirected_hypergraph.txt')
    
    partition = partitioning.normalized_hypergraph_cut(H)
    
    # Correctness tests go here
    
    # Try partitioning an invalid undirected hypergraph
    try:
        partition = partitioning.normalized_hypergraph_cut("H")
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

    # Try partitioning an invalid undirected hypergraph
    try:
        pi = partitioning.stationary_distribution("H")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e
