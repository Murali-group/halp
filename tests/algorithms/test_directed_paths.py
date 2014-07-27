from hypergraph.directed_hypergraph import DirectedHypergraph
from hypergraph.algorithms import directed_paths
import unittest


def test_visit():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    visited_nodes, Pv, Pe = directed_paths.visit(H, 's')

    assert visited_nodes == set(['s', 'x', 'y', 'z', 'u', 't', 'a'])

    assert Pv['s'] is None
    assert (Pe['e1'], Pe['e2'], Pe['e3']) == ('s', 's', 's')
    assert Pv['x'] in ('e1', 'e2')
    assert Pv['y'] == 'e2'
    assert Pv['z'] == 'e3'
    assert Pe['e4'] in ('x', 'y', 'z')
    assert Pv['u'] == 'e4'
    assert Pv['t'] == 'e8'
    assert Pv['a'] == 'e7'
    assert Pe['e5'] == 'a'
    assert Pe['e6'] == 'x'
    assert Pe['e7'] == 't'
    assert Pe['e8'] == 's'
    assert Pv['b'] is None

    try:
        directed_paths.visit('s', 't')
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_is_connected():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_paths.is_connected(H, 's', 'x')
    assert directed_paths.is_connected(H, 's', 'y')
    assert directed_paths.is_connected(H, 's', 'z')
    assert directed_paths.is_connected(H, 's', 't')
    assert directed_paths.is_connected(H, 's', 'u')
    assert directed_paths.is_connected(H, 's', 'a')
    assert not directed_paths.is_connected(H, 's', 'b')


def test_b_visit():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    # Let 's' be the source node:
    b_visited_nodes, Pv, Pe, v = directed_paths.b_visit(H, 's')

    assert b_visited_nodes == set(['s', 'x', 'y', 'z', 't', 'u'])

    assert Pv['s'] is None
    assert v['s'] == 0
    assert (Pe['e1'], Pe['e2'], Pe['e3']) == ('s', 's', 's')
    assert Pv['x'] in ('e1', 'e2')
    assert Pv['y'] == 'e2'
    assert Pv['z'] == 'e3'
    assert (v['x'], v['y'], v['z']) == (1, 1, 1)
    assert Pe['e4'] in ('x', 'y', 'z')
    assert Pv['u'] == 'e4'
    assert Pv['t'] == 'e8'
    assert v['t'] == 1
    assert v['u'] == 2
    assert Pv['a'] is None
    assert Pe['e5'] is None
    assert Pe['e6'] == 'x'
    assert Pe['e7'] is None
    assert Pe['e8'] == 's'
    assert Pv['b'] is None

    # Let 't' be the source node:
    b_visited_nodes, Pv, Pe, v = directed_paths.b_visit(H, 't')

    assert b_visited_nodes == set(['t'])

    assert Pv['t'] is None
    assert (Pv['s'], Pv['x'], Pv['y'], Pv['z'], Pv['u'], Pv['a'], Pv['b']) == \
        (None, None, None, None, None, None, None)
    assert (Pe["e1"], Pe["e2"], Pe["e3"], Pe["e4"],
            Pe["e5"], Pe["e6"], Pe["e7"]) == \
        (None, None, None, None, None, None, None)

    # Try an invalid B-Visit
    try:
        directed_paths.b_visit('s', 't')
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_is_b_connected():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_paths.is_b_connected(H, 's', 's')
    assert directed_paths.is_b_connected(H, 's', 'x')
    assert directed_paths.is_b_connected(H, 's', 'y')
    assert directed_paths.is_b_connected(H, 's', 'z')
    assert directed_paths.is_b_connected(H, 's', 't')
    assert directed_paths.is_b_connected(H, 's', 'u')
    assert not directed_paths.is_b_connected(H, 's', 'a')
    assert not directed_paths.is_b_connected(H, 's', 'b')


