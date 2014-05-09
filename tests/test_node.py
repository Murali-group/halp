from __future__ import absolute_import

from hypergraph.node import Node


def test_node():
    '''
        Tests the base node class.
    '''

    # Test defailt node values
    node = Node()
    assert node.name == ""
    assert node.nodeId == -1

    # Test node non defaults
    node = Node(name="bob", nodeId=1)
    assert node.name == "bob"
    assert node.nodeId == 1

    # Test copy
    node1 = node.copy()
    node2 = node
    assert not (node1 is node)
    assert node2 is node

    # Test __str__
    assert str(node1) == "bob"
    assert repr(node1) == "bob"

    # Test __eq__
    node1 = Node(name="s", nodeId=1)
    node2 = Node(name="s", nodeId=1)
    node3 = Node(name="t", nodeId=1)
    assert node1 == node2
    assert node1 != node3
