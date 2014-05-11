import unittest

from hypergraph.algorithms import kShortestHyperpaths as ksh
from hypergraph.directedHyperGraph import DirectedHyperGraph
from hypergraph.directedHyperGraph import DirectedBHyperGraph
from hypergraph.node import Node
from hypergraph.hyperedge import HyperEdge


class TestGetHyperpathFromHypertree(unittest.TestCase):
    # valid input tests

    def test_raises_exception_if_T_does_not_map_from_node_to_edges(self):
        s = Node('1')
        T = {s: 'a'}
        self.assertRaises(ksh.InvalidArgumentError,
                          ksh.get_hyperpath_from_hypertree, T, s, s)

    def test_raises_exception_if_more_than_one_node_does_not_have_predecessor(
            self):
        s1, s2, s3 = Node('1'), Node('2'), Node('3')
        T = {s1: None, s2: None, s3: HyperEdge(head={s2}, tail={s1})}
        self.assertRaises(ksh.InvalidArgumentError,
                          ksh.get_hyperpath_from_hypertree, T, s1, s2)

    def test_raises_exception_if_all_nodes_have_predecessor(self):
        s1, s2, s3 = Node('1'), Node('2'), Node('3')
        e = HyperEdge(head={s2}, tail={s1})
        T = {s1: e, s2: e, s3: e}
        self.assertRaises(ksh.InvalidArgumentError,
                          ksh.get_hyperpath_from_hypertree, T, s1, s2)

    # various cases
    def test_returns_hyperpath_with_single_node_when_S_equals_T(self):
        s = Node('1')
        T = {s: None}
        G = ksh.get_hyperpath_from_hypertree(T, s, s)
        self.assertEqual(len(G.nodes), 1)
        self.assertEqual(len(G.hyperedges), 0)

    def test_returns_hyperpath_containing_S_when_S_equals_T(self):
        s = Node('1')
        T = {s: None}
        G = ksh.get_hyperpath_from_hypertree(T, s, s)
        self.assertIsNot(G.get_node_by_name('1'), None)

    def test_returns_hyperpath_for_simple_tree(self):
        s1, s2, s3, s4 = Node('1'), Node('2'), Node('3'), Node('4')
        e1 = HyperEdge({s2}, {s1})
        e2 = HyperEdge({s3}, {s1})
        e3 = HyperEdge({s4}, {s3})
        T = {s4: e3, s3: e2, s2: e1, s1: None}
        G = ksh.get_hyperpath_from_hypertree(T, s1, s4)
        # validate nodes
        self.assertEqual(G.get_node_names(), {'1', '3', '4'})
        # validate hyperedges
        hyperedgesTuple = [({node.name for node in e.head},
                            {node.name for node in e.tail})
                           for e in G.hyperedges]
        self.assertEqual(len(G.hyperedges), 2)
        self.assertIn(({'4'}, {'3'}), hyperedgesTuple)
        self.assertIn(({'3'}, {'1'}), hyperedgesTuple)

    def test_returns_hyperpath_for_tree_with_multiple_nodes_in_tail(self):
        s1, s2, s3 = Node('1'), Node('2'), Node('3')
        s4, s5, s6 = Node('4'), Node('5'), Node('6')
        e1 = HyperEdge({s2}, {s1})
        e2 = HyperEdge({s3}, {s1})
        e3 = HyperEdge({s4}, {s1})
        e4 = HyperEdge({s5}, {s2, s3})
        e5 = HyperEdge({s6}, {s5})

        T = {s6: e5, s5: e4, s4: e3, s3: e2, s2: e1, s1: None}
        G = ksh.get_hyperpath_from_hypertree(T, s1, s6)
        # validate nodes
        self.assertEqual(G.get_node_names(), {'1', '2', '3', '5', '6'})
        # validate hyperedges
        hyperedgesTuple = [({node.name for node in e.head},
                            {node.name for node in e.tail})
                           for e in G.hyperedges]
        self.assertEqual(len(G.hyperedges), 4)
        self.assertIn(({'6'}, {'5'}), hyperedgesTuple)
        self.assertIn(({'5'}, {'2', '3'}), hyperedgesTuple)
        self.assertIn(({'3'}, {'1'}), hyperedgesTuple)
        self.assertIn(({'2'}, {'1'}), hyperedgesTuple)

    def test_returns_hyperpath_when_node_is_in_tail_of_two_edges(self):
        s1, s2, s3 = Node('1'), Node('2'), Node('3')
        s4 = Node('4')
        e1 = HyperEdge({s2}, {s1})
        e2 = HyperEdge({s3}, {s2})
        e3 = HyperEdge({s4}, {s2, s3})

        T = {s4: e3, s3: e2, s2: e1, s1: None}
        G = ksh.get_hyperpath_from_hypertree(T, s1, s4)
        # validate nodes
        self.assertEqual(G.get_node_names(), {'1', '2', '3', '4'})
        # validate hyperedges
        hyperedgesTuple = [({node.name for node in e.head},
                            {node.name for node in e.tail})
                           for e in G.hyperedges]
        self.assertEqual(len(G.hyperedges), 3)
        self.assertIn(({'4'}, {'2', '3'}), hyperedgesTuple)
        self.assertIn(({'3'}, {'2'}), hyperedgesTuple)
        self.assertIn(({'2'}, {'1'}), hyperedgesTuple)


