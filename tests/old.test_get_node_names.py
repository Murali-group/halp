from __future__ import absolute_import

from hypergraph.undirectedHyperGraph import UndirectedHyperGraph


def test_get_node_names():
    '''
        Test adding nodes to a graph either by name or by object.
    '''
    # create hypergraph
    graph = UndirectedHyperGraph(set())

    # add  node by name
    graph.add_node('x1')
    graph.add_node('x2')

    assert len(graph.get_node_names()) == 2
    assert 'x1' in graph.get_node_names()
    assert 'x2' in graph.get_node_names()
