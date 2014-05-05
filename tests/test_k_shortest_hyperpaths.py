import unittest

from hypergraph.algorithms import kShortestHyperpaths as ksh
from hypergraph.directedHyperGraph import DirectedHyperGraph, DirectedBHyperGraph
from hypergraph.node import Node
from hypergraph.hyperedge import HyperEdge

class TestGetHyperpathFromHypertree(unittest.TestCase):
    #valid input tests
    def testRaisesExceptionIfTDoesNotMapFromNodeToEdges(self):
        s = Node('1')
        T = {s: 'a'}
        self.assertRaises(ksh.InvalidArgumentError, ksh.get_hyperpath_from_hypertree, T, s, s)

    def testRaisesExceptionIfMoreThanOneNodeDoesNotHavePredecessor(self):
        s1, s2, s3 = Node('1'), Node('2'), Node('3')
        T = {s1: None, s2:None, s3:HyperEdge(head=set([s2]), tail=set([s1]))}
        self.assertRaises(ksh.InvalidArgumentError, ksh.get_hyperpath_from_hypertree, T, s1, s2)

    def testRaisesExceptionIfAllNodesHavePredecessor(self):
        s1, s2, s3 = Node('1'), Node('2'), Node('3')
        e = HyperEdge(head=set([s2]), tail=set([s1]))
        T = {s1:e, s2:e, s3:e}
        self.assertRaises(ksh.InvalidArgumentError, ksh.get_hyperpath_from_hypertree, T, s1, s2)

    #various cases
    def testReturnsHypergraphWithSingleNodeWhenSEqualsT(self):
        s = Node('1')
        T = {s: None}
        G = ksh.get_hyperpath_from_hypertree(T,s,s)
        self.assertEqual(len(G.nodes), 1)
        self.assertEqual(len(G.hyperedges), 0)
    
    def testReturnsHypergraphContainingSWhenSEqualsT(self):
        s = Node('1')
        T = {s: None}
        G = ksh.get_hyperpath_from_hypertree(T,s,s)
        self.assertIsNot(G.get_node_by_name('1'), None)

    def testReturnsHyperpathForSimpleTree(self):
        s1,s2,s3,s4 = Node('1'), Node('2'), Node('3'), Node('4')
        e1 = HyperEdge(set([s2]),set([s1]))
        e2 = HyperEdge(set([s3]),set([s1]))
        e3 = HyperEdge(set([s4]),set([s3]))
        T = {s4:e3, s3:e2, s2:e1, s1:None}
        G = ksh.get_hyperpath_from_hypertree(T,s1,s4)
        #validate nodes
        self.assertEqual(G.get_node_names(), set(['1','3','4']))
        #validate hyperedges
        hyperedgesTuple = [(set([node.name for node in e.head]), 
                            set([node.name for node in e.tail])) for e in G.hyperedges]
        self.assertEqual(len(G.hyperedges),2)
        self.assertIn((set(['4']),set(['3'])),hyperedgesTuple)
        self.assertIn((set(['3']),set(['1'])),hyperedgesTuple)

    def testReturnsHyperpathForTreeWithMultipleNodesInTail(self):
        s1,s2,s3 = Node('1'), Node('2'), Node('3')
        s4,s5,s6 = Node('4'), Node('5'), Node('6')
        e1 = HyperEdge(set([s2]),set([s1]))
        e2 = HyperEdge(set([s3]),set([s1]))
        e3 = HyperEdge(set([s4]),set([s1]))
        e4 = HyperEdge(set([s5]),set([s2,s3]))
        e5 = HyperEdge(set([s6]),set([s5]))

        T = {s6:e5, s5:e4, s4:e3, s3:e2, s2:e1, s1:None}
        G = ksh.get_hyperpath_from_hypertree(T,s1,s6)
        #validate nodes
        self.assertEqual(G.get_node_names(), set(['1','2','3','5','6']))
        #validate hyperedges
        hyperedgesTuple = [(set([node.name for node in e.head]), 
                            set([node.name for node in e.tail])) for e in G.hyperedges]
        self.assertEqual(len(G.hyperedges),4)
        self.assertIn((set(['6']),set(['5'])),hyperedgesTuple)
        self.assertIn((set(['5']),set(['2','3'])),hyperedgesTuple)
        self.assertIn((set(['3']),set(['1'])),hyperedgesTuple)
        self.assertIn((set(['2']),set(['1'])),hyperedgesTuple)

    def testReturnsHyperpathWhenNodeIsInTailOfTwoEdges(self):
        s1,s2,s3 = Node('1'), Node('2'), Node('3')
        s4  = Node('4')
        e1 = HyperEdge(set([s2]),set([s1]))
        e2 = HyperEdge(set([s3]),set([s2]))
        e3 = HyperEdge(set([s4]),set([s2,s3]))

        T = {s4:e3, s3:e2, s2:e1, s1:None}
        G = ksh.get_hyperpath_from_hypertree(T,s1,s4)
        #validate nodes
        self.assertEqual(G.get_node_names(), set(['1','2','3','4']))
        #validate hyperedges
        hyperedgesTuple = [(set([node.name for node in e.head]), 
                            set([node.name for node in e.tail])) for e in G.hyperedges]
        self.assertEqual(len(G.hyperedges),3)
        self.assertIn((set(['4']),set(['2','3'])),hyperedgesTuple)
        self.assertIn((set(['3']),set(['2'])),hyperedgesTuple)
        self.assertIn((set(['2']),set(['1'])),hyperedgesTuple)

