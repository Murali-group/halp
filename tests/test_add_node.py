from __future__ import absolute_import

from hypergraph.node import Node
from hypergraph.undirectedHyperGraph import UndirectedHyperGraph


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

    # Test duplicate node name (by name)
    try:
        graph.add_node('x2')
    except Exception:
        pass
    else:
        raise Exception(
            'add_node should raise Exception, but it did not')

    # Test duplicate node name (by object)
    try:
        graph.add_node(Node('x2'))
        graph.__add_node_by_object('x2')
    except Exception:
        pass
    else:
        raise Exception(
            'add_node should raise Exception, but it did not')

    # Test duplicate node name (by object)
    try:
        graph._HyperGraph__add_node_by_object('x2')
    except Exception:
        pass
    else:
        raise Exception(
            '__add_node_by_object should raise Exception, but it did not')


    # Test wrong input type
    try:
        graph.add_node(set())
    except ValueError:
        pass
    else:
        raise Exception(
            'add_node should raise ValueError exception, but it did not')
