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
    e1 = DirectedBHyperEdge(set([x2]),set([x1]),1.0)
    e2 = DirectedBHyperEdge(set([x1]),set([x3]),4.0)
    e3 = DirectedBHyperEdge(set([x1]),set([x2,x4]),7.0)
    e4 = DirectedBHyperEdge(set([x3]),set([x4]),5.0)
    e5 = DirectedBHyperEdge(set([x2]),set([x4]),0.5)
    root = set([x1])
    ordering = [root,e2,x3,e4,x4,e3,x2]
    flow = {}
    flow[e1] = 3
    flow[e5] = 5
    demand = {}
    demand[x2] = 4
    demand[x3] = 7
    demand[x4] = 1

    demand2, flow2 = graph.flow(ordering, demand, flow)
    print demand2, flow2

