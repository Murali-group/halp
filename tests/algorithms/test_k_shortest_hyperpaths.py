import unittest

from hypergraph.algorithms import k_shortest_hyperpaths as ksh
from hypergraph.directed_hypergraph import DirectedHypergraph
from hypergraph.algorithms.directed_paths import sum_function


class TestBranchingStep(unittest.TestCase):

    def setUp(self):
        self.nielsenGraph = DirectedHypergraph()
        self.nielsenGraph.add_node('s')
        self.nielsenGraph.add_node('1')
        self.nielsenGraph.add_node('2')
        self.nielsenGraph.add_node('3')
        self.nielsenGraph.add_node('4')
        self.nielsenGraph.add_node('t')
        self.nielsenGraph.add_hyperedge({'s'}, {'1'}, weight=1)
        self.nielsenGraph.add_hyperedge({'s'}, {'2'}, weight=1)
        self.nielsenGraph.add_hyperedge({'s'}, {'3'}, weight=1)
        self.nielsenGraph.add_hyperedge({'1'}, {'2'}, weight=1)
        self.nielsenGraph.add_hyperedge({'2'}, {'3'}, weight=1)
        self.nielsenGraph.add_hyperedge({'1', '2'}, {'t'}, weight=1)
        self.nielsenGraph.add_hyperedge({'4'}, {'t'}, weight=1)
        self.nielsenGraph.add_hyperedge({'2', '3'}, {'4'}, weight=1)
        self.nielsenGraph.add_hyperedge({'4'}, {'1'}, weight=1)

    def test_returns_disconnected_nodes_on_graph_with_two_nodes(self):
        H = DirectedHypergraph()
        s, t = 's', 't'
        H.add_node(s)
        H.add_node(t)
        e1 = H.add_hyperedge({s}, {t})
        predecessor = {s: None, t: e1}
        ordering = [s, t]
        branch = ksh._branching_step(H, predecessor, ordering)[0]
        self.assertEqual(branch.get_hyperedge_id_set(), set([]))
        self.assertEqual(branch.get_node_set(), {'s', 't'})

    def test_returns_correct_branching_for_nielsen_graph(self):
        H = self.nielsenGraph
        ordering = ['s', '1', '2', 't']
        pred = {'s': None, '1': H.get_hyperedge_id({'s'}, {'1'}),
                '2': H.get_hyperedge_id({'s'}, {'2'}),
                't': H.get_hyperedge_id({'2', '1'}, {'t'})}

        branches = ksh._branching_step(H, pred, ordering)
        self.assertEqual(len(branches), 3)
        # branch 1
        b1 = branches[0]
        self.assertEqual(b1.get_node_set(), H.get_node_set())
        hyperedges = b1.get_hyperedge_id_set()
        hyperedgesTuple = [(b1.get_hyperedge_tail(e),
                            b1.get_hyperedge_head(e))
                           for e in hyperedges]
        self.assertEqual(len(hyperedges), 6)
        self.assertIn(({'s'}, {'2'}), hyperedgesTuple)
        self.assertIn(({'s'}, {'3'}), hyperedgesTuple)
        self.assertIn(({'2'}, {'3'}), hyperedgesTuple)
        self.assertIn(({'2', '3'}, {'4'}), hyperedgesTuple)
        self.assertIn(({'1', '2'}, {'t'}), hyperedgesTuple)
        self.assertIn(({'4'}, {'1'}), hyperedgesTuple)
        # branch 2
        b2 = branches[1]
        self.assertEqual(b2.get_node_set(), H.get_node_set())
        hyperedges = b2.get_hyperedge_id_set()
        hyperedgesTuple = [(b2.get_hyperedge_tail(e),
                            b2.get_hyperedge_head(e))
                           for e in hyperedges]
        self.assertEqual(len(hyperedges), 7)
        self.assertIn(({'s'}, {'1'}), hyperedgesTuple)
        self.assertIn(({'s'}, {'3'}), hyperedgesTuple)
        self.assertIn(({'1'}, {'2'}), hyperedgesTuple)
        self.assertIn(({'2'}, {'3'}), hyperedgesTuple)
        self.assertIn(({'2', '3'}, {'4'}), hyperedgesTuple)
        self.assertIn(({'1', '2'}, {'t'}), hyperedgesTuple)
        self.assertIn(({'4'}, {'1'}), hyperedgesTuple)
        # branch 3
        b3 = branches[2]
        self.assertEqual(b3.get_node_set(), H.get_node_set())
        hyperedges = b3.get_hyperedge_id_set()
        hyperedgesTuple = [(b3.get_hyperedge_tail(e),
                            b3.get_hyperedge_head(e))
                           for e in hyperedges]
        self.assertEqual(len(hyperedges), 8)
        self.assertIn(({'s'}, {'1'}), hyperedgesTuple)
        self.assertIn(({'s'}, {'2'}), hyperedgesTuple)
        self.assertIn(({'s'}, {'3'}), hyperedgesTuple)
        self.assertIn(({'1'}, {'2'}), hyperedgesTuple)
        self.assertIn(({'2'}, {'3'}), hyperedgesTuple)
        self.assertIn(({'2', '3'}, {'4'}), hyperedgesTuple)
        self.assertIn(({'4'}, {'t'}), hyperedgesTuple)
        self.assertIn(({'4'}, {'1'}), hyperedgesTuple)