def test_f_visit():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    # Let 's' be the source node:
    f_visited_nodes, Pv, Pe, v = directed_paths.f_visit(H, 's')

    assert f_visited_nodes == set(['s', 'x'])

    assert Pv['s'] is None
    assert v['s'] == 0
    assert Pe['e1'] == 'x'
    assert (Pe['e2'], Pe['e3'], Pe['e4'], Pe['e5'], Pe['e7']) == \
        (None, None, None, None, None)
    assert (Pv['y'], Pv['z'], Pv['u'], Pv['t'], Pv['a'], Pv['b']) == \
        (None, None, None, None, None, None)

    # Let 't' be the source node:
    f_visited_nodes, Pv, Pe, v = directed_paths.f_visit(H, 't')

    assert f_visited_nodes == set(['t', 's', 'x'])

    assert Pv['t'] is None
    assert Pv['s'] == 'e8'
    assert Pv['x'] == 'e6'
    assert (Pv['y'], Pv['z'], Pv['u'], Pv['a'], Pv['b']) == \
        (None, None, None, None, None)
    assert Pe["e8"] == 't'
    assert Pe["e6"] == 's'
    assert Pe["e1"] == 'x'
    assert (Pe["e2"], Pe["e3"], Pe["e4"],
            Pe["e5"], Pe["e7"]) == \
        (None, None, None, None, None)

    # Try invalid F-visit
    try:
        directed_paths.f_visit('s', 't')
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_is_f_connected():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert directed_paths.is_f_connected(H, 's', 's')
    assert directed_paths.is_f_connected(H, 's', 'x')
    assert not directed_paths.is_f_connected(H, 's', 'y')
    assert not directed_paths.is_f_connected(H, 's', 'z')
    assert not directed_paths.is_f_connected(H, 's', 't')
    assert not directed_paths.is_f_connected(H, 's', 'u')
    assert not directed_paths.is_f_connected(H, 's', 'a')
    assert not directed_paths.is_f_connected(H, 's', 'b')


def test_shortest_sum_b_tree():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    Pv, W, valid_ordering = \
        directed_paths.shortest_b_tree(
            H, 's', directed_paths.sum_function, True)

    assert valid_ordering.count('s') == 1
    assert valid_ordering.index('s') < valid_ordering.index('x')
    assert valid_ordering.index('s') < valid_ordering.index('y')
    assert valid_ordering.index('s') < valid_ordering.index('z')
    assert valid_ordering.index('s') < valid_ordering.index('t')
    assert valid_ordering.index('s') < valid_ordering.index('u')
    assert valid_ordering.count('x') == 1
    assert valid_ordering.index('x') < valid_ordering.index('t')
    assert valid_ordering.index('x') < valid_ordering.index('u')
    assert valid_ordering.count('y') == 1
    assert valid_ordering.index('y') < valid_ordering.index('t')
    assert valid_ordering.index('y') < valid_ordering.index('u')
    assert valid_ordering.count('z') == 1
    assert valid_ordering.index('z') < valid_ordering.index('t')
    assert valid_ordering.index('z') < valid_ordering.index('u')
    assert valid_ordering.count('t') == 1
    assert valid_ordering.count('u') == 1
    assert valid_ordering.count('a') == 0
    assert valid_ordering.count('b') == 0

    assert Pv['s'] is None
    assert Pv['x'] == 'e1'
    assert Pv['y'] == 'e2'
    assert Pv['z'] == 'e3'
    assert Pv['t'] == 'e4'
    assert Pv['u'] == 'e4'
    assert (Pv['a'], Pv['b']) == (None, None)

    assert W['s'] == 0
    assert W['x'] == 1
    assert W['y'] == 2
    assert W['z'] == 2
    assert W['u'] == 8
    assert W['t'] == 8
    assert W['a'] == float('inf')
    assert W['b'] == float('inf')


def test_shortest_distance_b_tree():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    Pv, W = \
        directed_paths.shortest_b_tree(
            H, 's', directed_paths.distance_function)

    assert Pv['s'] is None
    assert Pv['x'] == 'e1'
    assert Pv['y'] == 'e2'
    assert Pv['z'] == 'e3'
    assert Pv['t'] == 'e4'
    assert Pv['u'] == 'e4'
    assert (Pv['a'], Pv['b']) == (None, None)

    assert W['s'] == 0
    assert W['x'] == 1
    assert W['y'] == 2
    assert W['z'] == 2
    assert W['u'] == 5
    assert W['t'] == 5
    assert W['a'] == float('inf')
    assert W['b'] == float('inf')


