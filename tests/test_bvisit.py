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
    Bvisitx3 = graph.b_visit(x3) 
    Bvisitx4 = graph.b_visit(x4) 
    Bvisitx5 = graph.b_visit(x5) 
    Bvisitx6 = graph.b_visit(x6) 
    Bvisitx7 = graph.b_visit(x7) 
    Bvisitx8 = graph.b_visit(x8) 
    Bvisitx9 = graph.b_visit(x9) 
    Bvisitx10 = graph.b_visit(x10) 
    Bvisitx11 = graph.b_visit(x11) 
    Bvisitx12 = graph.b_visit(x12) 

    assert Bvisitx1 == set([x1,x3,x7])
    assert Bvisitx2 == set([x1,x2,x3,x4,x5,x6,x7,x8,x9,x10])
    assert Bvisitx3 == set([x3, x7])
    assert Bvisitx4 == set([x4])
    assert Bvisitx5 == set([x5])
    assert Bvisitx6 == set([x6])
    assert Bvisitx7 == set([x7])
    assert Bvisitx8 == set([x8])
    assert Bvisitx9 == set([x9])
    assert Bvisitx10 == set([x10,x1,x3,x7])
    assert Bvisitx11 == set([x11])
    assert Bvisitx12 == set([x12])
