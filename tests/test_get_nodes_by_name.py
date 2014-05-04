from __future__ import absolute_import

from hypergraph.undirectedHyperGraph import UndirectedHyperGraph
from hypergraph.node import Node

def test_get_node_names():
    '''
        Test adding nodes to a graph either by name or by object.
    '''
    # create hypergraph
    graph = UndirectedHyperGraph(set())

    # add  node by name
    n1 = Node('x1')
    n2 = Node('x2')
    n3 = Node('x3')

    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_node(n3)

    assert len(graph.get_nodes_by_name(['x1', 'x2'])) == 2
    assert n1 in graph.get_nodes_by_name(['x1', 'x2'])
    assert n2 in graph.get_nodes_by_name(['x1', 'x2'])
    assert n3 not in graph.get_nodes_by_name(['x1', 'x2'])
