from __future__ import absolute_import

from hypergraph.directedHyperGraph import DirectedBHyperGraph
from hypergraph.hyperedge import DirectedBHyperEdge


def test_flow_directedbhypergraph():
    '''
        Test reading directed b hypertrees from files,
        and testing visit functionality
    '''
    # read directed hypergraph
    graph = DirectedBHyperGraph(set(), set())
    graph.read('tests/data/flow_dirbhypergraph.txt')
    x1 = graph.get_node_by_name('x1')
    x2 = graph.get_node_by_name('x2')
    x3 = graph.get_node_by_name('x3')
    x4 = graph.get_node_by_name('x4')
    e1 = DirectedBHyperEdge(set([x2]), set([x1]), 1.0)
    e2 = DirectedBHyperEdge(set([x1]), set([x3]), 4.0)
    e3 = DirectedBHyperEdge(set([x1]), set([x2, x4]), 7.0)
    e4 = DirectedBHyperEdge(set([x3]), set([x4]), 5.0)
    e5 = DirectedBHyperEdge(set([x2]), set([x4]), 0.5)
    root = set([x1])
    ordering = [root, e2, x3, e4, x4, e3, x2]
    potential = {}
    potential[x1] = 3.0
    cost = {}
    cost[e2] = 7.0
    cost[e3] = 5.0
    cost[e4] = 9.0

    cost2, potential2 = graph.potential(ordering, cost, potential)
    assert potential2[x1] == 3
    assert potential2[x2] == 12.0 / 7
    assert potential2[x3] == -1
    assert potential2[x4] == -2
    assert cost2[e1] == -9.0 / 7
    assert cost2[e2] == 4
    assert cost2[e3] == -12
    assert cost2[e4] == 10
    assert cost2[e5] == 19.0 / 7