class TestBranchingStep(unittest.TestCase):

    def setUp(self):
        self.nielsenGraph = DirectedBHyperGraph(set(), set())
        self.nielsenGraph.add_node(Node('s'))
        self.nielsenGraph.add_node(Node('1'))
        self.nielsenGraph.add_node(Node('2'))
        self.nielsenGraph.add_node(Node('3'))
        self.nielsenGraph.add_node(Node('4'))
        self.nielsenGraph.add_node(Node('t'))
        self.nielsenGraph.add_hyperedge({'1'}, {'s'}, 1)
        self.nielsenGraph.add_hyperedge({'2'}, {'s'}, 1)
        self.nielsenGraph.add_hyperedge({'3'}, {'s'}, 1)
        self.nielsenGraph.add_hyperedge({'2'}, {'1'}, 1)
        self.nielsenGraph.add_hyperedge({'3'}, {'2'}, 1)
        self.nielsenGraph.add_hyperedge({'t'}, {'1', '2'}, 1)
        self.nielsenGraph.add_hyperedge({'t'}, {'4'}, 1)
        self.nielsenGraph.add_hyperedge({'4'}, {'2', '3'}, 1)
        self.nielsenGraph.add_hyperedge({'1'}, {'4'}, 1)

    def test_returns_disconnected_nodes_on_graph_with_two_nodes(self):
        G = DirectedBHyperGraph(set(), set())
        s = Node('s')
        t = Node('t')
        e1 = HyperEdge({t}, {s}, 1)
        G.add_node(s)
        G.add_node(t)
        G.add_hyperedge(e1)
        predecessor = {s: None, t: e1}
        ordering = [s, t]
        branch = ksh.branching_step(G, predecessor, ordering)[0]
        self.assertEqual(branch.hyperedges, set([]))
        self.assertEqual(branch.get_node_names(), {'s', 't'})

    def test_returns_correct_branching_for_nielsen_graph(self):
        get_node = self.nielsenGraph.get_node_by_name
        nielsenNodes = self.nielsenGraph.get_node_names()
        ordering = [get_node('s'), get_node('1'),
                    get_node('2'), get_node('t')]
        pred = {get_node('s'): None}

        # we really need better ways to access
        # a hypergraph's hyperedges
        for e in self.nielsenGraph.hyperedges:
            if e.head == {get_node('1')} and e.tail == {get_node('s')}:
                pred[get_node('1')] = e
            elif e.head == {get_node('2')} and e.tail == {get_node('s')}:
                pred[get_node('2')] = e
            elif e.head == {get_node('t')} and e.tail == {get_node('2'),
                                                          get_node('1')}:
                pred[get_node('t')] = e
        branches = ksh.branching_step(self.nielsenGraph, pred, ordering)
        self.assertEqual(len(branches), 3)
        # branch 1
        b1 = branches[0]
        self.assertEqual(b1.get_node_names(), nielsenNodes)
        hyperedges = b1.hyperedges
        hyperedgesTuple = [({node.name for node in e.head},
                            {node.name for node in e.tail})
                           for e in hyperedges]
        self.assertEqual(len(hyperedges), 6)
        self.assertIn(({'2'}, {'s'}), hyperedgesTuple)
        self.assertIn(({'3'}, {'s'}), hyperedgesTuple)
        self.assertIn(({'3'}, {'2'}), hyperedgesTuple)
        self.assertIn(({'4'}, {'2', '3'}), hyperedgesTuple)
        self.assertIn(({'t'}, {'1', '2'}), hyperedgesTuple)
        self.assertIn(({'1'}, {'4'}), hyperedgesTuple)
        # branch 2
        b2 = branches[1]
        self.assertEqual(b2.get_node_names(), nielsenNodes)
        hyperedges = b2.hyperedges
        hyperedgesTuple = [({node.name for node in e.head},
                            {node.name for node in e.tail})
                           for e in hyperedges]
        self.assertEqual(len(hyperedges), 7)
        self.assertIn(({'1'}, {'s'}), hyperedgesTuple)
        self.assertIn(({'3'}, {'s'}), hyperedgesTuple)
        self.assertIn(({'2'}, {'1'}), hyperedgesTuple)
        self.assertIn(({'3'}, {'2'}), hyperedgesTuple)
        self.assertIn(({'4'}, {'2', '3'}), hyperedgesTuple)
        self.assertIn(({'t'}, {'1', '2'}), hyperedgesTuple)
        self.assertIn(({'1'}, {'4'}), hyperedgesTuple)
        # branch 3
        b3 = branches[2]
        self.assertEqual(b3.get_node_names(), nielsenNodes)
        hyperedges = b3.hyperedges
        hyperedgesTuple = [({node.name for node in e.head},
                            {node.name for node in e.tail})
                           for e in hyperedges]
        self.assertEqual(len(hyperedges), 8)
        self.assertIn(({'1'}, {'s'}), hyperedgesTuple)
        self.assertIn(({'2'}, {'s'}), hyperedgesTuple)
        self.assertIn(({'3'}, {'s'}), hyperedgesTuple)
        self.assertIn(({'2'}, {'1'}), hyperedgesTuple)
        self.assertIn(({'3'}, {'2'}), hyperedgesTuple)
        self.assertIn(({'4'}, {'2', '3'}), hyperedgesTuple)
        self.assertIn(({'t'}, {'4'}), hyperedgesTuple)
        self.assertIn(({'1'}, {'4'}), hyperedgesTuple)