def test_shortest_gap_b_tree():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    Pv, W = \
        directed_paths.shortest_b_tree(H, 's', directed_paths.gap_function)

    assert Pv['s'] is None
    assert Pv['x'] == 'e1'
    assert Pv['y'] == 'e2'
    assert Pv['z'] == 'e3'
    assert Pv['t'] == 'e4'
    assert Pv['u'] == 'e4'
    assert (Pv['a'], Pv['b']) == (None, None)

    assert W['s'] == 0
    assert W['x'] == 1
    assert W['y'] == 2
    assert W['z'] == 2
    assert W['u'] == 4
    assert W['t'] == 4
    assert W['a'] == float('inf')
    assert W['b'] == float('inf')


def test_shortest_sum_f_tree():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    Pv, W = directed_paths.shortest_f_tree(H, 't', directed_paths.sum_function)

    assert Pv['s'] == 'e8'
    assert Pv['x'] == 'e6'
    assert (Pv['y'], Pv['z'], Pv['t'], Pv['u'], Pv['a'], Pv['b']) == \
        (None, None, None, None, None, None)

    assert W['t'] == 0
    assert W['s'] == 100
    assert W['x'] == 101
    assert (W['y'], W['z'], W['u'], W['a'], W['b']) == \
        (float('inf'), float('inf'), float('inf'),
         float('inf'), float('inf'))


def test_get_hypertree_from_predecessors():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    # Test with a weighting
    Pv, W, valid_ordering = \
        directed_paths.shortest_b_tree(
            H, 's', directed_paths.sum_function, True)

    sub_H = directed_paths.get_hypertree_from_predecessors(H, 's', Pv, W)

    sub_H._check_consistency()

    assert sub_H.get_node_set() == set(['s', 'x', 'y', 'z', 't', 'u'])

    assert sub_H.get_node_attribute('s', 'weight') == 0
    assert sub_H.get_node_attribute('x', 'weight') == 1
    assert sub_H.get_node_attribute('y', 'weight') == 2
    assert sub_H.get_node_attribute('z', 'weight') == 2
    assert sub_H.get_node_attribute('u', 'weight') == 8
    assert sub_H.get_node_attribute('t', 'weight') == 8

    assert len(sub_H.get_hyperedge_id_set()) == 4
    assert sub_H.has_hyperedge(['s'], ['x'])
    assert sub_H.has_hyperedge(['s'], ['x', 'y'])
    assert sub_H.has_hyperedge(['s'], ['z'])
    assert sub_H.has_hyperedge(['x', 'y', 'z'], ['u', 't'])

    # Test without a weighting
    Pv, W = directed_paths.shortest_f_tree(H, 't', directed_paths.sum_function)

    sub_H = directed_paths.get_hypertree_from_predecessors(H, 't', Pv)

    sub_H._check_consistency()

    assert sub_H.get_node_set() == set(['t', 's', 'x'])

    assert len(sub_H.get_hyperedge_id_set()) == 2
    assert sub_H.has_hyperedge(['x'], ['s'])
    assert sub_H.has_hyperedge(['s'], ['t'])


