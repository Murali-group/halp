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
    e1 = DirectedHyperEdge(set([x2]), set([x1]))
    e2 = DirectedHyperEdge(set([x4]), set([x1,x2]))
    e3 = DirectedHyperEdge(set([x4]), set([x1,x3]))
    root1 = set([x1])
    root2 = set([x2])
    ordering = graph.get_spanning_hypertree()
    if ordering[0] == root1:
        assert ordering[1] == e1
        assert ordering[2] == x2
        assert ordering[3] == e2
        assert ordering[4] == x4
        assert ordering[5] == e3
        assert ordering[6] == x3
    elif ordering[0] == root2:
        assert ordering[1] == e1
        assert ordering[2] == x1
        assert ordering[3] == e2
        assert ordering[4] == x4
        assert ordering[5] == e3
        assert ordering[6] == x3
    else:
        assert False


