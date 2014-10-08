from os import remove

from halp.undirected_hypergraph import UndirectedHypergraph


def test_add_node():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    attrib_c = {'alt_name': 1337}
    node_d = 'D'
    attrib_d = {'label': 'black', 'sink': True}

    # Test adding unadded nodes with various attribute settings
    H = UndirectedHypergraph()
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
    H = UndirectedHypergraph()
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

    nodes1 = set([node_a, node_b, node_c])
    frozen_nodes1 = frozenset(nodes1)

    attrib = {'weight': 6, 'color': 'black'}

    H = UndirectedHypergraph()
    H.add_node(node_a, label=1337)
    hyperedge_name = H.add_hyperedge(nodes1, attrib, weight=5)

    assert hyperedge_name == 'e1'

    # Test that all hyperedge attributes are correct
    assert H._hyperedge_attributes[hyperedge_name]['nodes'] == nodes1
    assert H._hyperedge_attributes[hyperedge_name]['__frozen_nodes'] == \
        frozen_nodes1
    assert H._hyperedge_attributes[hyperedge_name]['weight'] == 5
    assert H._hyperedge_attributes[hyperedge_name]['color'] == 'black'

    # Test that compose_hyperedge list contains the correct info
    assert frozen_nodes1 in H._node_set_to_hyperedge
    assert hyperedge_name == H._node_set_to_hyperedge[frozen_nodes1]

    # Test that the stars contain the correct info
    for node in frozen_nodes1:
        assert hyperedge_name in H._star[node]

    # Test that adding same hyperedge will only update attributes
    new_attrib = {'weight': 10}
    H.add_hyperedge(nodes1, new_attrib)
    assert H._hyperedge_attributes[hyperedge_name]['weight'] == 10
    assert H._hyperedge_attributes[hyperedge_name]['color'] == 'black'

    try:
        H.add_hyperedge(set())
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

    nodes1 = set([node_a, node_b, node_c])
    frozen_nodes1 = frozenset(nodes1)

    nodes2 = set([node_a, node_d])
    frozen_nodes2 = frozenset(nodes2)

    common_attrib = {'sink': False}

    hyperedges = [nodes1, nodes2]

    H = UndirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    assert 'e1' in hyperedge_names
    assert 'e2' in hyperedge_names

    assert H._hyperedge_attributes['e1']['nodes'] == nodes1
    assert H._hyperedge_attributes['e1']['weight'] == 1
    assert H._hyperedge_attributes['e1']['color'] == 'white'
    assert H._hyperedge_attributes['e1']['sink'] is False

    assert H._hyperedge_attributes['e2']['nodes'] == nodes2
    assert H._hyperedge_attributes['e2']['weight'] == 1
    assert H._hyperedge_attributes['e2']['color'] == 'white'
    assert H._hyperedge_attributes['e2']['sink'] is False

    assert set(hyperedge_names) == H.get_hyperedge_id_set()
    assert set(hyperedge_names) == H.get_hyperedge_id_set()
    for hyperedge_id in H.hyperedge_id_iterator():
        assert hyperedge_id in hyperedge_names


def test_remove_hyperedge():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    nodes1 = set([node_a, node_b, node_c])
    frozen_nodes1 = frozenset(nodes1)

    nodes2 = set([node_a, node_d])
    frozen_nodes2 = frozenset(nodes2)

    nodes3 = set([node_d, node_e])
    frozen_nodes3 = frozenset(nodes3)

    common_attrib = {'sink': False}

    hyperedges = hyperedges = [nodes1, nodes2, nodes3]

    H = UndirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')
    H.remove_hyperedge('e1')

    assert 'e1' not in H._hyperedge_attributes
    assert 'e1' not in H._star[node_a]
    assert 'e1' not in H._star[node_b]
    assert 'e1' not in H._star[node_c]
    assert frozen_nodes1 not in H._node_set_to_hyperedge

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

    nodes1 = set([node_a, node_b, node_c])
    frozen_nodes1 = frozenset(nodes1)

    nodes2 = set([node_a, node_d])
    frozen_nodes2 = frozenset(nodes2)

    nodes3 = set([node_d, node_e])
    frozen_nodes3 = frozenset(nodes3)

    common_attrib = {'sink': False}

    hyperedges = hyperedges = [nodes1, nodes2, nodes3]

    H = UndirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')
    H.remove_hyperedges(['e1', 'e3'])

    assert 'e1' not in H._hyperedge_attributes
    assert 'e1' not in H._star[node_a]
    assert 'e1' not in H._star[node_b]
    assert 'e1' not in H._star[node_c]
    assert frozen_nodes1 not in H._node_set_to_hyperedge

    assert 'e3' not in H._hyperedge_attributes
    assert 'e3' not in H._star[node_d]
    assert 'e3' not in H._star[node_e]
    assert frozen_nodes3 not in H._node_set_to_hyperedge


