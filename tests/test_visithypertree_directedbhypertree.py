from __future__ import absolute_import

from hypergraph.directedHyperGraph import DirectedBHyperTree


def test_read_dirbhypertree():
    '''
        Test reading directed hypergraphs from files,
        and add edges with and without weights.
    '''
    # read directed hypergraph
    graph = DirectedBHyperTree(set(), set(), set())
    graph.read('tests/data/dirbhypertree.txt')

    x5 = graph.get_node_by_name('x5')
    x6 = graph.get_node_by_name('x6')

    assert x5, x6 in graph.rootNodes
    assert x5, x6 not in graph.nonRootNodes




