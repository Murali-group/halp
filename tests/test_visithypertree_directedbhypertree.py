from __future__ import absolute_import

from hypergraph.directedHyperGraph import DirectedBHyperTree
from hypergraph.hyperedge import DirectedHyperEdge


def test_read_dirbhypertree():
    '''
        Test reading directed hypergraphs from files,
        and add edges with and without weights.
    '''
    # read directed hypergraph
    graph = DirectedBHyperTree(set(), set(), set())
    graph.read('tests/data/dirbhypertree.txt')
    x1 = graph.get_node_by_name('x1')
    x2 = graph.get_node_by_name('x2')
    x3 = graph.get_node_by_name('x3')
    x4 = graph.get_node_by_name('x4')
    x5 = graph.get_node_by_name('x5')
    x6 = graph.get_node_by_name('x6')
    e10 = DirectedHyperEdge(set([x4]),set([x5,x6]))
    e4 = DirectedHyperEdge(set([x2]),set([x4,x5]))
    e3 = DirectedHyperEdge(set([x1]),set([x2,x4]))
    e6 = DirectedHyperEdge(set([x3]),set([x1,x4]))
    root = set([x5, x6])
    nonroot = set([x1, x2, x3, x4])
    assert root ==  graph.rootNodes
    assert nonroot ==  graph.nonRootNodes
    ordering = graph.visitHyperTree()
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