class TestComputeLowerBound(unittest.TestCase):

    def setUp(self):
        self.nielsenGraph = DirectedHypergraph()
        self.nielsenGraph.add_node('s')
        self.nielsenGraph.add_node('1')
        self.nielsenGraph.add_node('2')
        self.nielsenGraph.add_node('3')
        self.nielsenGraph.add_node('4')
        self.nielsenGraph.add_node('t')
        self.nielsenGraph.add_hyperedge({'s'}, {'1'}, weight=1)
        self.nielsenGraph.add_hyperedge({'s'}, {'2'}, weight=1)
        self.nielsenGraph.add_hyperedge({'s'}, {'3'}, weight=1)
        self.nielsenGraph.add_hyperedge({'1'}, {'2'}, weight=1)
        self.nielsenGraph.add_hyperedge({'2'}, {'3'}, weight=1)
        self.nielsenGraph.add_hyperedge({'1', '2'}, {'t'}, weight=1)
        self.nielsenGraph.add_hyperedge({'4'}, {'t'}, weight=1)
        self.nielsenGraph.add_hyperedge({'2', '3'}, {'4'}, weight=1)
        self.nielsenGraph.add_hyperedge({'4'}, {'1'}, weight=1)

    def test_returns_12_for_lower_bound_for_nielsen_H_21(self):
        '''
            Test graph is discussed in Section 3.2 example 2 of
            Nielsen et al.\
        '''
        H_2 = self.nielsenGraph.copy()
        e1 = H_2.get_hyperedge_id({'s'}, {'1'})
        e2 = H_2.get_hyperedge_id({'1'}, {'2'})
        e3 = H_2.get_hyperedge_id({'1', '2'}, {'t'})
        H_2.remove_hyperedge(H_2.get_hyperedge_id({'s'}, {'2'}))
        H_2.remove_hyperedge(H_2.get_hyperedge_id({'4'}, {'t'}))

        # weight vector
        W = {'s': 0, '1': 1, '2': 2, '3': 1, '4': 4, 't': 4}
        # predecessor function
        pred = {'s': None, '1': e1, '2': e2, 't': e3}
        # ordering
        ordering = ['s', '1', '2', 't']

        # branch of H_2 for the test
        H_2_1 = H_2.copy()
        H_2_1.remove_hyperedge(
            H_2_1.get_hyperedge_id({'s'}, {'1'}))

        self.assertEqual(ksh._compute_lower_bound(
            H_2_1, 0, pred, ordering, W, 't'), 12)


