from __future__ import absolute_import

from hypergraph.directed_hypergraph import DirectedHypergraph


def test_add_node():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    attrib_c = {'alt_name': 1337}
    node_d = 'D'
    attrib_d = {'label': 'black', 'sink': True}

    # Test adding unadded nodes with various attribute settings
    H = DirectedHypergraph()
    H.add_node(node_a)
    H.add_node(node_b, source=True)
    H.add_node(node_c, attrib_c)
    H.add_node(node_d, attrib_d, sink=False)

    assert node_a in H._node_attributes
    assert H._node_attributes[node_a] == {}

    assert node_b in H._node_attributes
    assert H._node_attributes[node_b]['source'] is True

    assert node_c in H._node_attributes
    assert H._node_attributes[node_c]['alt_name'] == 1337

    assert node_d in H._node_attributes
    assert H._node_attributes[node_d]['label'] == 'black'
    assert H._node_attributes[node_d]['sink'] is False

    # Test adding a node that has already been added
    H.add_nodes(node_a, common=False)
    assert H._node_attributes[node_a]['common'] is False

    # Pass in bad (non-dict) attribute
    try:
        H.add_node(node_a, ["label", "black"])
        assert False
    except AttributeError:
        pass
    except BaseException as e:
        assert False, e


def test_add_nodes():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    attrib_c = {'alt_name': 1337}
    node_d = 'D'
    attrib_d = {'label': 'black', 'sink': True}
    common_attrib = {'common': True, 'source': False}

    node_list = [node_a, (node_b, {'source': False}),
                 (node_c, attrib_c), (node_d, attrib_d)]

    # Test adding unadded nodes with various attribute settings
    H = DirectedHypergraph()
    H.add_nodes(node_list, common_attrib)

    assert node_a in H._node_attributes
    assert H._node_attributes[node_a] == common_attrib

    assert node_b in H._node_attributes
    assert H._node_attributes[node_b]['source'] is False

    assert node_c in H._node_attributes
    assert H._node_attributes[node_c]['alt_name'] == 1337

    assert node_d in H._node_attributes
    assert H._node_attributes[node_d]['label'] == 'black'
    assert H._node_attributes[node_d]['sink'] is True


def test_add_hyperedge():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'

    tail = set([node_a, node_b])
    head = set([node_c, node_d])
    frozen_tail = frozenset(tail)
    frozen_head = frozenset(head)

    attrib = {'weight': 6, 'color': 'black'}

    H = DirectedHypergraph()
    H.add_node(node_a, label=1337)
    hyperedge_name = H.add_hyperedge(tail, head, attrib, weight=5)

    assert hyperedge_name == 'e1'

    # Test that all hyperedge attributes are correct
    assert H._hyperedge_attributes[hyperedge_name]['tail'] == tail
    assert H._hyperedge_attributes[hyperedge_name]['head'] == head
    assert H._hyperedge_attributes[hyperedge_name]['weight'] == 5
    assert H._hyperedge_attributes[hyperedge_name]['color'] == 'black'

    # Test that successor list contains the correct info
    assert frozen_head in H._successors[frozen_tail]
    assert hyperedge_name in H._successors[frozen_tail][frozen_head]

    # Test that the precessor list contains the correct info
    assert frozen_tail in H._predecessors[frozen_head]
    assert hyperedge_name in H._predecessors[frozen_head][frozen_tail]

    # Test that forward-stars and backward-stars contain the correct info
    for node in frozen_tail:
        assert hyperedge_name in H._forward_star[node]
    for node in frozen_head:
        assert hyperedge_name in H._backward_star[node]

    # Test that adding same hyperedge will only update attributes
    new_attrib = {'weight': 10}
    H.add_hyperedge(tail, head, new_attrib)
    assert H._hyperedge_attributes[hyperedge_name]['weight'] == 10
    assert H._hyperedge_attributes[hyperedge_name]['color'] == 'black'

    try:
        H.add_hyperedge(set(), set())
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e


