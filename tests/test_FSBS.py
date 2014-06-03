from __future__ import absolute_import

from hypergraph.directedHyperGraph import DirectedHyperGraph
from hypergraph.hyperedge import DirectedHyperEdge
import copy


def test_FSBS():
    '''
        Test FS and BS functions
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

    e1 = DirectedHyperEdge(set([x3]), set([x1]), 1)
    e2 = DirectedHyperEdge(set([x4]), set([x1, x2]), 1)
    e3 = DirectedHyperEdge(set([x5]), set([x2]), 1)
    e4 = DirectedHyperEdge(set([x6]), set([x2]), 1)
    e5 = DirectedHyperEdge(set([x10]), set([x2, x8]), 1)
    e6 = DirectedHyperEdge(set([x8]), set([x5, x6]), 1)
    e7 = DirectedHyperEdge(set([x9]), set([x4, x8]), 1)
    e8 = DirectedHyperEdge(set([x1]), set([x10]), 1)
    e9 = DirectedHyperEdge(set([x7]), set([x3]), 1)
    e10 = DirectedHyperEdge(set([x12]), set([x1, x7, x11]), 1)

    BFSx1 = graph.FS(x1)
    BBSx1 = graph.BS(x1)
    BFSx2 = graph.FS(x2)
    BBSx2 = graph.BS(x2)
    BFSx3 = graph.FS(x3)
    BBSx3 = graph.BS(x3)
    BFSx4 = graph.FS(x4)
    BBSx4 = graph.BS(x4)
    BFSx5 = graph.FS(x5)
    BBSx5 = graph.BS(x5)
    BFSx6 = graph.FS(x6)
    BBSx6 = graph.BS(x6)
    BFSx7 = graph.FS(x7)
    BBSx7 = graph.BS(x7)
    BFSx8 = graph.FS(x8)
    BBSx8 = graph.BS(x8)
    BFSx9 = graph.FS(x9)
    BBSx9 = graph.BS(x9)
    BFSx10 = graph.FS(x10)
    BBSx10 = graph.BS(x10)
    BFSx11 = graph.FS(x11)
    BBSx11 = graph.BS(x11)
    BFSx12 = graph.FS(x12)
    BBSx12 = graph.BS(x12)

    assert BFSx1 == set([e1, e2, e10])
    assert BBSx1 == set([e8])
    assert BFSx2 == set([e2, e3, e4, e5])
    assert BBSx2 == set()
    assert BFSx3 == set([e9])
    assert BBSx3 == set([e1])
    assert BFSx4 == set([e7])
    assert BBSx4 == set([e2])
    assert BFSx5 == set([e6])
    assert BBSx5 == set([e3])
    assert BFSx6 == set([e6])
    assert BBSx6 == set([e4])
    assert BFSx7 == set([e10])
    assert BBSx7 == set([e9])
    assert BFSx8 == set([e5, e7])
    assert BBSx8 == set([e6])
    assert BFSx9 == set()
    assert BBSx9 == set([e7])
    assert BFSx10 == set([e8])
    assert BBSx10 == set([e5])
    assert BFSx11 == set([e10])
    assert BBSx11 == set()
    assert BFSx12 == set()
    assert BBSx12 == set([e10])
