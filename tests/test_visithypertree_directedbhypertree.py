from __future__ import absolute_import

from hypergraph.directedHyperGraph import DirectedBHyperTree
from hypergraph.hyperedge import HyperEdge


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
    root = set([x5, x6])
    nonroot = set([x1, x2, x3, x4])
    assert root ==  graph.rootNodes
    assert nonroot ==  graph.nonRootNodes
    ordering = graph.visitHyperTree()

    assert ordering[0] == root