def test_add_hyperedges():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'

    tail1 = set([node_a, node_b])
    head1 = set([node_c, node_d])
    frozen_tail1 = frozenset(tail1)
    frozen_head1 = frozenset(head1)

    tail2 = set([node_b, node_c])
    head2 = set([node_d, node_a])
    frozen_tail2 = frozenset(tail2)
    frozen_head2 = frozenset(head2)

    attrib = {'weight': 6, 'color': 'black'}
    common_attrib = {'sink': False}

    hyperedges = [(tail1, head1, attrib), (tail2, head2)]

    H = DirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    assert 'e1' in hyperedge_names
    assert 'e2' in hyperedge_names

    assert H._hyperedge_attributes['e1']['tail'] == tail1
    assert H._hyperedge_attributes['e1']['head'] == head1
    assert H._hyperedge_attributes['e1']['weight'] == 6
    assert H._hyperedge_attributes['e1']['color'] == 'black'
    assert H._hyperedge_attributes['e1']['sink'] is False

    assert H._hyperedge_attributes['e2']['tail'] == tail2
    assert H._hyperedge_attributes['e2']['head'] == head2
    assert H._hyperedge_attributes['e2']['weight'] == 1
    assert H._hyperedge_attributes['e2']['color'] == 'white'
    assert H._hyperedge_attributes['e2']['sink'] is False


def test_remove_node():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    tail1 = set([node_a, node_b])
    head1 = set([node_c, node_d])
    frozen_tail1 = frozenset(tail1)
    frozen_head1 = frozenset(head1)

    tail2 = set([node_b, node_c])
    head2 = set([node_d, node_a])
    frozen_tail2 = frozenset(tail2)
    frozen_head2 = frozenset(head2)

    tail3 = set([node_d])
    head3 = set([node_e])
    frozen_tail3 = frozenset(tail3)
    frozen_head3 = frozenset(head3)

    attrib = {'weight': 6, 'color': 'black'}
    common_attrib = {'sink': False}

    hyperedges = [(tail1, head1, attrib), (tail2, head2), (tail3, head3)]

    H = DirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')
    H.remove_node(node_a)

    # Test that everything that needed to be removed was removed
    assert node_a not in H._node_attributes
    assert node_a not in H._forward_star
    assert node_a not in H._backward_star
    assert "e1" not in H._hyperedge_attributes
    assert "e2" not in H._hyperedge_attributes
    assert frozen_tail1 not in H._successors
    assert frozen_tail1 not in H._predecessors[frozen_head1]
    assert frozen_head2 not in H._predecessors
    assert frozen_head2 not in H._successors[frozen_tail2]

    # Test that everything that wasn't supposed to be removed wasn't removed
    assert "e3" in H._hyperedge_attributes
    assert frozen_tail3 in H._successors
    assert frozen_head3 in H._predecessors

    try:
        H.remove_node(node_a)
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e


def test_remove_nodes():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    tail1 = set([node_a, node_b])
    head1 = set([node_c, node_d])
    frozen_tail1 = frozenset(tail1)
    frozen_head1 = frozenset(head1)

    tail2 = set([node_b, node_c])
    head2 = set([node_d, node_a])
    frozen_tail2 = frozenset(tail2)
    frozen_head2 = frozenset(head2)

    tail3 = set([node_d])
    head3 = set([node_e])
    frozen_tail3 = frozenset(tail3)
    frozen_head3 = frozenset(head3)

    attrib = {'weight': 6, 'color': 'black'}
    common_attrib = {'sink': False}

    hyperedges = [(tail1, head1, attrib), (tail2, head2), (tail3, head3)]

    H = DirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')
    H.remove_nodes([node_a, node_e])

    # Test that everything that needed to be removed was removed
    assert node_a not in H._node_attributes
    assert node_a not in H._forward_star
    assert node_a not in H._backward_star
    assert "e1" not in H._hyperedge_attributes
    assert "e2" not in H._hyperedge_attributes
    assert frozen_tail1 not in H._successors
    assert frozen_tail1 not in H._predecessors[frozen_head1]
    assert frozen_head2 not in H._predecessors
    assert frozen_head2 not in H._successors[frozen_tail2]

    assert node_e not in H._node_attributes
    assert node_e not in H._forward_star
    assert node_e not in H._backward_star
    assert "e3" not in H._hyperedge_attributes
    assert frozen_head3 not in H._predecessors
    assert frozen_head3 not in H._successors[frozen_tail3]


