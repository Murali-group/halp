from hypergraph.directed_hypergraph import DirectedHypergraph
from hypergraph.algorithms import directed_random_walk as rw


def test_stationary_distribution():
    H = DirectedHypergraph()
    H.read('./tests/data/basic_directed_hypergraph.txt')
    H.add_hyperedge(["u"],["u"], weight=1)

    pi = rw.stationary_distribution(H)

    # Correctness tests go here

    # Try partitioning an invalid directed hypergraph
    try:
        pi = rw.stationary_distribution("H")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e
