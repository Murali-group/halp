from os import remove

from halp.directed_hypergraph import DirectedHypergraph


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

    node_set = H.get_node_set()
    assert node_set == set(['A', 'B', 'C', 'D'])
    assert len(node_set) == len(node_list)
    for node in H.node_iterator():
        assert node in node_set


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


def test_get_hyperedge_attributes():
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

    assert H.get_hyperedge_attributes(hyperedge_name) == \
        {'tail': tail, 'head': head, 'weight': 5, 'color': 'black'}

    # Test getting non-existent hyperedge's attributes
    try:
        H.get_hyperedge_attributes("e10")
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

    assert set(hyperedge_names) == H.get_hyperedge_id_set()
    for hyperedge_id in H.hyperedge_id_iterator():
        assert hyperedge_id in hyperedge_names


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
    assert frozen_head1 not in H._predecessors
    assert frozen_head2 not in H._predecessors
    assert frozen_tail2 not in H._successors

    # Test that everything that wasn't supposed to be removed wasn't removed
    assert "e3" in H._hyperedge_attributes
    assert frozen_tail3 in H._successors
    assert frozen_head3 in H._predecessors

    # Remove another node
    H.remove_node(node_e)
    assert node_e not in H._node_attributes
    assert node_e not in H._forward_star
    assert node_e not in H._backward_star
    assert "e3" not in H._hyperedge_attributes
    assert frozen_head3 not in H._predecessors
    assert frozen_tail3 not in H._successors

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

    tail4 = set([node_c])
    head4 = set([node_e])
    frozen_tail4 = frozenset(tail4)
    frozen_head4 = frozenset(head4)

    attrib = {'weight': 6, 'color': 'black'}
    common_attrib = {'sink': False}

    hyperedges = [(tail1, head1, attrib),
                  (tail2, head2),
                  (tail3, head3),
                  (tail4, head4)]

    H = DirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')
    H.remove_nodes([node_a, node_d])

    # Test that everything that needed to be removed was removed
    assert node_a not in H._node_attributes
    assert node_a not in H._forward_star
    assert node_a not in H._backward_star
    assert "e1" not in H._hyperedge_attributes
    assert "e2" not in H._hyperedge_attributes
    assert frozen_tail1 not in H._successors
    assert frozen_head1 not in H._predecessors
    assert frozen_head2 not in H._predecessors
    assert frozen_tail2 not in H._successors

    assert node_d not in H._node_attributes
    assert node_d not in H._forward_star
    assert node_d not in H._backward_star
    assert "e3" not in H._hyperedge_attributes
    assert "e3" not in H._predecessors[frozen_head3]
    assert frozen_tail3 not in H._predecessors[frozen_head3]


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
    assert frozen_tail1 not in H._successors
    assert frozen_head1 not in H._predecessors
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
    assert frozen_tail1 not in H._successors
    assert frozen_head1 not in H._predecessors
    assert 'e1' not in H._forward_star[node_a]
    assert 'e1' not in H._forward_star[node_b]
    assert 'e1' not in H._backward_star[node_c]
    assert 'e1' not in H._backward_star[node_d]

    assert 'e3' not in H._hyperedge_attributes
    assert frozen_tail3 not in H._successors
    assert frozen_head3 not in H._predecessors
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


def test_get_node_attributes():
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

    assert H.get_node_attributes(node_a) == {}
    assert H.get_node_attributes(node_d) == {'label': 'black', 'sink': False}

    # Test getting non-existent node's attributes
    try:
        H.get_node_attributes("X")
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


def test_copy():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    attrib_c = {'alt_name': 1337}
    common_attrib = {'common': True, 'source': False}

    node_list = [node_a, (node_b, {'source': True}), (node_c, attrib_c)]

    node_d = 'D'

    H = DirectedHypergraph()
    H.add_nodes(node_list, common_attrib)

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

    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    new_H = H.copy()

    assert new_H._node_attributes == H._node_attributes
    assert new_H._hyperedge_attributes == H._hyperedge_attributes

    assert new_H._backward_star == H._backward_star
    assert new_H._forward_star == H._forward_star

    assert new_H._successors == H._successors
    assert new_H._predecessors == H._predecessors