class TestComputeLowerBound(unittest.TestCase):

    def setUp(self):
        self.nielsenGraph = DirectedBHyperGraph(set(), set())
        self.nielsenGraph.add_node(Node('s'))
        self.nielsenGraph.add_node(Node('1'))
        self.nielsenGraph.add_node(Node('2'))
        self.nielsenGraph.add_node(Node('3'))
        self.nielsenGraph.add_node(Node('4'))
        self.nielsenGraph.add_node(Node('t'))
        self.nielsenGraph.add_hyperedge({'1'}, {'s'}, 1)
        self.nielsenGraph.add_hyperedge({'2'}, {'s'}, 1)
        self.nielsenGraph.add_hyperedge({'3'}, {'s'}, 1)
        self.nielsenGraph.add_hyperedge({'2'}, {'1'}, 1)
        self.nielsenGraph.add_hyperedge({'3'}, {'2'}, 1)
        self.nielsenGraph.add_hyperedge({'t'}, {'1', '2'}, 1)
        self.nielsenGraph.add_hyperedge({'t'}, {'4'}, 1)
        self.nielsenGraph.add_hyperedge({'4'}, {'2', '3'}, 1)
        self.nielsenGraph.add_hyperedge({'1'}, {'4'}, 1)

    def test_returns_12_for_lower_bound_for_nielsen_H_21(self):
        '''
            Test graph is discussed in Section 3.2 example 2 of
            Nielsen et al.\
        '''
        H_2 = self.nielsenGraph.copy()
        e1, e2, e3 = None, None, None
        hyperedges = list(H_2.hyperedges)
        for e in hyperedges:
            if ((e.head == {H_2.get_node_by_name('2')} and
                 e.tail == {H_2.get_node_by_name('s')}) or
                (e.head == {H_2.get_node_by_name('t')} and
                 e.tail == {H_2.get_node_by_name('4')})):
                H_2.remove_hyperedge(e)
            elif ((e.head == {H_2.get_node_by_name('1')} and
                   e.tail == {H_2.get_node_by_name('s')})):
                e1 = e
            elif ((e.head == {H_2.get_node_by_name('2')} and
                   e.tail == {H_2.get_node_by_name('1')})):
                e2 = e
            elif ((e.head == {H_2.get_node_by_name('t')} and
                   e.tail == {H_2.get_node_by_name('1'),
                              H_2.get_node_by_name('2')})):
                e3 = e

        # weight vector
        W = {H_2.get_node_by_name('s'): 0, H_2.get_node_by_name('1'): 1,
             H_2.get_node_by_name('2'): 2, H_2.get_node_by_name('3'): 1,
             H_2.get_node_by_name('4'): 4, H_2.get_node_by_name('t'): 4}
        # predecessor function
        pred = {H_2.get_node_by_name('s'): None,
                H_2.get_node_by_name('1'): e1,
                H_2.get_node_by_name('2'): e2,
                H_2.get_node_by_name('t'): e3}

        # ordering
        ordering = [H_2.get_node_by_name('s'),
                    H_2.get_node_by_name('1'),
                    H_2.get_node_by_name('2'),
                    H_2.get_node_by_name('t')]

        # branch of H_2 for the test
        H_21 = H_2.copy()
        for e in H_21.hyperedges:
            if ((e.head == {H_2.get_node_by_name('1')} and
                 e.tail == {H_2.get_node_by_name('s')})):
                H_21.remove_hyperedge(e)
                break

        subproblem = (H_2, None, pred, ordering)
        self.assertEqual(ksh.compute_lower_bound(
            H_21, 0, pred,
            ordering, W, H_21.get_node_by_name('t')), 12)