class TestGetHyperpathFromPredecessors(unittest.TestCase):
    # valid input tests

    def test_raises_exception_if_keys_of_function_are_not_nodes_in_hypergraph(
            self):
        s1, s2, s3 = 1, 2, 3
        H = DirectedHypergraph()
        H.add_nodes([s1, s2])
        e1 = H.add_hyperedge([s1], [s2])
        T = {s1: None, s3: e1}
        self.assertRaises(TypeError,
                          directed_paths.get_hyperpath_from_predecessors,
                          H, T, s1, s2)

    def test_raises_exception_if_values_of_function_are_not__in_hypergraph(
            self):
        s1, s2, s3 = 1, 2, 3
        H = DirectedHypergraph()
        H.add_nodes([s1, s2])
        e1 = H.add_hyperedge([s1], [s2])
        T = {s1: None, s2: 'e2'}
        self.assertRaises(TypeError,
                          directed_paths.get_hyperpath_from_predecessors,
                          H, T, s1, s2)

    def test_raises_exception_if_more_than_one_node_does_not_have_predecessor(
            self):
        s1, s2, s3 = 1, 2, 3
        H = DirectedHypergraph()
        H.add_nodes([s1, s2, s3])
        e1 = H.add_hyperedge([s1], [s2])
        T = {s1: None, s2: e1, s3: None}
        self.assertRaises(ValueError,
                          directed_paths.get_hyperpath_from_predecessors,
                          H, T, s1, s2)

    def test_raises_exception_if_all_nodes_have_predecessors(self):
        s1, s2, s3 = 1, 2, 3
        H = DirectedHypergraph()
        H.add_nodes([s1, s2, s3])
        e1 = H.add_hyperedge([s1], [s2])
        T = {s1: e1, s2: e1, s3: e1}
        self.assertRaises(ValueError,
                          directed_paths.get_hyperpath_from_predecessors,
                          H, T, s1, s2)

    # various cases
    def test_returns_hyperpath_with_single_node_if_source_equals_destination(
            self):
        s = '1'
        T = {s: None}
        H = DirectedHypergraph()
        H.add_node(s)
        path = directed_paths.get_hyperpath_from_predecessors(H, T, s, s)
        self.assertEqual(len(path.get_node_set()), 1)
        self.assertEqual(len(path.get_hyperedge_id_set()), 0)

    def test_returns_hyperpath_containing_source_if_source_equals_destination(
            self):
        s = '1'
        T = {s: None}
        H = DirectedHypergraph()
        H.add_node(s)
        path = directed_paths.get_hyperpath_from_predecessors(H, T, s, s)
        self.assertTrue(path.has_node(s))

    def test_returns_hyperpath_for_simple_tree(self):
        s1, s2, s3, s4 = 1, 2, 3, 4
        H = DirectedHypergraph()
        H.add_nodes([s1, s2, s3, s4])
        e1 = H.add_hyperedge([s1], [s2])
        e2 = H.add_hyperedge([s1], [s3])
        e3 = H.add_hyperedge([s3], [s4])
        T = {s4: e3, s3: e2, s2: e1, s1: None}
        path = directed_paths.get_hyperpath_from_predecessors(H, T, s1, s4)
        # validate nodes
        self.assertEqual(path.get_node_set(), {s1, s3, s4})
        # validate hyperedges
        self.assertEqual(len(path.get_hyperedge_id_set()), 2)
        self.assertTrue(path.get_hyperedge_id([1], [3]))
        self.assertTrue(path.get_hyperedge_id([3], [4]))

    def test_returns_hyperpath_for_tree_with_multiple_nodes_in_tail(self):
        s1, s2, s3 = 1, 2, 3
        s4, s5, s6 = 4, 5, 6
        H = DirectedHypergraph()
        H.add_nodes([s1, s2, s3, s4, s5, s6])
        e1 = H.add_hyperedge([s1], [s2])
        e2 = H.add_hyperedge([s1], [s3])
        e3 = H.add_hyperedge([s1], [s4])
        e4 = H.add_hyperedge([s2, s3], [s5])
        e5 = H.add_hyperedge([s5], [s6])

        T = {s6: e5, s5: e4, s4: e3, s3: e2, s2: e1, s1: None}
        path = directed_paths.get_hyperpath_from_predecessors(H, T, s1, s6)
        # validate nodes
        self.assertEqual(path.get_node_set(), {s1, s2, s3, s5, s6})
        # validate hyperedges
        self.assertEqual(len(path.get_hyperedge_id_set()), 4)
        self.assertTrue(path.get_hyperedge_id([5], [6]))
        self.assertTrue(path.get_hyperedge_id([2, 3], [5]))
        self.assertTrue(path.get_hyperedge_id([1], [3]))
        self.assertTrue(path.get_hyperedge_id([1], [2]))

    def test_returns_hyperpath_when_node_is_in_tail_of_two_edges(self):
        s1, s2, s3 = 1, 2, 3
        s4 = 4
        H = DirectedHypergraph()
        e1 = H.add_hyperedge([s1], [s2])
        e2 = H.add_hyperedge([s2], [s3])
        e3 = H.add_hyperedge([s2, s3], [s4])

        T = {s4: e3, s3: e2, s2: e1, s1: None}
        path = directed_paths.get_hyperpath_from_predecessors(H, T, s1, s4)
        # validate nodes
        self.assertEqual(path.get_node_set(), {s1, s2, s3, s4})
        # validate hyperedges
        self.assertEqual(len(path.get_hyperedge_id_set()), 3)
        self.assertTrue(path.get_hyperedge_id([2, 3], [4]))
        self.assertTrue(path.get_hyperedge_id([2], [3]))
        self.assertTrue(path.get_hyperedge_id([1], [2]))