def test_remove_hyperedge():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    tail1 = set([node_a, node_b])
    head1 = set([node_c, node_d])
    frozen_tail1 = frozenset(tail1)
    frozen_head1 = frozenset(head1)

    tail2 = set([node_b, node_c])
    head2 = set([node_d, node_a])
    frozen_tail2 = frozenset(tail2)
    frozen_head2 = frozenset(head2)

    tail3 = set([node_d])
    head3 = set([node_e])
    frozen_tail3 = frozenset(tail3)
    frozen_head3 = frozenset(head3)

    attrib = {'weight': 6, 'color': 'black'}
    common_attrib = {'sink': False}

    hyperedges = [(tail1, head1, attrib), (tail2, head2), (tail3, head3)]

    H = DirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')
    H.remove_hyperedge('e1')

    assert 'e1' not in H._hyperedge_attributes
    assert 'e1' not in H._successors[frozen_tail1]
    assert 'e1' not in H._predecessors[frozen_head1]
    assert 'e1' not in H._forward_star[node_a]
    assert 'e1' not in H._forward_star[node_b]
    assert 'e1' not in H._backward_star[node_c]
    assert 'e1' not in H._backward_star[node_d]

    try:
        H.remove_hyperedge('e1')
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e


def test_remove_hyperedges():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    tail1 = set([node_a, node_b])
    head1 = set([node_c, node_d])
    frozen_tail1 = frozenset(tail1)
    frozen_head1 = frozenset(head1)

    tail2 = set([node_b, node_c])
    head2 = set([node_d, node_a])
    frozen_tail2 = frozenset(tail2)
    frozen_head2 = frozenset(head2)

    tail3 = set([node_d])
    head3 = set([node_e])
    frozen_tail3 = frozenset(tail3)
    frozen_head3 = frozenset(head3)

    attrib = {'weight': 6, 'color': 'black'}
    common_attrib = {'sink': False}

    hyperedges = [(tail1, head1, attrib), (tail2, head2), (tail3, head3)]

    H = DirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')
    H.remove_hyperedges(['e1', 'e3'])

    assert 'e1' not in H._hyperedge_attributes
    assert 'e1' not in H._successors[frozen_tail1]
    assert 'e1' not in H._predecessors[frozen_head1]
    assert 'e1' not in H._forward_star[node_a]
    assert 'e1' not in H._forward_star[node_b]
    assert 'e1' not in H._backward_star[node_c]
    assert 'e1' not in H._backward_star[node_d]

    assert 'e3' not in H._hyperedge_attributes
    assert 'e3' not in H._successors[frozen_tail3]
    assert 'e3' not in H._predecessors[frozen_head3]
    assert 'e3' not in H._forward_star[node_d]
    assert 'e3' not in H._backward_star[node_e]


def test_get_hyperedge_id():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    tail1 = set([node_a, node_b])
    head1 = set([node_c, node_d])
    frozen_tail1 = frozenset(tail1)
    frozen_head1 = frozenset(head1)

    tail2 = set([node_b, node_c])
    head2 = set([node_d, node_a])
    frozen_tail2 = frozenset(tail2)
    frozen_head2 = frozenset(head2)

    tail3 = set([node_d])
    head3 = set([node_e])
    frozen_tail3 = frozenset(tail3)
    frozen_head3 = frozenset(head3)

    attrib = {'weight': 6, 'color': 'black'}
    common_attrib = {'sink': False}

    hyperedges = [(tail1, head1, attrib), (tail2, head2), (tail3, head3)]

    H = DirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    assert H.get_hyperedge_id(tail1, head1) == 'e1'
    assert H.get_hyperedge_id(tail2, head2) == 'e2'
    assert H.get_hyperedge_id(tail3, head3) == 'e3'

    try:
        H.get_hyperedge_id(tail1, head2)
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e


