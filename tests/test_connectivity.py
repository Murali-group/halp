from __future__ import absolute_import

from hypergraph.directed_hypergraph import DirectedHypergraph
from hypergraph.algorithms import connectivity


def test_visit():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    visited_nodes, Pv, Pe = connectivity.visit(H, 's')

    assert visited_nodes == set(['s', 'x', 'y', 'z', 'u', 't', 'a'])

    assert Pv['s'] is None
    assert (Pe['e1'], Pe['e2'], Pe['e3']) == ('s', 's', 's')
    assert Pv['x'] in ('e1', 'e2')
    assert Pv['y'] == 'e2'
    assert Pv['z'] == 'e3'
    assert Pe['e4'] in ('x', 'y', 'z')
    assert (Pv['u'], Pv['t']) == ('e4', 'e4')
    assert Pv['a'] == 'e7'
    assert Pe['e5'] == 'a'
    assert Pe['e6'] == 'x'
    assert Pe['e7'] == 't'
    assert Pv['b'] is None

    try:
        connectivity.visit('s', 't')
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_is_connected():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert connectivity.is_connected(H, 's', 'x')
    assert connectivity.is_connected(H, 's', 'y')
    assert connectivity.is_connected(H, 's', 'z')
    assert connectivity.is_connected(H, 's', 't')
    assert connectivity.is_connected(H, 's', 'u')
    assert connectivity.is_connected(H, 's', 'a')
    assert not connectivity.is_connected(H, 's', 'b')


def test_b_visit():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    # Let 's' be the source node:
    b_visited_nodes, Pv, Pe, v = connectivity.b_visit(H, 's')

    assert b_visited_nodes == set(['s', 'x', 'y', 'z', 't', 'u'])

    assert Pv['s'] is None
    assert v['s'] == 0
    assert (Pe['e1'], Pe['e2'], Pe['e3']) == ('s', 's', 's')
    assert Pv['x'] in ('e1', 'e2')
    assert Pv['y'] == 'e2'
    assert Pv['z'] == 'e3'
    assert (v['x'], v['y'], v['z']) == (1, 1, 1)
    assert Pe['e4'] in ('x', 'y', 'z')
    assert (Pv['u'], Pv['t']) == ('e4', 'e4')
    assert (v['u'], v['t']) == (2, 2)
    assert Pv['a'] is None
    assert Pe['e5'] is None
    assert Pe['e6'] == 'x'
    assert Pe['e7'] is None
    assert Pv['b'] is None

    # Let 't' be the source node:
    b_visited_nodes, Pv, Pe, v = connectivity.b_visit(H, 't')

    assert b_visited_nodes == set(['t'])

    assert Pv['t'] is None
    assert (Pv['s'], Pv['x'], Pv['y'], Pv['z'], Pv['u'], Pv['a'], Pv['b']) == \
        (None, None, None, None, None, None, None)
    assert (Pe["e1"], Pe["e2"], Pe["e3"], Pe["e4"],
            Pe["e5"], Pe["e6"], Pe["e7"]) == \
        (None, None, None, None, None, None, None)

    # Try an invalid B-Visit
    try:
        connectivity.b_visit('s', 't')
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_is_b_connected():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert connectivity.is_b_connected(H, 's', 's')
    assert connectivity.is_b_connected(H, 's', 'x')
    assert connectivity.is_b_connected(H, 's', 'y')
    assert connectivity.is_b_connected(H, 's', 'z')
    assert connectivity.is_b_connected(H, 's', 't')
    assert connectivity.is_b_connected(H, 's', 'u')
    assert not connectivity.is_b_connected(H, 's', 'a')
    assert not connectivity.is_b_connected(H, 's', 'b')


def test_f_visit():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    # Let 's' be the source node:
    f_visited_nodes, Pv, Pe, v = connectivity.f_visit(H, 's')

    assert f_visited_nodes == set(['s', 'x'])

    assert Pv['s'] is None
    assert v['s'] == 0
    assert Pe['e1'] == 'x'
    assert (Pe['e2'], Pe['e3'], Pe['e4'], Pe['e5'], Pe['e7']) == \
        (None, None, None, None, None)
    assert (Pv['y'], Pv['z'], Pv['u'], Pv['t'], Pv['a'], Pv['b']) == \
        (None, None, None, None, None, None)

    # Let 't' be the source node:
    f_visited_nodes, Pv, Pe, v = connectivity.f_visit(H, 't')

    assert f_visited_nodes == set(['t'])
    
    assert Pv['t'] is None
    assert (Pv['s'], Pv['x'], Pv['y'], Pv['z'], Pv['u'], Pv['a'], Pv['b']) == \
        (None, None, None, None, None, None, None)
    assert (Pe["e1"], Pe["e2"], Pe["e3"], Pe["e4"],
            Pe["e5"], Pe["e6"], Pe["e7"]) == \
        (None, None, None, None, None, None, None)

    # Try invalid F-visit
    try:
        connectivity.f_visit('s', 't')
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e


def test_is_f_connected():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    assert connectivity.is_f_connected(H, 's', 's')
    assert connectivity.is_f_connected(H, 's', 'x')
    assert not connectivity.is_f_connected(H, 's', 'y')
    assert not connectivity.is_f_connected(H, 's', 'z')
    assert not connectivity.is_f_connected(H, 's', 't')
    assert not connectivity.is_f_connected(H, 's', 'u')
    assert not connectivity.is_f_connected(H, 's', 'a')
    assert not connectivity.is_f_connected(H, 's', 'b')
