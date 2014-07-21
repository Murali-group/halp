from hypergraph.directed_hypergraph import DirectedHypergraph

from hypergraph.utilities import directed_graph_transformations


def test_to_graph_decomposition():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    G = directed_graph_transformations.to_graph_decomposition(H)
    G._check_consistency()
    
    assert G.get_node_set() == H.get_node_set()

    for hyperedge_id in G.hyperedge_id_iterator():
        tail_set = G.get_hyperedge_tail(hyperedge_id)
        head_set = G.get_hyperedge_head(hyperedge_id)
        assert len(tail_set) == 1
        assert len(head_set) == 1
        assert G.has_hyperedge(tail_set.pop(), head_set.pop())

    # Try posting invalid directed hypergraph
    try:
        directed_graph_transformations.to_graph_decomposition("invalid H")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e
