from halp.directed_hypergraph import DirectedHypergraph
from halp.algorithms import directed_random_walk as rw


def test_stationary_distribution():
    H = DirectedHypergraph()
    H.read('./tests/data/basic_directed_hypergraph.txt')
    
    # Try random-walking a directed hypergraph with a node
    # with no outgoing hyperedges
    try:
        pi = rw.stationary_distribution(H)
        assert False
    except AssertionError:
        pass
    except BaseException as e:
        assert False, e

    # Try random-walking a valid directed hypergraph
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