def test_read_and_write():
    # Try writing the following hypergraph to a file
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    attrib_c = {'alt_name': 1337}
    common_attrib = {'common': True, 'source': False}

    node_list = [node_a, (node_b, {'source': True}), (node_c, attrib_c)]

    node_d = 'D'

    H = DirectedHypergraph()
    H.add_nodes(node_list, common_attrib)

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

    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    H.write("test_directed_read_and_write.txt")

    # Try reading the hypergraph that was just written into a new hypergraph
    new_H = DirectedHypergraph()
    new_H.read("test_directed_read_and_write.txt")

    assert H._node_attributes.keys() == new_H._node_attributes.keys()

    for new_hyperedge_id in new_H.get_hyperedge_id_set():
        new_hyperedge_tail = new_H.get_hyperedge_tail(new_hyperedge_id)
        new_hyperedge_head = new_H.get_hyperedge_head(new_hyperedge_id)
        new_hyperedge_weight = new_H.get_hyperedge_weight(new_hyperedge_id)

        found_matching_hyperedge = False
        for hyperedge_id in H.get_hyperedge_id_set():
            hyperedge_tail = H.get_hyperedge_tail(hyperedge_id)
            hyperedge_head = H.get_hyperedge_head(hyperedge_id)
            hyperedge_weight = H.get_hyperedge_weight(hyperedge_id)

            if new_hyperedge_tail == hyperedge_tail and \
               new_hyperedge_head == hyperedge_head and \
               new_hyperedge_weight == hyperedge_weight:
                found_matching_hyperedge = True
                continue

        assert found_matching_hyperedge

    remove("test_directed_read_and_write.txt")

    # Try reading an invalid hypergraph file
    invalid_H = DirectedHypergraph()
    try:
        invalid_H.read("tests/data/invalid_directed_hypergraph.txt")
        assert False
    except IOError:
        pass
    except BaseException as e:
        assert False, e


def test_check_hyperedge_attributes_consistency():
    # make test hypergraph
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    attrib_c = {'alt_name': 1337}
    common_attrib = {'common': True, 'source': False}

    node_list = [node_a, (node_b, {'source': True}), (node_c, attrib_c)]

    node_d = 'D'

    H = DirectedHypergraph()
    H.add_nodes(node_list, common_attrib)

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

    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    # This should not fail
    H._check_consistency()

    # The following consistency checks should fail
    # Check 1.1
    new_H = H.copy()
    del new_H._hyperedge_attributes["e1"]["weight"]
    try:
        new_H._check_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 1.2
    new_H = H.copy()
    new_H._hyperedge_attributes["e1"]["tail"] = head1
    try:
        new_H._check_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 1.3
    new_H = H.copy()
    new_H._hyperedge_attributes["e1"]["head"] = tail1
    try:
        new_H._check_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 1.4
    new_H = H.copy()
    del new_H._successors[frozen_tail1]
    try:
        new_H._check_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 1.5
    new_H = H.copy()
    del new_H._predecessors[frozen_head1]
    try:
        new_H._check_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 1.6
    new_H = H.copy()
    new_H._forward_star["A"].pop()
    try:
        new_H._check_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 1.7
    new_H = H.copy()
    new_H._backward_star["C"].pop()
    try:
        new_H._check_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e


def test_check_node_attributes_consistency():
    # make test hypergraph
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    attrib_c = {'alt_name': 1337}
    common_attrib = {'common': True, 'source': False}

    node_list = [node_a, (node_b, {'source': True}), (node_c, attrib_c)]

    node_d = 'D'

    H = DirectedHypergraph()
    H.add_nodes(node_list, common_attrib)

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

    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    # This should not fail
    H._check_consistency()

    # Check 2.1
    new_H = H.copy()
    new_H._node_attributes["E"] = {}
    try:
        new_H._check_node_attributes_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 2.2
    new_H = H.copy()
    new_H._node_attributes["E"] = {}
    new_H._forward_star["E"] = set()
    try:
        new_H._check_node_attributes_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 2.3
    new_H = H.copy()
    new_H._forward_star["A"].add("e10")
    try:
        new_H._check_node_attributes_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 2.4
    new_H = H.copy()
    new_H._backward_star["A"].add("e10")
    try:
        new_H._check_node_attributes_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e


