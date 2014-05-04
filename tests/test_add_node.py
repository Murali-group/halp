from __future__ import absolute_import

from hypergraph.node import Node
from hypergraph.undirectedHyperGraph import UndirectedHyperGraph
from hypergraph.hypergraph import HyperGraph


def test_addNodeToHypergraph():
    '''
        Test adding nodes to a graph either by name or by object.
    '''
    # create hypergraph
    graph = UndirectedHyperGraph(set())

    # add  node by name
    graph.add_node('x1')
    assert graph.get_node_by_name('x1') is not None

    # add  node by Node object
    n = Node('x2')
    graph.add_node(n)
    assert graph.get_node_by_name('x2') is not None

    # Test wrong input
    try:
        graph.add_node(set())
    except ValueError:
        pass
    else:
        raise Exception(
            'add_node should raise ValueError exception, but it did not')