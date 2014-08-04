from hypergraph.undirected_hypergraph import UndirectedHypergraph

from hypergraph.utilities import undirected_graph_transformations


def test_to_graph_decomposition():
    H = UndirectedHypergraph()
    H.read("tests/data/basic_undirected_hypergraph.txt")

    G = undirected_graph_transformations.to_graph_decomposition(H)

    assert G.get_node_set() == H.get_node_set()

    for hyperedge_id in G.hyperedge_id_iterator():
        hyperedge_nodes = G.get_hyperedge_nodes(hyperedge_id)
        assert len(hyperedge_nodes) == 2
        assert G.has_hyperedge((hyperedge_nodes[0], hyperedge_nodes[1]))

    # Try posting an invalid undirected hypergraph
    try:
        undirected_graph_transformations.to_graph_decomposition("invalid H")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_to_networkx_graph():
    H = UndirectedHypergraph()
    H.read("tests/data/basic_undirected_hypergraph.txt")

    G = undirected_graph_transformations.to_networkx_graph(H)

    H_nodes = H.get_node_set()
    G_nodes = G.node.keys()

    assert H_nodes == set(G_nodes)

    H_nodes_attributes = [H.get_node_attributes(node) for node in H_nodes]
    for node in G_nodes:
        assert G.node[node] in H_nodes_attributes

    for hyperedge_id in H.hyperedge_id_iterator():
        hyperedge_nodes = H.get_hyperedge_nodes(hyperedge_id)
        for node_a in hyperedge_nodes:
            for node_b in hyperedge_nodes:
                if node_a != node_b:
                    assert G.has_edge(node_a, node_b)
                else:
                    if G.has_edge(node_a, node_b):
                        assert False

    # Try transforming an invalid undirected hypergraph
    try:
        undirected_graph_transformations.to_networkx_graph("invalid H")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_from_networkx_graph():
    H = UndirectedHypergraph()
    H.read("tests/data/basic_undirected_hypergraph.txt")

    nxG = undirected_graph_transformations.to_networkx_graph(H)

    G = undirected_graph_transformations.from_networkx_graph(nxG)

    nxG_nodes = nxG.node.keys()
    G_nodes = G.get_node_set()

    assert G_nodes == set(nxG_nodes)

    for edge in nxG.edges_iter():
        assert G.has_hyperedge((edge[0], edge[1]))

    # Try transforming an invalid undirected hypergraph
    try:
        undirected_graph_transformations.from_networkx_graph("G")
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e