def test_get_hyperedge_attribute():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'

    tail1 = set([node_a, node_b])
    head1 = set([node_c, node_d])
    frozen_tail1 = frozenset(tail1)
    frozen_head1 = frozenset(head1)

    tail2 = set([node_b, node_c])
    head2 = set([node_d, node_a])
    frozen_tail2 = frozenset(tail2)
    frozen_head2 = frozenset(head2)

    attrib = {'weight': 6, 'color': 'black'}
    common_attrib = {'sink': False}

    hyperedges = [(tail1, head1, attrib), (tail2, head2)]

    H = DirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    assert H.get_hyperedge_attribute('e1', 'weight') == 6
    assert H.get_hyperedge_attribute('e1', 'color') == 'black'
    assert H.get_hyperedge_attribute('e1', 'sink') is False

    # Try requesting an invalid hyperedge
    try:
        H.get_hyperedge_attribute('e5', 'weight')
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Try requesting an invalid attribute
    try:
        H.get_hyperedge_attribute('e1', 'source')
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e


def test_get_hyperedge_tail():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'

    tail1 = set([node_a, node_b])
    head1 = set([node_c, node_d])
    frozen_tail1 = frozenset(tail1)
    frozen_head1 = frozenset(head1)

    tail2 = set([node_b, node_c])
    head2 = set([node_d, node_a])
    frozen_tail2 = frozenset(tail2)
    frozen_head2 = frozenset(head2)

    attrib = {'weight': 6, 'color': 'black'}
    common_attrib = {'sink': False}

    hyperedges = [(tail1, head1, attrib), (tail2, head2)]

    H = DirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    retrieved_tail1 = H.get_hyperedge_tail('e1')
    retrieved_tail2 = H.get_hyperedge_tail('e2')
    assert retrieved_tail1 == tail1
    assert retrieved_tail2 == tail2


def test_get_hyperedge_head():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'

    tail1 = set([node_a, node_b])
    head1 = set([node_c, node_d])
    frozen_tail1 = frozenset(tail1)
    frozen_head1 = frozenset(head1)

    tail2 = set([node_b, node_c])
    head2 = set([node_d, node_a])
    frozen_tail2 = frozenset(tail2)
    frozen_head2 = frozenset(head2)

    attrib = {'weight': 6, 'color': 'black'}
    common_attrib = {'sink': False}

    hyperedges = [(tail1, head1, attrib), (tail2, head2)]

    H = DirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    retrieved_head1 = H.get_hyperedge_head('e1')
    retrieved_head2 = H.get_hyperedge_head('e2')
    assert retrieved_head1 == head1
    assert retrieved_head2 == head2


def test_get_hyperedge_weight():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'

    tail1 = set([node_a, node_b])
    head1 = set([node_c, node_d])
    frozen_tail1 = frozenset(tail1)
    frozen_head1 = frozenset(head1)

    tail2 = set([node_b, node_c])
    head2 = set([node_d, node_a])
    frozen_tail2 = frozenset(tail2)
    frozen_head2 = frozenset(head2)

    attrib = {'weight': 6, 'color': 'black'}
    common_attrib = {'sink': False}

    hyperedges = [(tail1, head1, attrib), (tail2, head2)]

    H = DirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    weight_e1 = H.get_hyperedge_weight('e1')
    weight_e2 = H.get_hyperedge_weight('e2')
    assert weight_e1 == 6
    assert weight_e2 == 1


def test_get_node_attribute():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    attrib_c = {'alt_name': 1337}
    common_attrib = {'common': True, 'source': False}

    node_list = [node_a, (node_b, {'source': True}), (node_c, attrib_c)]

    # Test adding unadded nodes with various attribute settings
    H = DirectedHypergraph()
    H.add_nodes(node_list, common_attrib)

    assert H.get_node_attribute(node_a, 'common') is True
    assert H.get_node_attribute(node_a, 'source') is False
    assert H.get_node_attribute(node_b, 'common') is True
    assert H.get_node_attribute(node_b, 'source') is True
    assert H.get_node_attribute(node_c, 'alt_name') == 1337

    # Try requesting an invalid node
    try:
        H.get_node_attribute("D", 'common')
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Try requesting an invalid attribute
    try:
        H.get_node_attribute(node_a, 'alt_name')
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e


