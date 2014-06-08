from __future__ import absolute_import

from hypergraph.node import Node


def test_node():
    '''
        Tests the base node class.
    '''

    # Test defailt node values
    node = Node()
    assert node.name == ""

    # Test node non defaults
    node = Node(name="bob")
    assert node.name == "bob"

    # Test copy
    node1 = node.copy()
    node2 = node
    assert not (node1 is node)
    assert node2 is node

    # Test __eq__
    node1 = Node(name="s")
    node2 = Node(name="s")
    node3 = Node(name="t")
    assert node1 == node2
    assert node1 != node3

    # Test __str__
    assert str(node1) == "<Node name=s>"
    assert repr(node1) == "<Node name=s>"
