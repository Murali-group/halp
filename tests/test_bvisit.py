from __future__ import absolute_import

from hypergraph.directedHyperGraph import DirectedHyperGraph

def test_bvisit():
    '''
        Test B-visiting a hypergraph from various starting vertices
    '''
    # read directed hypergraph
    graph = DirectedHyperGraph(set(), set())
    graph.read('tests/data/unweightedDirectedHypergraph.txt')
    nodes = graph.nodes
    hyperedges = graph.hyperedges

    x1 = graph.get_node_by_name('x1')
    x2 = graph.get_node_by_name('x2')
    x3 = graph.get_node_by_name('x3')
    x4 = graph.get_node_by_name('x4')
    x5 = graph.get_node_by_name('x5')
    x6 = graph.get_node_by_name('x6')
    x7 = graph.get_node_by_name('x7')
    x8 = graph.get_node_by_name('x8')
    x9 = graph.get_node_by_name('x9')
    x10 = graph.get_node_by_name('x10')
    x11 = graph.get_node_by_name('x11')
    x12 = graph.get_node_by_name('x12')

    assert len(nodes) == 12
    assert len(hyperedges) == 10

    Bvisitx1 = graph.b_visit(x1)
    Bvisitx2 = graph.b_visit(x2) 

    assert Bvisitx1 == set(x1,x3,x7)
    assert Bvisitx2 == set(x1,x2,x3,x4,x5,x6,x7,x8,x9,x10)
