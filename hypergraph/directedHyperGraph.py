from __future__ import absolute_import

from .hypergraph import HyperGraph
from copy import deepcopy

from .node import Node
from .hyperedge import HyperEdge, UndirectedHyperEdge

import numpy as np

'''----------------------- Directed HyperGraph -----------------------------'''


class DirectedHyperGraph(HyperGraph):
    @property
    def nodeIdList(self):
        '''
        Returns the name of the nodes
        '''
        return self._nodeIdList

    @property
    def H_plus(self):
        '''
        Returns the incidence tail matrix
        '''
        return self._incMatTail

    @property
    def H_minus(self):
        '''
        Returns the incidence head matrix
        '''
        return self._incMatHead

    @property
    def edgeWeight(self):
        '''
        Returns the diagonal weight matrix for hyperedge
        '''
        return self._edgeWeight

    def __init__(self, nodes=set(), hyperedges=set()):
        HyperGraph.__init__(self, nodes, hyperedges)
        self._nodeIdList = {}
        self._incMatHead = []
        self._incMatTail = []
        self._edgeWeight = []

    def printGraph(self):
        i = 1
        for h in self._hyperedges:
            print("Edge {}: Tail: {}, Head: {}, weight: {}".format(
                i, h.tail, h.head, h.weight))
            i += 1

    def add_hyperedgeByNames(self, head=set(), tail=set(), weight=0):
        '''
        Adds a hyperedge to the graph by node names.
        '''
        # Create hypergraph from current line
        hyperedge = HyperEdge(set(), set(), weight)

        # Read Tail nodes
        for t in tail:
            node = self.get_node_by_name(t)
            if (node is None):
                node = Node(t)
                self.add_node(node)
            hyperedge.tail.add(node)

        # Read Head nodes
        for h in head:
            node = self.get_node_by_name(h)
            if (node is None):
                node = Node(h)
                self.add_node(node)
            hyperedge.head.add(node)

        self.add_hyperedge(hyperedge)

    def read(self, fileName, sep='\t', delim=','):
        '''
            Read a directed hypergraph from file FileName
            each row is a hyperEdge.
            Tail, head and weight are separated by "sep"
            nodes within a hypernode are separated by "delim"
        '''
        fin = open(fileName, 'r')

        # read first header line
        fin.readline()
        i = 1
        for line in fin.readlines():
            line = line.strip('\n')
            if line == "":
                continue   # skip empty lines
            words = line.split(sep)
            if not (2 <= len(words) <= 3):
                raise Exception('File format error at line {}'.format(i))
            i += 1
            tail = words[0].split(delim)
            head = words[1].split(delim)
            try:
                weight = float(words[2].split(delim)[0])
            except:
                weight = 1

            # Create hypergraph from current line
            self.add_hyperedge(head, tail, weight)
        fin.close()

    def write(self, fileName, sep='\t', delim=','):
        '''
            write a directed hypergraph to file FileName
            each row is a hyperEdge.
            Tail, head and weight are separated by "sep"
            nodes within a hypernode are separated by "delim"
        '''
        fout = open(fileName, 'w')

        # write first header line
        fout.write("Tail" + sep + "Head" + sep + "weight\n")

        for e in self.hyperedges:
            line = ""
            for t in e.tail:
                line += t.name + delim
            line = line[:-1]    # remove last extra delim
            line += sep           # add separetor between columns
            for h in e.head:
                line += h.name + delim
            line = line[:-1]    # remove last extra delim
            line += sep + str(e.weight) + "\n"
            fout.write(line)
        fout.close()

    def symmetric_image(self):
        '''
        Returns a new hypergraph that is the
        symmetric image of this hypergraph
        '''
        nodes = deepcopy(self.nodes)
        hyperedges = deepcopy(self.hyperedges)
        for e in hyperedges:
            # TODO: put @property setters in hyperedge class?
            e._tail, e._head = e.head, e.tail
        # what if it's now a DirectedHyperArcGraph?
        return DirectedHyperGraph(nodes, hyperedges)

    def b_visit(self, s):
        '''
        Returns the set of all nodes that are B-Connected to s
        '''
        # TODO: implement B-Visit method
        pass

    def b_connection(self, s):
        '''
        Alias for b_visit
        '''
        return self.b_visit(s)

    def f_visit(self, s):
        '''
        Returns the set of all nodes that are F-Connected to node s
        '''
        symmetric_image = self.symmetric_image()
        s = symmetric_image.get_node_by_name(s.name)

        symmetric_b_visit = symmetric_image.b_visit(s)

        f_connected_node_names = self.get_node_names(symmetric_b_visit)
        return self.get_nodes_by_name(f_connected_node_names)

    def f_connection(self, s):
        '''
        Alias for f_visit
        '''
        return self.f_visit(s)

    def is_b_connected(self, *arg):
        '''
        Determines if a node is B-Connected to other nodes
        usage:
                1st argument is node 's'
                if 1 argument is provided:
                        determines if all nodes are B-Connected to 's'
                if 2 arguments are provided:
                        determines if the node 't' specified
                        by the 2nd argument is B-Connected to 's'
        '''
        if len(arg) == 1:
            s = arg[0]
            b_connected_nodes = self.b_visit(s)
            return b_connected_nodes == self.nodes
        elif len(arg) == 2:
            s = arg[0]
            t = arg[1]
            b_connected_nodes = self.b_visit(s)
            return t in b_connected_nodes
        else:
            raise ValueError(
                'Invalid number of arguments {}'.format(len(arg)))

    def is_f_connected(self, *arg):
        '''
        Determines if a node is F-Connected to other nodes
        usage:
                1st argument is node 's'
                if 1 argument is provided:
                        determines if all nodes are F-Connected to 's'
                if 2 arguments are provided:
                        determines if the node 't' specified by
                        the 2nd argument is F-Connected to 's'
        '''
        if len(arg) == 1:
            symmetric_image = self.symmetric_image()
            s = symmetric_image.get_node_by_name(arg[0].name)
            return symmetric_image.is_b_connected(s)
        elif len(arg) == 2:
            symmetric_image = self.symmetric_image()
            s = symmetric_image.get_node_by_name(arg[0].name)
            t = symmetric_image.get_node_by_name(arg[1].name)
            return symmetric_image.is_b_connected(t, s)
        else:
            raise ValueError(
                'Invalid number of arguments {}'.format(len(arg)))

    def build_incidence_matrix(self):
        '''
        Builds the incidence matrix with tail and head matrices
        usage:
                Pass the directed hypergraph
                Returns the head and tail incidence matrices
        '''
        edgeNum = len(self.hyperedges)
        nodeNum = len(self.nodes)

        incMatHead = np.zeros((nodeNum, edgeNum), dtype=int)
        incMatTail = np.zeros((nodeNum, edgeNum), dtype=int)

        hyperedgeId = 0
        nodeId = 0
        self.edgeWeight = np.zeros(edgeNum, dtype=int)
        for e in self.hyperedges:
            for n in e.head:
                if n.name not in self.nodeIdList:
                    self.nodeIdList[n.name] = nodeId
                    nodeId = nodeId + 1
                incMatHead[self.nodeIdList.get(n.name)][hyperedgeId] = 1
            for n in e.tail:
                if n.name not in self.nodeIdList:
                    self.nodeIdList[n.name] = nodeId
                    nodeId = nodeId + 1
                incMatTail[self.nodeIdList.get(n.name)][hyperedgeId] = 1
            self.edgeWeight[hyperedgeId] = e.weight
            hyperedgeId = hyperedgeId + 1
        self.H_minus = incMatHead
        self.H_plus = incMatTail

    def build_diagonal_node_matrix(self):
        '''
        Constructs the diagonal matrix for nodes
        '''
        if self.H_minus.shape == (0, 0):
            self.build_incidence_matrix(self)
        edgeNum = len(self.hyperedges)
        nodeNum = len(self.nodes)
        degreesPlus = np.zeros(nodeNum, dtype=int)
        degreesMinus = np.zeros(nodeNum, dtype=int)
        for row in xrange(nodeNum):
            for col in xrange(edgeNum):
                if self.H_plus[row][col] == 1:
                    degreesPlus[row] = degreesPlus[row] + self.edgeWeight[col]
                if self.H_minus[row][col] == 1:
                    degreesMinus[row] = degreesMinus[row] + \
                        self.edgeWeight[col]
        return np.diag(degreesMinus), np.diag(degreesPlus)

    def build_diagonal_edge_matrix(self):
        '''
        Constructs the diagonal matrix for hyperedges
        '''
        if self.H_minus.shape == (0, 0):
            self.build_incidence_matrix(self)
        degreesMinus = np.sum(self.H_minus, axis=0)
        degreesPlus = np.sum(self.H_plus, axis=0)
        return np.diag(degreesMinus), np.diag(degreesPlus)

    def build_diagonal_weight_matrix(self):
        '''
        Constructs the diagonal weight matrix for the hyperedges
        '''
        if self.H_minus.shape == (0, 0):
            self.build_incidence_matrix(self)
        return np.diag(self.edgeWeight)

    def build_transition_matrix(self):
        '''
        Constructs the P transition matrix for use in random walk algorithms
        Based on equation: P = D_{v^+}^{-1}H_+WD_{e^-}^{-1}H_-^T

        Usage:
            Will return P unless given dirhypergraph produces non-invertible
            degree node matrix, in which case P is empty
        '''
        D_v_minus, D_v_plus = self.build_diagonal_node_matrix()
        D_e_minus, D_e_plus = self.build_diagonal_edge_matrix()
        W = self.build_diagonal_weight_matrix()
        mainDiag = D_v_plus.diagonal()
        P = []
        for x in mainDiag:
            if x == 0:
                return P
        D_v_plus_inverse = np.linalg.inv(D_v_plus)
        D_e_minus_inverse = np.linalg.inv(D_e_minus)
        H_minus_transpose = self.H_minus.transpose()
        P = np.dot(D_v_plus_inverse, self.H_plus)
        P = np.dot(P, W)
        P = np.dot(P, D_e_minus_inverse)
        P = np.dot(P, H_minus_transpose)
        return P
