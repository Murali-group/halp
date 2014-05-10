from __future__ import absolute_import

from hypergraph.directedHyperGraph import DirectedBHyperGraph
from hypergraph.hyperedge import DirectedHyperEdge

def test_get_spanning_hypertree():
    '''
        Test reading directed hypergraphs from files,
        and determining its spanning hypertree
    '''
    # read directed hypergraph
    graph = DirectedBHyperGraph(set(), set())
    graph.read('tests/data/dirhypergraph_spanning.txt')
    x1 = graph.get_node_by_name('x1')
    x2 = graph.get_node_by_name('x2')
    x3 = graph.get_node_by_name('x3')
    x4 = graph.get_node_by_name('x4')
    x5 = graph.get_node_by_name('x5')
    x6 = graph.get_node_by_name('x6')
    e1 = DirectedHyperEdge(set([x2]), set([x1]))
    e2 = DirectedHyperEdge(set([x1]), set([x3]))
    e3 = DirectedHyperEdge(set([x1]), set([x2,x4]))
    e4 = DirectedHyperEdge(set([x5]), set([x2,x4]))
    e5 = DirectedHyperEdge(set([x2]), set([x4]))
    e6 = DirectedHyperEdge(set([x3]), set([x4]))
    e7 = DirectedHyperEdge(set([x5]), set([x4]))
    e8 = DirectedHyperEdge(set([x6]), set([x4]))
    e9 = DirectedHyperEdge(set([x6]), set([x3]))
    e10 = DirectedHyperEdge(set([x4]), set([x5,x6]))
    root = set([x5, x6])
    nonroot = set([x1, x2, x3, x4])
    ordering = graph.get_spanning_hypertree()
    #print ordering
    assert ordering[0] == root
    assert ordering[1] == e10
    assert ordering[2] == x4
    assert ordering[3] == e4
    assert ordering[4] == x2
    assert ordering[5] == e3
    assert ordering[6] == x1
    assert ordering[7] == e6
    assert ordering[8] == x3