def test_get_forward_star():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    tail1 = set([node_a, node_b])
    head1 = set([node_c, node_d])
    frozen_tail1 = frozenset(tail1)
    frozen_head1 = frozenset(head1)

    tail2 = set([node_b, node_c])
    head2 = set([node_d, node_a])
    frozen_tail2 = frozenset(tail2)
    frozen_head2 = frozenset(head2)

    tail3 = set([node_d])
    head3 = set([node_e])
    frozen_tail3 = frozenset(tail3)
    frozen_head3 = frozenset(head3)

    hyperedges = [(tail1, head1), (tail2, head2), (tail3, head3)]

    H = DirectedHypergraph()
    hyperedge_names = H.add_hyperedges(hyperedges)

    assert H.get_forward_star(node_a) == set(['e1'])
    assert H.get_forward_star(node_b) == set(['e1', 'e2'])
    assert H.get_forward_star(node_c) == set(['e2'])
    assert H.get_forward_star(node_d) == set(['e3'])
    assert H.get_forward_star(node_e) == set()

    # Try requesting an invalid node
    try:
        H.get_forward_star("F")
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e


def test_get_backward_star():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    tail1 = set([node_a, node_b])
    head1 = set([node_c, node_d])
    frozen_tail1 = frozenset(tail1)
    frozen_head1 = frozenset(head1)

    tail2 = set([node_b, node_c])
    head2 = set([node_d, node_a])
    frozen_tail2 = frozenset(tail2)
    frozen_head2 = frozenset(head2)

    tail3 = set([node_d])
    head3 = set([node_e])
    frozen_tail3 = frozenset(tail3)
    frozen_head3 = frozenset(head3)

    hyperedges = [(tail1, head1), (tail2, head2), (tail3, head3)]

    H = DirectedHypergraph()
    hyperedge_names = H.add_hyperedges(hyperedges)

    assert H.get_backward_star(node_a) == set(['e2'])
    assert H.get_backward_star(node_b) == set()
    assert H.get_backward_star(node_c) == set(['e1'])
    assert H.get_backward_star(node_d) == set(['e1', 'e2'])
    assert H.get_backward_star(node_e) == set(['e3'])

    # Try requesting an invalid node
    try:
        H.get_backward_star("F")
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e


def test_get_successors():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    tail1 = set([node_a, node_b])
    head1 = set([node_c, node_d])
    frozen_tail1 = frozenset(tail1)
    frozen_head1 = frozenset(head1)

    tail2 = set([node_b, node_c])
    head2 = set([node_d, node_a])
    frozen_tail2 = frozenset(tail2)
    frozen_head2 = frozenset(head2)

    tail3 = set([node_d])
    head3 = set([node_e])
    frozen_tail3 = frozenset(tail3)
    frozen_head3 = frozenset(head3)

    hyperedges = [(tail1, head1), (tail2, head2), (tail3, head3), (tail3, "F")]

    H = DirectedHypergraph()
    hyperedge_names = H.add_hyperedges(hyperedges)

    assert 'e1' in H.get_successors(tail1)
    assert 'e2' in H.get_successors(tail2)
    assert 'e3' in H.get_successors(tail3)
    assert 'e4' in H.get_successors(tail3)

    assert H.get_successors([node_a]) == set()


def test_get_predecessors():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    tail1 = set([node_a, node_b])
    head1 = set([node_c, node_d])
    frozen_tail1 = frozenset(tail1)
    frozen_head1 = frozenset(head1)

    tail2 = set([node_b, node_c])
    head2 = set([node_d, node_a])
    frozen_tail2 = frozenset(tail2)
    frozen_head2 = frozenset(head2)

    tail3 = set([node_d])
    head3 = set([node_e])
    frozen_tail3 = frozenset(tail3)
    frozen_head3 = frozenset(head3)

    hyperedges = [(tail1, head1), (tail2, head2), (tail3, head3), (tail3, "F")]

    H = DirectedHypergraph()
    hyperedge_names = H.add_hyperedges(hyperedges)

    assert 'e1' in H.get_predecessors(head1)
    assert 'e2' in H.get_predecessors(head2)
    assert 'e3' in H.get_predecessors(head3)
    assert 'e4' in H.get_predecessors("F")

    assert H.get_predecessors([node_a]) == set()
