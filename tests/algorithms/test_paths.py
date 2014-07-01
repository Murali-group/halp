from hypergraph.directed_hypergraph import DirectedHypergraph
from hypergraph.algorithms import paths


def test_visit():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    visited_nodes, Pv, Pe = paths.visit(H, 's')

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
        paths.visit('s', 't')
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_is_connected():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert paths.is_connected(H, 's', 'x')
    assert paths.is_connected(H, 's', 'y')
    assert paths.is_connected(H, 's', 'z')
    assert paths.is_connected(H, 's', 't')
    assert paths.is_connected(H, 's', 'u')
    assert paths.is_connected(H, 's', 'a')
    assert not paths.is_connected(H, 's', 'b')


def test_b_visit():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    # Let 's' be the source node:
    b_visited_nodes, Pv, Pe, v = paths.b_visit(H, 's')

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
    b_visited_nodes, Pv, Pe, v = paths.b_visit(H, 't')

    assert b_visited_nodes == set(['t'])

    assert Pv['t'] is None
    assert (Pv['s'], Pv['x'], Pv['y'], Pv['z'], Pv['u'], Pv['a'], Pv['b']) == \
        (None, None, None, None, None, None, None)
    assert (Pe["e1"], Pe["e2"], Pe["e3"], Pe["e4"],
            Pe["e5"], Pe["e6"], Pe["e7"]) == \
        (None, None, None, None, None, None, None)

    # Try an invalid B-Visit
    try:
        paths.b_visit('s', 't')
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_is_b_connected():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert paths.is_b_connected(H, 's', 's')
    assert paths.is_b_connected(H, 's', 'x')
    assert paths.is_b_connected(H, 's', 'y')
    assert paths.is_b_connected(H, 's', 'z')
    assert paths.is_b_connected(H, 's', 't')
    assert paths.is_b_connected(H, 's', 'u')
    assert not paths.is_b_connected(H, 's', 'a')
    assert not paths.is_b_connected(H, 's', 'b')


def test_f_visit():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    # Let 's' be the source node:
    f_visited_nodes, Pv, Pe, v = paths.f_visit(H, 's')

    assert f_visited_nodes == set(['s', 'x'])

    assert Pv['s'] is None
    assert v['s'] == 0
    assert Pe['e1'] == 'x'
    assert (Pe['e2'], Pe['e3'], Pe['e4'], Pe['e5'], Pe['e7']) == \
        (None, None, None, None, None)
    assert (Pv['y'], Pv['z'], Pv['u'], Pv['t'], Pv['a'], Pv['b']) == \
        (None, None, None, None, None, None)

    # Let 't' be the source node:
    f_visited_nodes, Pv, Pe, v = paths.f_visit(H, 't')

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
        paths.f_visit('s', 't')
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_is_f_connected():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert paths.is_f_connected(H, 's', 's')
    assert paths.is_f_connected(H, 's', 'x')
    assert not paths.is_f_connected(H, 's', 'y')
    assert not paths.is_f_connected(H, 's', 'z')
    assert not paths.is_f_connected(H, 's', 't')
    assert not paths.is_f_connected(H, 's', 'u')
    assert not paths.is_f_connected(H, 's', 'a')
    assert not paths.is_f_connected(H, 's', 'b')


def test_shortest_sum_b_tree():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    Pv, W, valid_ordering = \
        paths.shortest_b_tree(H, 's', paths.sum_function, True)

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
        paths.shortest_b_tree(H, 's', paths.distance_function)

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
        paths.shortest_b_tree(H, 's', paths.gap_function)

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

    Pv, W = \
        paths.shortest_f_tree(H, 't', paths.sum_function)

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