def test_check_predecessor_successor_consistency():
    # make test hypergraph
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    attrib_c = {'alt_name': 1337}
    common_attrib = {'common': True, 'source': False}

    node_list = [node_a, (node_b, {'source': True}), (node_c, attrib_c)]

    node_d = 'D'

    H = DirectedHypergraph()
    H.add_nodes(node_list, common_attrib)

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

    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    # This should not fail
    H._check_consistency()

    # Check 3.1
    new_H = H.copy()
    new_H._predecessors[frozenset(["X"])] = {}
    try:
        new_H._check_predecessor_successor_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 3.2
    new_H = H.copy()
    new_H._successors[frozenset(["X"])] = {}
    try:
        new_H._check_predecessor_successor_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 3.3
    new_H = H.copy()
    new_frozentail = frozenset("A")
    new_frozenhead = frozenset("C")
    new_H._successors[new_frozentail] = {}
    new_H._successors[new_frozentail][new_frozenhead] = "e1"
    new_H._predecessors[new_frozenhead] = {}
    new_H._predecessors[new_frozenhead][new_frozentail] = "e2"
    try:
        new_H._check_predecessor_successor_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e


def test_check_hyperedge_id_consistency():
    # make test hypergraph
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    attrib_c = {'alt_name': 1337}
    common_attrib = {'common': True, 'source': False}

    node_list = [node_a, (node_b, {'source': True}), (node_c, attrib_c)]

    node_d = 'D'

    H = DirectedHypergraph()
    H.add_nodes(node_list, common_attrib)

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

    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    # This should not fail
    H._check_consistency()

    # Check 4.1
    new_H = H.copy()
    new_H._forward_star["X"] = set("e0")
    try:
        new_H._check_hyperedge_id_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 4.2
    new_H = H.copy()
    new_H._backward_star["X"] = set("e0")
    try:
        new_H._check_hyperedge_id_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 4.3
    new_H = H.copy()
    new_H._predecessors[frozen_head1][frozen_tail1] = "e0"
    try:
        new_H._check_hyperedge_id_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 4.4
    new_H = H.copy()
    new_H._successors[frozen_tail1][frozen_head1] = "e0"
    try:
        new_H._check_hyperedge_id_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e


def test_check_node_consistency():
    # make test hypergraph
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    attrib_c = {'alt_name': 1337}
    common_attrib = {'common': True, 'source': False}

    node_list = [node_a, (node_b, {'source': True}), (node_c, attrib_c)]

    node_d = 'D'

    H = DirectedHypergraph()
    H.add_nodes(node_list, common_attrib)

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

    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    # This should not fail
    H._check_consistency()

    # Check 5.1
    new_H = H.copy()
    new_H._forward_star["X"] = {}
    try:
        new_H._check_node_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 5.2
    new_H = H.copy()
    new_H._backward_star["X"] = {}
    try:
        new_H._check_node_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 5.3.1
    new_H = H.copy()
    new_H.add_hyperedge("X", "Y")
    del new_H._node_attributes["X"]
    del new_H._forward_star["X"]
    del new_H._forward_star["Y"]
    del new_H._backward_star["X"]
    del new_H._backward_star["Y"]
    try:
        new_H._check_node_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 5.3.2
    new_H = H.copy()
    new_H.add_hyperedge("X", "Y")
    del new_H._node_attributes["Y"]
    del new_H._forward_star["X"]
    del new_H._forward_star["Y"]
    del new_H._backward_star["X"]
    del new_H._backward_star["Y"]
    try:
        new_H._check_node_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 5.4
    new_H = H.copy()
    new_H._predecessors[frozenset("X")] = {}
    try:
        new_H._check_node_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Check 5.5
    new_H = H.copy()
    new_H._successors[frozenset("X")] = {}
    new_H._predecessors[frozenset("X")] = {}
    try:
        new_H._check_node_consistency()
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e


