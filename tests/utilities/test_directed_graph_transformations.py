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

    # Try posting an invalid directed hypergraph
    try:
        directed_graph_transformations.to_graph_decomposition("invalid H")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_to_networkx_digraph():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    G = directed_graph_transformations.to_networkx_digraph(H)

    H_nodes = H.get_node_set()
    G_nodes = G.node.keys()

    assert H_nodes == set(G_nodes)

    H_nodes_attributes = [H.get_node_attributes(node) for node in H_nodes]
    for node in G_nodes:
        assert G.node[node] in H_nodes_attributes

    for hyperedge_id in H.hyperedge_id_iterator():
        tail_set = H.get_hyperedge_tail(hyperedge_id)
        head_set = H.get_hyperedge_head(hyperedge_id)
        for tail_node in tail_set:
            for head_node in head_set:
                assert G[tail_node][head_node]

    # Try transforming an invalid directed hypergraph
    try:
        directed_graph_transformations.to_networkx_digraph("invalid H")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_from_networkx_digraph():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    nxG = directed_graph_transformations.to_networkx_digraph(H)

    G = directed_graph_transformations.from_networkx_digraph(nxG)

    nxG_nodes = nxG.node.keys()
    G_nodes = G.get_node_set()

    assert G_nodes == set(nxG_nodes)

    for edge in nxG.edges_iter():
        tail_node = edge[0]
        head_node = edge[1]
        assert G.has_hyperedge(tail_node, head_node)

    # Try transforming an invalid directed hypergraph
    try:
        directed_graph_transformations.from_networkx_digraph("G")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e
