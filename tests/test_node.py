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
    assert node1 == node

    # Test __str__
    assert str(node1) == "<Node name=bob nodeId=1>"
    assert repr(node1) == "<Node name=bob nodeId=1>"