def test_get_symmetric_image():
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

    sym_H = H.get_symmetric_image()

    sym_H._check_consistency()

    assert sym_H._node_attributes == H._node_attributes

    assert sym_H._hyperedge_attributes["e1"]["tail"] == head1
    assert sym_H._hyperedge_attributes["e1"]["head"] == tail1
    assert sym_H._hyperedge_attributes["e1"]["__frozen_tail"] == frozen_head1
    assert sym_H._hyperedge_attributes["e1"]["__frozen_head"] == frozen_tail1
    assert sym_H._hyperedge_attributes["e2"]["tail"] == head2
    assert sym_H._hyperedge_attributes["e2"]["head"] == tail2
    assert sym_H._hyperedge_attributes["e2"]["__frozen_tail"] == frozen_head2
    assert sym_H._hyperedge_attributes["e2"]["__frozen_head"] == frozen_tail2
    assert sym_H._hyperedge_attributes["e3"]["tail"] == head3
    assert sym_H._hyperedge_attributes["e3"]["head"] == tail3
    assert sym_H._hyperedge_attributes["e3"]["__frozen_tail"] == frozen_head3
    assert sym_H._hyperedge_attributes["e3"]["__frozen_head"] == frozen_tail3

    assert sym_H._forward_star[node_a] == set(["e2"])
    assert sym_H._forward_star[node_b] == set()
    assert sym_H._forward_star[node_c] == set(["e1"])
    assert sym_H._forward_star[node_d] == set(["e1", "e2"])
    assert sym_H._forward_star[node_e] == set(["e3"])

    assert sym_H._backward_star[node_a] == set(["e1"])
    assert sym_H._backward_star[node_b] == set(["e1", "e2"])
    assert sym_H._backward_star[node_c] == set(["e2"])
    assert sym_H._backward_star[node_d] == set(["e3"])
    assert sym_H._backward_star[node_e] == set()


def test_get_induced_subhypergraph():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    induce_on_nodes = H.get_node_set() - {'t'}
    induced_H = H.get_induced_subhypergraph(induce_on_nodes)

    induced_nodes = induced_H.get_node_set()
    assert induced_nodes == H.get_node_set() - {'t'}

    hyperedges = [(induced_H.get_hyperedge_tail(hyperedge_id),
                   induced_H.get_hyperedge_head(hyperedge_id))
                  for hyperedge_id in induced_H.get_hyperedge_id_set()]
    for hyperedge in hyperedges:
        tail, head = hyperedge
        assert set(tail) - induce_on_nodes == set()
        assert set(head) - induce_on_nodes == set()
        assert H.has_hyperedge(tail, head)


def test_is_B_hypergraph():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert not H.is_B_hypergraph()

    H = DirectedHypergraph()
    H.add_hyperedge(['a', 'b'], ['c'])
    assert H.is_B_hypergraph()

    H = DirectedHypergraph()
    H.add_hyperedge(['x'], ['y', 'z'])
    assert not H.is_B_hypergraph()

    H = DirectedHypergraph()
    H.add_hyperedge(['a', 'b'], ['c'])
    H.add_hyperedge(['x'], ['y', 'z'])
    assert not H.is_B_hypergraph()


def test_is_F_hypergraph():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert not H.is_F_hypergraph()

    H = DirectedHypergraph()
    H.add_hyperedge(['a', 'b'], ['c'])
    assert not H.is_F_hypergraph()

    H = DirectedHypergraph()
    H.add_hyperedge(['x'], ['y', 'z'])
    assert H.is_F_hypergraph()

    H = DirectedHypergraph()
    H.add_hyperedge(['a', 'b'], ['c'])
    H.add_hyperedge(['x'], ['y', 'z'])
    assert not H.is_F_hypergraph()


def test_is_BF_hypergraph():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert not H.is_BF_hypergraph()

    H = DirectedHypergraph()
    H.add_hyperedge(['a', 'b'], ['c'])
    assert H.is_BF_hypergraph()

    H = DirectedHypergraph()
    H.add_hyperedge(['x'], ['y', 'z'])
    assert H.is_BF_hypergraph()

    H = DirectedHypergraph()
    H.add_hyperedge(['a', 'b'], ['c'])
    H.add_hyperedge(['x'], ['y', 'z'])
    assert H.is_BF_hypergraph()