def test_remove_node():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    nodes1 = set([node_a, node_b, node_c])
    frozen_nodes1 = frozenset(nodes1)

    nodes2 = set([node_a, node_d])
    frozen_nodes2 = frozenset(nodes2)

    nodes3 = set([node_d, node_e])
    frozen_nodes3 = frozenset(nodes3)

    common_attrib = {'sink': False}

    hyperedges = hyperedges = [nodes1, nodes2, nodes3]

    H = UndirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')
    H.remove_node(node_a)

    # Test that everything that needed to be removed was removed
    assert node_a not in H._node_attributes
    assert node_a not in H._star
    assert "e1" not in H._hyperedge_attributes
    assert "e2" not in H._hyperedge_attributes
    assert frozen_nodes1 not in H._node_set_to_hyperedge
    assert frozen_nodes2 not in H._node_set_to_hyperedge

    # Test that everything that wasn't supposed to be removed wasn't removed
    assert "e3" in H._hyperedge_attributes
    assert frozen_nodes3 in H._node_set_to_hyperedge

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

    nodes1 = set([node_a, node_b, node_c])
    frozen_nodes1 = frozenset(nodes1)

    nodes2 = set([node_a, node_d])
    frozen_nodes2 = frozenset(nodes2)

    nodes3 = set([node_d, node_e])
    frozen_nodes3 = frozenset(nodes3)

    common_attrib = {'sink': False}

    hyperedges = hyperedges = [nodes1, nodes2, nodes3]

    H = UndirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')
    H.remove_nodes([node_a, node_e])

    # Test that everything that needed to be removed was removed
    assert node_a not in H._node_attributes
    assert node_a not in H._star
    assert "e1" not in H._hyperedge_attributes
    assert "e2" not in H._hyperedge_attributes
    assert frozen_nodes1 not in H._node_set_to_hyperedge
    assert frozen_nodes2 not in H._node_set_to_hyperedge

    assert node_e not in H._node_attributes
    assert node_e not in H._star
    assert "e3" not in H._hyperedge_attributes
    assert frozen_nodes3 not in H._node_set_to_hyperedge


def test_get_hyperedge_id():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    nodes1 = set([node_a, node_b, node_c])
    frozen_nodes1 = frozenset(nodes1)

    nodes2 = set([node_a, node_d])
    frozen_nodes2 = frozenset(nodes2)

    nodes3 = set([node_d, node_e])
    frozen_nodes3 = frozenset(nodes3)

    common_attrib = {'sink': False}

    hyperedges = hyperedges = [nodes1, nodes2, nodes3]

    H = UndirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    assert H.get_hyperedge_id(nodes1) == 'e1'
    assert H.get_hyperedge_id(nodes2) == 'e2'
    assert H.get_hyperedge_id(nodes3) == 'e3'

    try:
        H.get_hyperedge_id(set([node_a, node_b, node_c, node_d]))
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
    node_e = 'E'

    nodes1 = set([node_a, node_b, node_c])
    frozen_nodes1 = frozenset(nodes1)

    nodes2 = set([node_a, node_d])
    frozen_nodes2 = frozenset(nodes2)

    nodes3 = set([node_d, node_e])
    frozen_nodes3 = frozenset(nodes3)

    common_attrib = {'sink': False}

    hyperedges = hyperedges = [nodes1, nodes2, nodes3]

    H = UndirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    assert H.get_hyperedge_attribute('e1', 'weight') == 1
    assert H.get_hyperedge_attribute('e1', 'color') == 'white'
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


def test_get_hyperedge_attributes():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    nodes1 = set([node_a, node_b, node_c])
    frozen_nodes1 = frozenset(nodes1)

    nodes2 = set([node_a, node_d])
    frozen_nodes2 = frozenset(nodes2)

    nodes3 = set([node_d, node_e])
    frozen_nodes3 = frozenset(nodes3)

    common_attrib = {'sink': False}

    hyperedges = hyperedges = [nodes1, nodes2, nodes3]

    H = UndirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    attrs = H.get_hyperedge_attributes('e1')
    assert attrs['weight'] == 1
    assert attrs['color'] == 'white'
    assert attrs['sink'] is False

    # Try requesting an invalid hyperedge
    try:
        H.get_hyperedge_attributes('e5')
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e


def test_get_hyperedge_nodes():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    nodes1 = set([node_a, node_b, node_c])
    frozen_nodes1 = frozenset(nodes1)

    nodes2 = set([node_a, node_d])
    frozen_nodes2 = frozenset(nodes2)

    nodes3 = set([node_d, node_e])
    frozen_nodes3 = frozenset(nodes3)

    common_attrib = {'sink': False}

    hyperedges = hyperedges = [nodes1, nodes2, nodes3]

    H = UndirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    retrieved_nodes1 = H.get_hyperedge_nodes('e1')
    retrieved_nodes2 = H.get_hyperedge_nodes('e2')
    assert retrieved_nodes1 == nodes1
    assert retrieved_nodes2 == nodes2


def test_get_hyperedge_weight():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    nodes1 = set([node_a, node_b, node_c])
    frozen_nodes1 = frozenset(nodes1)

    nodes2 = set([node_a, node_d])
    frozen_nodes2 = frozenset(nodes2)

    nodes3 = set([node_d, node_e])
    frozen_nodes3 = frozenset(nodes3)

    common_attrib = {'weight': 2, 'sink': False}

    hyperedges = hyperedges = [nodes1, nodes2, nodes3]

    H = UndirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    weight_e1 = H.get_hyperedge_weight('e1')
    weight_e2 = H.get_hyperedge_weight('e2')
    assert weight_e1 == 2
    assert weight_e2 == 2


