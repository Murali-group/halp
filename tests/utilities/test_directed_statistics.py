from hypergraph.directed_hypergraph import DirectedHypergraph
from hypergraph.utilities import directed_statistics


def test_number_of_nodes():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.number_of_nodes(H) == 8

    # Try counting an invalid directed hypergraph
    try:
        directed_statistics.number_of_nodes("invalid hypergraph")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_number_of_hyperedges():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.number_of_hyperedges(H) == 8

    # Try counting an invalid directed hypergraph
    try:
        directed_statistics.number_of_hyperedges("invalid hypergraph")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_max_outdegree():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.max_outdegree(H) == 4

    # Try counting an invalid directed hypergraph
    try:
        directed_statistics.max_outdegree("invalid hypergraph")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_min_outdegree():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.min_outdegree(H) == 0


def test_average_outdegree():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.average_outdegree(H) == 11 / float(8)


def test_max_indegree():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.max_indegree(H) == 3

    # Try counting an invalid directed hypergraph
    try:
        directed_statistics.max_indegree("invalid hypergraph")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_min_indegree():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.min_indegree(H) == 0


def test_average_indegree():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.average_indegree(H) == 11 / float(8)


def test_max_tail_cardinalitiy():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.max_tail_cardinality(H) == 3

    # Try counting an invalid directed hypergraph
    try:
        directed_statistics.max_tail_cardinality("invalid hypergraph")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_min_tail_cardinalitiy():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.min_tail_cardinality(H) == 1


def test_average_tail_cardinalitiy():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.average_tail_cardinality(H) == 11 / float(8)


def test_max_head_cardinalitiy():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.max_head_cardinality(H) == 2

    # Try counting an invalid directed hypergraph
    try:
        directed_statistics.max_head_cardinality("invalid hypergraph")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_min_head_cardinalitiy():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.min_head_cardinality(H) == 1


def test_average_head_cardinalitiy():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.average_head_cardinality(H) == 11 / float(8)