class TestKShortestHyperpaths(unittest.TestCase):

    def setUp(self):
        self.nielsenGraph = DirectedBHyperGraph(set(), set())
        self.nielsenGraph.add_node(Node('s'))
        self.nielsenGraph.add_node(Node('1'))
        self.nielsenGraph.add_node(Node('2'))
        self.nielsenGraph.add_node(Node('3'))
        self.nielsenGraph.add_node(Node('4'))
        self.nielsenGraph.add_node(Node('t'))
        self.nielsenGraph.add_hyperedge({'1'}, {'s'}, 1)
        self.nielsenGraph.add_hyperedge({'2'}, {'s'}, 1)
        self.nielsenGraph.add_hyperedge({'3'}, {'s'}, 1)
        self.nielsenGraph.add_hyperedge({'2'}, {'1'}, 1)
        self.nielsenGraph.add_hyperedge({'3'}, {'2'}, 1)
        self.nielsenGraph.add_hyperedge({'t'}, {'1', '2'}, 1)
        self.nielsenGraph.add_hyperedge({'t'}, {'4'}, 1)
        self.nielsenGraph.add_hyperedge({'4'}, {'2', '3'}, 1)
        self.nielsenGraph.add_hyperedge({'1'}, {'4'}, 1)

    # valid input tests
    def test_raises_exception_if_G_not_B_hypegraph(self):
        G = DirectedHyperGraph(set(), set())
        s = Node('1')
        t = Node('2')
        G.add_node(s)
        G.add_node(t)
        self.assertRaises(ksh.InvalidArgumentError,
                          ksh.k_shortest_hyperpaths, G, s, t, 1)

    def test_raises_exception_if_root_not_in_graph(self):
        G = DirectedBHyperGraph(set(), set())
        s = Node('1')
        t = Node('2')
        G.add_node(s)
        G.add_node(t)
        self.assertRaises(ksh.InvalidArgumentError,
                          ksh.k_shortest_hyperpaths, G, Node('3'), t, 1)

    def test_raises_exception_if_destination_not_in_graph(self):
        G = DirectedBHyperGraph(set(), set())
        s = Node('1')
        t = Node('2')
        G.add_node(s)
        G.add_node(t)
        self.assertRaises(ksh.InvalidArgumentError,
                          ksh.k_shortest_hyperpaths, G, s, Node('3'), 1)

    def test_raises_exception_if_k_not_integer(self):
        G = DirectedBHyperGraph(set(), set())
        s = Node('1')
        t = Node('2')
        G.add_node(s)
        G.add_node(t)
        self.assertRaises(ksh.InvalidArgumentError,
                          ksh.k_shortest_hyperpaths, G, s, t, 0.1)

    def test_raises_exception_if_k_negative(self):
        G = DirectedBHyperGraph(set(), set())
        s = Node('1')
        t = Node('2')
        G.add_node(s)
        G.add_node(t)
        self.assertRaises(ksh.OutOfRangeError,
                          ksh.k_shortest_hyperpaths, G, s, t, -4)

    def test_raises_exception_if_k_zero(self):
        G = DirectedBHyperGraph(set(), set())
        s = Node('1')
        t = Node('2')
        G.add_node(s)
        G.add_node(t)
        self.assertRaises(ksh.OutOfRangeError,
                          ksh.k_shortest_hyperpaths, G, s, t, 0)

    # various cases
    def test_returns_only_one_hyperpath_for_k_equals_one(self):
        G = DirectedBHyperGraph(set(), set())
        G.add_node(Node('s'))
        G.add_node(Node('1'))
        G.add_node(Node('2'))
        G.add_node(Node('3'))
        G.add_node(Node('t'))
        G.add_hyperedge({'1'}, {'s'}, 1)
        G.add_hyperedge({'2'}, {'s'}, 1)
        G.add_hyperedge({'3'}, {'s'}, 1)
        G.add_hyperedge({'t'}, {'1'}, 1)
        G.add_hyperedge({'t'}, {'2', '3'}, 1)

        output = ksh.k_shortest_hyperpaths(G, G.get_node_by_name('s'),
                                           G.get_node_by_name('t'), 1)
        self.assertEqual(len(output), 1)

    def test_returns_shortest_hyperpath_for_k_equals_one(self):
        # probably too long for a unit test
        # it should be refactored once we have proper methods to
        # compare hypergraphs
        G = DirectedBHyperGraph(nodes=set(), hyperedges=set())
        G.add_node(Node('s'))
        G.add_node(Node('1'))
        G.add_node(Node('2'))
        G.add_node(Node('3'))
        G.add_node(Node('t'))
        G.add_hyperedge({'1'}, {'s'}, 1)
        G.add_hyperedge({'2'}, {'s'}, 1)
        G.add_hyperedge({'3'}, {'s'}, 1)
        G.add_hyperedge({'t'}, {'1'}, 1)
        G.add_hyperedge({'t'}, {'2', '3'}, 1)

        output = ksh.k_shortest_hyperpaths(G, G.get_node_by_name('s'),
                                           G.get_node_by_name('t'), 1)
        hyperpath = output[0]
        self.assertEqual(hyperpath.get_node_names(), {'s', '1', 't'})
        hyperedges = hyperpath.hyperedges
        hyperedgesTuple = [({node.name for node in e.head},
                            {node.name for node in e.tail})
                           for e in hyperedges]
        self.assertEqual(len(hyperedges), 2)
        self.assertIn(({'1'}, {'s'}), hyperedgesTuple)
        self.assertIn(({'t'}, {'1'}), hyperedgesTuple)

    def test_returns_empty_list_if_no_s_t_path(self):
        G = DirectedBHyperGraph(set(), set())
        G.add_node(Node('s'))
        G.add_node(Node('1'))
        G.add_node(Node('2'))
        G.add_node(Node('t'))
        G.add_hyperedge({'1'}, {'s'}, 1)
        G.add_hyperedge({'t'}, {'1', '2'}, 1)

        output = ksh.k_shortest_hyperpaths(G, G.get_node_by_name('s'),
                                           G.get_node_by_name('t'), 1)
        self.assertEqual(output, [])

    def test_returns_3_shortest_hypergraphs_for_nielsen_example_with_k_equal_3(
            self):
        threeShortest = ksh.k_shortest_hyperpaths(
            self.nielsenGraph,
            self.nielsenGraph.get_node_by_name('s'),
            self.nielsenGraph.get_node_by_name('t'), 3)
        self.assertEquals(len(threeShortest), 3)
        # shortest path
        hyperpath = threeShortest[0]
        self.assertEqual(hyperpath.get_node_names(), {'s', '1', '2', 't'})
        hyperedges = hyperpath.hyperedges
        hyperedgesTuple = [({node.name for node in e.head},
                            {node.name for node in e.tail})
                           for e in hyperedges]
        self.assertEqual(len(hyperedges), 3)
        self.assertIn(({'1'}, {'s'}), hyperedgesTuple)
        self.assertIn(({'2'}, {'s'}), hyperedgesTuple)
        self.assertIn(({'t'}, {'1', '2'}), hyperedgesTuple)
        # second shortest path
        hyperpath = threeShortest[1]
        self.assertEqual(hyperpath.get_node_names(), {'s', '1', '2', 't'})
        hyperedges = hyperpath.hyperedges
        hyperedgesTuple = [({node.name for node in e.head},
                            {node.name for node in e.tail})
                           for e in hyperedges]
        self.assertEqual(len(hyperedges), 3)
        self.assertIn(({'1'}, {'s'}), hyperedgesTuple)
        self.assertIn(({'2'}, {'1'}), hyperedgesTuple)
        self.assertIn(({'t'}, {'1', '2'}), hyperedgesTuple)
        # third shortest path
        hyperpath = threeShortest[2]
        self.assertEqual(hyperpath.get_node_names(), {'s', '2', '3', '4', 't'})
        hyperedges = hyperpath.hyperedges
        hyperedgesTuple = [({node.name for node in e.head},
                            {node.name for node in e.tail})
                           for e in hyperedges]
        self.assertEqual(len(hyperedges), 4)
        self.assertIn(({'2'}, {'s'}), hyperedgesTuple)
        self.assertIn(({'3'}, {'s'}), hyperedgesTuple)
        self.assertIn(({'4'}, {'2', '3'}), hyperedgesTuple)
        self.assertIn(({'t'}, {'4'}), hyperedgesTuple)


if __name__ == '__main__':
    unittest.main()