def test_get_node_attribute():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    attrib_c = {'alt_name': 1337}
    node_d = 'D'
    attrib_d = {'label': 'black', 'sink': True}

    # Test adding unadded nodes with various attribute settings
    H = UndirectedHypergraph()
    H.add_node(node_a)
    H.add_node(node_b, source=True)
    H.add_node(node_c, attrib_c)
    H.add_node(node_d, attrib_d, sink=False)

    assert H.get_node_attribute(node_b, 'source') is True
    assert H.get_node_attribute(node_c, 'alt_name') == 1337
    assert H.get_node_attribute(node_d, 'sink') is False

    # Try requesting an invalid node
    try:
        H.get_node_attribute("E", 'common')
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
    H = UndirectedHypergraph()
    H.add_node(node_a)
    H.add_node(node_b, source=True)
    H.add_node(node_c, attrib_c)
    H.add_node(node_d, attrib_d, sink=False)

    attrs = H.get_node_attributes(node_b)
    assert attrs['source'] is True

    # Try requesting an invalid node
    try:
        H.get_node_attributes("E")
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e


def test_get_star():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    nodes1 = set([node_a, node_b, node_c])
    frozen_nodes1 = frozenset(nodes1)

    nodes2 = set([node_a, node_d])
    frozen_nodes2 = frozenset(nodes2)

    nodes3 = set([node_d, node_e])
    frozen_nodes3 = frozenset(nodes3)

    common_attrib = {'weight': 2, 'sink': False}

    hyperedges = hyperedges = [nodes1, nodes2, nodes3]

    H = UndirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    assert H.get_star(node_a) == set(['e1', 'e2'])
    assert H.get_star(node_b) == set(['e1'])
    assert H.get_star(node_c) == set(['e1'])
    assert H.get_star(node_d) == set(['e2', 'e3'])
    assert H.get_star(node_e) == set(['e3'])

    # Try requesting an invalid node
    try:
        H.get_star("F")
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e


def test_copy():
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    nodes1 = set([node_a, node_b, node_c])
    frozen_nodes1 = frozenset(nodes1)

    nodes2 = set([node_a, node_d])
    frozen_nodes2 = frozenset(nodes2)

    nodes3 = set([node_d, node_e])
    frozen_nodes3 = frozenset(nodes3)

    common_attrib = {'weight': 2, 'sink': False}

    hyperedges = hyperedges = [nodes1, nodes2, nodes3]

    H = UndirectedHypergraph()
    H.add_node("A", root=True)
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    new_H = H.copy()

    assert new_H._node_attributes == H._node_attributes
    assert new_H._hyperedge_attributes == H._hyperedge_attributes
    assert new_H._star == H._star
    assert new_H._node_set_to_hyperedge == H._node_set_to_hyperedge


def test_read_and_write():
    # Try writing the following hypergraph to a file
    node_a = 'A'
    node_b = 'B'
    node_c = 'C'
    node_d = 'D'
    node_e = 'E'

    nodes1 = set([node_a, node_b, node_c])
    frozen_nodes1 = frozenset(nodes1)

    nodes2 = set([node_a, node_d])
    frozen_nodes2 = frozenset(nodes2)

    nodes3 = set([node_d, node_e])
    frozen_nodes3 = frozenset(nodes3)

    common_attrib = {'weight': 2, 'sink': False}

    hyperedges = hyperedges = [nodes1, nodes2, nodes3]

    H = UndirectedHypergraph()
    hyperedge_names = \
        H.add_hyperedges(hyperedges, common_attrib, color='white')

    H.write("test_undirected_read_and_write.txt")

    # Try reading the hypergraph that was just written into a new hypergraph
    new_H = UndirectedHypergraph()
    new_H.read("test_undirected_read_and_write.txt")

    assert H._node_attributes.keys() == new_H._node_attributes.keys()

    for new_hyperedge_id in new_H.get_hyperedge_id_set():
        new_hyperedge_nodes = new_H.get_hyperedge_nodes(new_hyperedge_id)
        new_hyperedge_weight = new_H.get_hyperedge_weight(new_hyperedge_id)

        found_matching_hyperedge = False
        for hyperedge_id in H.get_hyperedge_id_set():
            hyperedge_nodes = H.get_hyperedge_nodes(hyperedge_id)
            hyperedge_weight = H.get_hyperedge_weight(hyperedge_id)

            if new_hyperedge_nodes == hyperedge_nodes and \
               new_hyperedge_weight == hyperedge_weight:
                found_matching_hyperedge = True
                continue

        assert found_matching_hyperedge

    remove("test_undirected_read_and_write.txt")

    # Try reading an invalid hypergraph file
    invalid_H = UndirectedHypergraph()
    try:
        invalid_H.read("tests/data/invalid_undirected_hypergraph.txt")
        assert False
    except IOError:
        pass
    except BaseException as e:
        assert False, e
