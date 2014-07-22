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


def test_mean_outdegree():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.mean_outdegree(H) == 11 / float(8)


def test_outdegree_list():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    outdegree_list = directed_statistics.outdegree_list(H)
    assert len(outdegree_list) == 8
    assert outdegree_list.count(0) == 1
    assert outdegree_list.count(1) == 5
    assert outdegree_list.count(2) == 1
    assert outdegree_list.count(4) == 1


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


def test_mean_indegree():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.mean_indegree(H) == 11 / float(8)


def test_indegree_list():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    indegree_list = directed_statistics.indegree_list(H)
    assert len(indegree_list) == 8
    assert indegree_list.count(0) == 1
    assert indegree_list.count(1) == 4
    assert indegree_list.count(2) == 2
    assert indegree_list.count(3) == 1


def test_max_tail_cardinalitiy():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.max_hyperedge_tail_cardinality(H) == 3

    # Try counting an invalid directed hypergraph
    try:
        directed_statistics.max_hyperedge_tail_cardinality(
            "invalid hypergraph")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_min_tail_cardinalitiy():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.min_hyperedge_tail_cardinality(H) == 1


def test_mean_tail_cardinalitiy():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.mean_hyperedge_tail_cardinality(H) == \
        11 / float(8)


def test_hyperedge_tail_cardinality_list():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    hyperedge_tail_cardinality_list = \
        directed_statistics.hyperedge_tail_cardinality_list(H)
    assert len(hyperedge_tail_cardinality_list) == 8
    assert hyperedge_tail_cardinality_list.count(1) == 6
    assert hyperedge_tail_cardinality_list.count(2) == 1
    assert hyperedge_tail_cardinality_list.count(3) == 1


def test_max_head_cardinalitiy():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.max_hyperedge_head_cardinality(H) == 2

    # Try counting an invalid directed hypergraph
    try:
        directed_statistics.max_hyperedge_head_cardinality(
            "invalid hypergraph")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_min_head_cardinalitiy():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.min_hyperedge_head_cardinality(H) == 1


def test_mean_head_cardinalitiy():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.mean_hyperedge_head_cardinality(H) == \
        11 / float(8)


def test_hyperedge_head_cardinality_list():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    hyperedge_head_cardinality_list = \
        directed_statistics.hyperedge_head_cardinality_list(H)
    assert len(hyperedge_head_cardinality_list) == 8
    assert hyperedge_head_cardinality_list.count(1) == 5
    assert hyperedge_head_cardinality_list.count(2) == 3


def test_max_hyperedge_cardinalitiy_ratio():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.max_hyperedge_cardinality_ratio(H) == 2

    # Try counting an invalid directed hypergraph
    try:
        directed_statistics.max_hyperedge_cardinality_ratio(
            "invalid hypergraph")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_min_hyperedge_cardinalitiy_ratio():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.min_hyperedge_cardinality_ratio(H) == .5


def test_mean_hyperedge_cardinalitiy_ratio():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_statistics.mean_hyperedge_cardinality_ratio(H) == 1.0625


def test_hyperedge_cardinality_ratio_list():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    ratio_list = [0.5, 1.0, 1.0, 1.0, 2.0, 1.0, 1.5, 0.5]
    returned_list = directed_statistics.hyperedge_cardinality_ratio_list(H)

    assert sorted(ratio_list) == sorted(returned_list)