class TestKShortestHyperpaths(unittest.TestCase):
    #valid input tests
    def testRaisesExceptionIfGNotBHypegraph(self):
        G = DirectedHyperGraph()
        s = Node('1')
        t = Node('2')
        G.add_node(s)
        G.add_node(t)
        self.assertRaises(ksh.InvalidArgumentError, ksh.k_shortest_hyperpaths, G, s, t, 1)

    def testRaisesExceptionIfRootNotInGraph(self):
        G = DirectedBHyperGraph()
        s = Node('1')
        t = Node('2')
        G.add_node(s)
        G.add_node(t)
        self.assertRaises(ksh.InvalidArgumentError, ksh.k_shortest_hyperpaths, G, Node('3'), t, 1)

    def testRaisesExceptionIfDestinationNotInGraph(self):
        G = DirectedBHyperGraph()
        s = Node('1')
        t = Node('2')
        G.add_node(s)
        G.add_node(t)
        self.assertRaises(ksh.InvalidArgumentError, ksh.k_shortest_hyperpaths, G, s, Node('3'), 1)

    def testRaisesExceptionIfKNotInteger(self):
        G = DirectedBHyperGraph()
        s = Node('1')
        t = Node('2')
        G.add_node(s)
        G.add_node(t)
        self.assertRaises(ksh.InvalidArgumentError, ksh.k_shortest_hyperpaths, G, s, t, 0.1)

    def testRaisesExceptionIfKNegative(self):
        G = DirectedBHyperGraph()
        s = Node('1')
        t = Node('2')
        G.add_node(s)
        G.add_node(t)
        self.assertRaises(ksh.OutOfRangeError, ksh.k_shortest_hyperpaths, G, s, t, -4)

    def testRaisesExceptionIfKZero(self):
        G = DirectedBHyperGraph()
        s = Node('1')
        t = Node('2')
        G.add_node(s)
        G.add_node(t)
        self.assertRaises(ksh.OutOfRangeError, ksh.k_shortest_hyperpaths, G, s, t, 0)


    #various cases
    def testReturnsOnlyOneHyperpathForKEqualsOne(self):
        G = DirectedBHyperGraph(set(),set())
        G.add_node(Node('s'))
        G.add_node(Node('1'))
        G.add_node(Node('2'))
        G.add_node(Node('3'))
        G.add_node(Node('t'))
        G.add_hyperedge({'1'},{'s'},1)
        G.add_hyperedge({'2'},{'s'},1)
        G.add_hyperedge({'3'},{'s'},1)
        G.add_hyperedge({'t'},{'1'},1)
        G.add_hyperedge({'t'},{'2','3'},1)

        output = ksh.k_shortest_hyperpaths(G, G.get_node_by_name('s'), 
                                   G.get_node_by_name('t'), 1)
        self.assertEqual(len(output),1)

    def testReturnsShortestHyperpathForKEqualsOne(self):
        #probably too long for a unit test
        #it should be refactored once we have proper methods to
        #compare hypergraphs
        G = DirectedBHyperGraph(nodes=set(),hyperedges=set())
        G.add_node(Node('s'))
        G.add_node(Node('1'))
        G.add_node(Node('2'))
        G.add_node(Node('3'))
        G.add_node(Node('t'))
        G.add_hyperedge({'1'},{'s'},1)
        G.add_hyperedge({'2'},{'s'},1)
        G.add_hyperedge({'3'},{'s'},1)
        G.add_hyperedge({'t'},{'1'},1)
        G.add_hyperedge({'t'},{'2','3'},1)

        output = ksh.k_shortest_hyperpaths(G, G.get_node_by_name('s'), 
                                   G.get_node_by_name('t'), 1)
        hyperpath = output[0]
        self.assertEqual(hyperpath.get_node_names(), set(['s','1','t']))
        hyperedges = hyperpath.hyperedges
        hyperedgesTuple = [(set([node.name for node in e.head]), 
                            set([node.name for node in e.tail])) for e in hyperedges]
        self.assertEqual(len(hyperedges),2)
        self.assertIn((set(['1']),set(['s'])),hyperedgesTuple)
        self.assertIn((set(['t']),set(['1'])),hyperedgesTuple)

    #def testReturnsListOfDirectedBHyperGraph(self)
    #    G = DirectedBHyperGraph()
    #    G.add_node(Node('s'))
    #    G.add_node(Node('1'))
    #    G.add_node(Node('2'))
    #    G.add_node(Node('3'))
    #    G.add_node(Node('t'))
    #    G.add_hyperedge({'1'},{'s'},1)
    #    G.add_hyperedge({'2'},{'s'},1)
    #    G.add_hyperedge({'3'},{'s'},1)
    #    G.add_hyperedge({'t'},{'1'},1)
    #    G.add_hyperedge({'t'},{'2','3'},1)

    #    output = ksh.k_shortest_hyperpaths(G, G.get_node_by_name('s'), 
    #                               G.get_node_by_name('t'), 3)

    #    for path in output:
    #        self.assertIsInstance(path,DirectedBHyperGraph)

    
if __name__=='__main__':
    unittest.main()
