from __future__ import absolute_import

from hypergraph.directedHyperGraph import DirectedHyperGraph

from operator import attrgetter


def test_node_ordering():
    d = DirectedHyperGraph(set(), set())
    d.add_node('x2')
    d.add_node('x4')
    d.add_node('x1')
    d.add_node('x3')
    d.add_node('x0')

    d.node_ordering = attrgetter('name')
    assert list(map(attrgetter('name'), d.nodes)) == ['x0', 'x1', 'x2', 'x3', 'x4']