class TestKShortestHyperpaths(unittest.TestCase):

    def setUp(self):
        self.nielsenGraph = DirectedHypergraph()
        self.nielsenGraph.add_node('s')
        self.nielsenGraph.add_node('1')
        self.nielsenGraph.add_node('2')
        self.nielsenGraph.add_node('3')
        self.nielsenGraph.add_node('4')
        self.nielsenGraph.add_node('t')
        self.nielsenGraph.add_hyperedge({'s'}, {'1'}, weight=1)
        self.nielsenGraph.add_hyperedge({'s'}, {'2'}, weight=1)
        self.nielsenGraph.add_hyperedge({'s'}, {'3'}, weight=1)
        self.nielsenGraph.add_hyperedge({'1'}, {'2'}, weight=1)
        self.nielsenGraph.add_hyperedge({'2'}, {'3'}, weight=1)
        self.nielsenGraph.add_hyperedge({'1', '2'}, {'t'}, weight=1)
        self.nielsenGraph.add_hyperedge({'4'}, {'t'}, weight=1)
        self.nielsenGraph.add_hyperedge({'2', '3'}, {'4'}, weight=1)
        self.nielsenGraph.add_hyperedge({'4'}, {'1'}, weight=1)

    # valid input tests
    def test_raises_exception_if_H_not_B_hypegraph(self):
        H = DirectedHypergraph()
        H.add_nodes([1, 2, 3])
        H.add_hyperedge([1], [2, 3])
        source, destination = 1, 2
        self.assertRaises(TypeError,
                          ksh.k_shortest_hyperpaths, H, source, destination, 1)

    def test_raises_exception_if_source_not_in_graph(self):
        H = DirectedHypergraph()
        source, destination = 1, 2
        H.add_nodes([source, destination])
        self.assertRaises(ValueError,
                          ksh.k_shortest_hyperpaths, H, 3, destination, 1)

    def test_raises_exception_if_destination_not_in_graph(self):
        H = DirectedHypergraph()
        source, destination = 1, 2
        H.add_nodes([source, destination])
        self.assertRaises(ValueError,
                          ksh.k_shortest_hyperpaths, H, source, 3, 1)

    def test_raises_exception_if_k_not_integer(self):
        H = DirectedHypergraph()
        source, destination = 1, 2
        H.add_nodes([source, destination])
        self.assertRaises(TypeError,
                          ksh.k_shortest_hyperpaths,
                          H, source, destination, 0.1)

    def test_raises_exception_if_k_not_positive(self):
        H = DirectedHypergraph()
        source, destination = 1, 2
        H.add_nodes([source, destination])
        self.assertRaises(ValueError,
                          ksh.k_shortest_hyperpaths,
                          H, source, destination, -4)
        self.assertRaises(ValueError,
                          ksh.k_shortest_hyperpaths,
                          H, source, destination, 0)

    # various cases
    def test_returns_only_one_hyperpath_for_k_equals_one(self):
        H = DirectedHypergraph()
        H.add_node('s')
        H.add_node('1')
        H.add_node('2')
        H.add_node('3')
        H.add_node('t')
        H.add_hyperedge({'s'}, {'1'}, weight=1)
        H.add_hyperedge({'s'}, {'2'}, weight=1)
        H.add_hyperedge({'s'}, {'3'}, weight=1)
        H.add_hyperedge({'1'}, {'t'}, weight=1)
        H.add_hyperedge({'2', '3'}, {'t'}, weight=1)

        output = ksh.k_shortest_hyperpaths(H, 's', 't', 1)
        self.assertEqual(len(output), 1)

    def test_returns_shortest_hyperpath_for_k_equals_one(self):
        H = DirectedHypergraph()
        H.add_node('s')
        H.add_node('1')
        H.add_node('2')
        H.add_node('3')
        H.add_node('t')
        H.add_hyperedge({'s'}, {'1'}, weight=1)
        H.add_hyperedge({'s'}, {'2'}, weight=1)
        H.add_hyperedge({'s'}, {'3'}, weight=1)
        H.add_hyperedge({'1'}, {'t'}, weight=1)
        H.add_hyperedge({'2', '3'}, {'t'}, weight=1)

        output = ksh.k_shortest_hyperpaths(H, 's', 't', 1)
        hyperpath = output[0]
        self.assertEqual(hyperpath.get_node_set(), {'s', '1', 't'})
        self.assertEqual(len(hyperpath.get_hyperedge_id_set()), 2)
        self.assertTrue(hyperpath.get_hyperedge_id({'s'}, {'1'}))
        self.assertTrue(hyperpath.get_hyperedge_id({'1'}, {'t'}))

    def test_returns_empty_list_if_no_s_t_path(self):
        H = DirectedHypergraph()
        H.add_node('s')
        H.add_node('1')
        H.add_node('2')
        H.add_node('t')
        H.add_hyperedge({'s'}, {'1'}, weight=1)
        H.add_hyperedge({'1', '2'}, {'t'}, weight=1)

        output = ksh.k_shortest_hyperpaths(H, 's', 't', 1)
        self.assertEqual(output, [])

    def test_returns_3_shortest_hypergraphs_for_nielsen_example_with_k_equal_3(
            self):
        threeShortest = ksh.k_shortest_hyperpaths(
            self.nielsenGraph, 's', 't', 3)
        self.assertEquals(len(threeShortest), 3)
        # shortest path
        hyperpath = threeShortest[0]
        self.assertEqual(hyperpath.get_node_set(), {'s', '1', '2', 't'})
        self.assertEqual(len(hyperpath.get_hyperedge_id_set()), 3)
        self.assertTrue(hyperpath.get_hyperedge_id({'s'}, {'1'}))
        self.assertTrue(hyperpath.get_hyperedge_id({'s'}, {'2'}))
        self.assertTrue(hyperpath.get_hyperedge_id({'1', '2'}, {'t'}))
        # second shortest path
        hyperpath = threeShortest[1]
        self.assertEqual(hyperpath.get_node_set(), {'s', '1', '2', 't'})
        self.assertEqual(len(hyperpath.get_hyperedge_id_set()), 3)
        self.assertTrue(hyperpath.get_hyperedge_id({'s'}, {'1'}))
        self.assertTrue(hyperpath.get_hyperedge_id({'1'}, {'2'}))
        self.assertTrue(hyperpath.get_hyperedge_id({'1', '2'}, {'t'}))
        # third shortest path
        hyperpath = threeShortest[2]
        self.assertEqual(hyperpath.get_node_set(), {'s', '2', '3', '4', 't'})
        self.assertEqual(len(hyperpath.get_hyperedge_id_set()), 4)
        self.assertTrue(hyperpath.get_hyperedge_id({'s'}, {'2'}))
        self.assertTrue(hyperpath.get_hyperedge_id({'s'}, {'3'}))
        self.assertTrue(hyperpath.get_hyperedge_id({'2', '3'}, {'4'}))
        self.assertTrue(hyperpath.get_hyperedge_id({'4'}, {'t'}))


if __name__ == '__main__':
    unittest.main()
