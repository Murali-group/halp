from __future__ import absolute_import
try:
    from queue import PriorityQueue
except ImportError:
    from Queue import PriorityQueue
from collections import deque

import numpy
from numpy.linalg import inv
import numpy as np

from tempfile import TemporaryFile
# from tempfile import imkdtemp
# import os.path as path

from operator import attrgetter

from .hypergraph import HyperGraph
from copy import deepcopy

from .node import Node
from .hyperedge import DirectedHyperEdge
from .hyperedge import DirectedFHyperEdge, DirectedBHyperEdge
from .hyperedge import HyperEdge


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
        hyperedge = DirectedHyperEdge(set(), set(), weight)

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

    def add_hyperedgeByObject(self, he):
        for t in he.tail:
            self.add_node(t)
        for h in he.head:
            self.add_node(h)
        self._hyperedges.add(he)

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
    
    def FS(self, v):
        '''
        Returns the Forward Star set of edges for the vertex v
        which is the set of edges that v is in the tail of
        '''
        return set([e for e in self.hyperedges if v in e.tail])

    def BS(self, v):
        '''
        Returns the Backward Star set of edges for the vertex v
        which is the set of edges that v is in the head of
        '''
        return set([e for e in self.hyperedges if v in e.head])

    def b_visit(self, s):
        '''
        Returns the set of all nodes that are B-Connected to s
        '''
        # TODO: decide what to do with the predecessor functions
        connected = set()
        Pv = {i: None for i in self.nodes}
        Pe = {i: None for i in self.hyperedges}
        B = {i: 0 for i in self.hyperedges}

        Pv[s] = 0
        connected.add(s)
        Q=[s]
        while Q:
            v = Q.pop(0)
            for e in self.FS(v):
                B[e] += 1
                if B[e] == len(e.tail):
                    Pe[e] = v
                    for h in [x for x in e.head if Pv[x] == None]:
                        Pv[h] = e
                        Q.append(h)
                        connected.add(h)
        return connected

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

    def SBT(self, s, F):
        '''
        Performs the SBT (Shortest B-Tree) algorithm from the 
        Directed hypergraphs and applications paper
        '''
        W = {i: float('inf') for i in self.nodes}
        Pv = {i: None for i in self.nodes}
        B = {e: 0 for e in self.hyperedges}

        Q = [s]
        W[s] = 0 
        while Q:
            u = Q.pop(Q.index(min(Q, key=lambda node: W[node])))
            for e in self.FS(u): 
                B[e] += 1
                if B[e] == len(e.tail):
                    f = F(e, W)
                    for y in [n for n in e.head if W[n] > e.weight + f]:
                        if y not in Q:
                            Q.append(y)
                            if W[y] < float('inf'): 
                                for eh in self.FS(self, y):
                                    B[eh] -= 1
                        W[y] = e.weight + f
                        Pv[y] = e
        return W

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
        self._nodeIdList = {}
        self._edgeWeight = np.zeros(edgeNum, dtype=int)
        for e in self.hyperedges:
            for n in e.head:
                if n.name not in self._nodeIdList:
                    self._nodeIdList[n.name] = nodeId
                    nodeId = nodeId + 1
                incMatHead[self._nodeIdList.get(n.name)][hyperedgeId] = 1
            for n in e.tail:
                if n.name not in self._nodeIdList:
                    self._nodeIdList[n.name] = nodeId
                    nodeId = nodeId + 1
                incMatTail[self._nodeIdList.get(n.name)][hyperedgeId] = 1
            self._edgeWeight[hyperedgeId] = e.weight
            hyperedgeId = hyperedgeId + 1
        self._H_minus = incMatHead
        self._H_plus = incMatTail

    def build_diagonal_node_matrix(self):
        '''
        Constructs the diagonal matrix for nodes
        '''
        if self._H_minus.shape == (0, 0):
            self.build_incidence_matrix(self)
        edgeNum = len(self.hyperedges)
        nodeNum = len(self.nodes)
        degreesPlus = np.zeros(nodeNum, dtype=int)
        degreesMinus = np.zeros(nodeNum, dtype=int)
        for row in range(nodeNum):
            for col in range(edgeNum):
                if self._H_plus[row][col] == 1:
                    degreesPlus[row] = degreesPlus[row] + self._edgeWeight[col]
                if self._H_minus[row][col] == 1:
                    degreesMinus[row] = degreesMinus[row] + \
                        self._edgeWeight[col]
        return np.diag(degreesMinus), np.diag(degreesPlus)

    def build_diagonal_edge_matrix(self):
        '''
        Constructs the diagonal matrix for hyperedges
        '''
        if self._H_minus.shape == (0, 0):
            self.build_incidence_matrix(self)
        degreesMinus = np.sum(self._H_minus, axis=0)
        degreesPlus = np.sum(self._H_plus, axis=0)
        return np.diag(degreesMinus), np.diag(degreesPlus)

    def build_diagonal_weight_matrix(self):
        '''
        Constructs the diagonal weight matrix for the hyperedges
        '''
        if self._H_minus.shape == (0, 0):
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
        H_minus_transpose = self._H_minus.transpose()
        P = np.dot(D_v_plus_inverse, self._H_plus)
        P = np.dot(P, W)
        P = np.dot(P, D_e_minus_inverse)
        P = np.dot(P, H_minus_transpose)
        return P


class DirectedBHyperGraph(DirectedHyperGraph):

    def __init__(self, nodes=set(), hyperedges=set()):
        HyperGraph.__init__(self, nodes, hyperedges)
        try:
            for e in hyperedges:
                assert isinstance(e, DirectedBHyperEdge)
        except:
            raise ValueError("Invalid b-hyperedge set")

    def add_hyperedgeByNames(self, head=set(), tail=set(), weight=0):
        '''
        Adds a hyperedge to the graph by node names.
        '''
        # Create hypergraph from current line
        hyperedge = DirectedBHyperEdge(set(), set(), weight)

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

    def get_spanning_hypertree(self):
        rootNodes = set()
        nonRootNodes = set()
        ordering = []
        vPrime = self.nodes.copy()
        ePrime = self.hyperedges.copy()
        eQueue = PriorityQueue()
        Q = dict()
        for e in self.hyperedges:
            Q[e] = e.head.union(e.tail)
            eQueue.put((len(Q[e]), e))

        while len(vPrime) > 0:
            x = eQueue.get()
            a = x[1]
            # print "chose", a
            if len(Q[a]) == 0:
                continue
            v = next(iter(Q[a]))
            # print "     chose", v
            if len(Q[a]) == 1:
                nonRootNodes.add(v)
                if v in vPrime:
                    vPrime.remove(v)
            else:
                rootNodes = rootNodes.union(Q[a].difference([v]))
                nonRootNodes.add(v)
                vPrime = vPrime.difference(Q[a])
            ordering.append(a)
            ordering.append(v)
            ePrime.remove(a)
            # print rootNodes
            eQueue = PriorityQueue()
            for e in ePrime:
                Q[e] = Q[e].difference(Q[a])
                if len(Q[e]) == 0:
                    import sys
                    MAX_VAL = sys.maxsize
                    eQueue.put((MAX_VAL, e))
                else:
                    eQueue.put((len(Q[e]), e))
        ordering.insert(0, rootNodes)
        return ordering

    def flow(self, tree, demand, flow):
        '''
        Given a demand vector for non-root nodes,
        a flow vector for external edges, and a
        spanning tree, this function returns a flow
        on tree edges and the root demand/supply.
        '''
        assert len(tree) > 0
        # Get root and non root nodes
        root_nodes = tree[0]
        non_root_nodes = set()
        tree_edges = set()
        predecessor = {}

        for i in range(1, len(tree)):
            if i % 2 == 1:
                tree_edges.add(tree[i])
            else:
                non_root_nodes.add(tree[i])
                predecessor[tree[i]] = tree[i - 1]

        ex_edges = self.hyperedges.difference(tree_edges)

        for node in root_nodes:
            demand[node] = 0

        for e in ex_edges:
            verts = e.head.union(e.tail)
            for v in verts:
                mult = 0
                if v in e.head:
                    mult = 1
                    demand[v] = demand[v] - (mult * flow[e])
                elif v in e.tail:
                    mult = -1 * e.weight
                    demand[v] = demand[v] - (mult * flow[e])

        unvisited = {}
        leaves = set()
        for node in self.nodes:
            count = 0
            for e in tree_edges:
                if node in e.head.union(e.tail):
                    count += 1
            if count == 1:
                leaves.add(node)
            unvisited[node] = count

        queue = list(leaves)
        while len(queue) != 0:
            v = queue.pop(0)
            e = predecessor[v]
            v_mult = 0
            if v in e.head:
                v_mult = 1
            elif v in e.tail:
                v_mult = -1 * e.weight
            flow[e] = demand[v] / v_mult
            for w in e.head.union(e.tail):
                if v == w:
                    continue
                if w in e.head:
                    w_mult = 1
                elif w in e.tail:
                    w_mult = -1 * e.weight
                demand[w] = demand[w] - w_mult * flow[e]
                unvisited[w] = unvisited[w] - 1
                if unvisited[w] == 1 and w not in root_nodes:
                    queue.append(w)
        for v in root_nodes:
            demand[v] = -1 * demand[v]
        return demand, flow

    def potential(self, tree, cost, potential):
        '''
        Given a cost vector for tree edges,
        a potential vector for root nodes, and a
        spanning tree, this function returns a potential
        on non-root nodes and a cost of external edges.
        '''
        assert len(tree) > 0
        # Get root and non root nodes
        root_nodes = tree[0]
        non_root_nodes = set()
        tree_edges = set()
        predecessor = {}
        for i in range(1, len(tree)):
            if i % 2 == 1:
                tree_edges.add(tree[i])
            else:
                non_root_nodes.add(tree[i])
                predecessor[tree[i]] = tree[i - 1]

        ex_edges = self.hyperedges.difference(tree_edges)

        for e in ex_edges:
            cost[e] = 0

        for v in root_nodes:
            for e in self.hyperedges:
                if v in e.head.union(e.tail):
                    mult = 0
                    if v in e.head:
                        mult = 1
                        cost[e] = cost[e] - (mult * potential[v])
                    elif v in e.tail:
                        mult = -1 * e.weight
                        cost[e] = cost[e] - (mult * potential[v])

        unvisited = {}
        branches = tree_edges.copy()
        for e in tree_edges:
            unvisited[e] = e.head.union(e.tail).intersection(non_root_nodes)
            if len(unvisited[e]) > 1:
                branches.remove(e)

        queue = list(branches)
        while len(queue) != 0:
            e = queue.pop(0)
            v = unvisited[e].pop()
            e_mult = 0
            if v in e.head:
                e_mult = 1
            elif v in e.tail:
                e_mult = -1 * e.weight
            potential[v] = cost[e] / e_mult
            for f in self.hyperedges:
                if f == e:
                    continue
                if v not in f.head.union(f.tail):
                    continue
                f_mult = 0
                if v in f.head:
                    f_mult = 1
                elif v in f.tail:
                    f_mult = -1 * f.weight
                cost[f] = cost[f] - (f_mult * potential[v])
                if f in unvisited:
                    unvisited[f].remove(v)
                    if len(unvisited[f]) == 1 and f not in ex_edges:
                        queue.append(f)
        for e in ex_edges:
            cost[e] = -1 * cost[e]

        return cost, potential


class DirectedBHyperTree(DirectedBHyperGraph):

    def __init__(self, rootNodes=set(), nonRootNodes=set(), hyperedges=set()):
        DirectedBHyperGraph.__init__(
            self,
            rootNodes.union(nonRootNodes),
            hyperedges)
        self.rootNodes = rootNodes
        self.nonRootNodes = nonRootNodes
        try:
            assert len(rootNodes.intersection(nonRootNodes)) == 0
        except:
            raise ValueError("Root and non-root set are not disjoint")
        try:
            for r in rootNodes:
                for e in r.inList:
                    assert e not in hyperedges
        except:
            raise ValueError("Invalid root set of nodes")
        try:
            for n in nonRootNodes:
                assert len(n.inList) == 1
        except:
            raise ValueError("Invalid non-root set of nodes")
        try:
            assert self.isCycleFree()
        except:
            raise ValueError("Hypertree is not cycle-free")

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
            if words[0] == "R":
                nodes = words[1].split(delim)
                self.define_root_nodes(nodes)
                break
            if not (2 <= len(words) <= 3):
                raise Exception('File format error at line {}'.format(i))
            i += 1
            tail = words[0].split(delim)
            head = words[1].split(delim)
            try:
                weight = float(words[2].split(delim)[0])
            except:
                weight = 0

            # Create hypergraph from current line
            self.add_hyperedge(head, tail, weight)
        fin.close()
        try:
            assert self.isCycleFree()
        except:
            raise ValueError("Hypertree is not cycle-free")

    def isCycleFree(self):
        queue = deque([])
        for n in self.rootNodes:
            queue.append((n, set([n])))
        while len(queue) > 0:
            curNode, curPath = queue.popleft()
            for e in self.hyperedges:
                if curNode in e.tail:
                    for newNode in e.head:
                        if newNode in curPath:
                            return False
                        queue.appendleft(
                            (newNode, curPath.union(set([newNode]))))
        return True

    def define_root_nodes(self, nodes):
        for node in nodes:
            self.rootNodes.add(self.get_node_by_name(node))
        self.nonRootNodes = self.nodes.difference(self.rootNodes)

    def visitHyperTree(self):
        '''
        This is the VISIT(T_R) function from the "Flows on Hypergraphs" paper
        '''
        ordering = [self.rootNodes]
        vPrime = self.rootNodes.copy()
        ePrime = self.hyperedges.copy()
        edgesUsed = 1
        while edgesUsed > 0:
            edgesUsed = 0
            ePrimeCopy = ePrime.copy()
            for e in ePrimeCopy:
                if e.tail.issubset(vPrime):
                    ePrime.remove(e)
                    ordering.append(e)
                    ordering.append(next(iter(e.head)))
                    vPrime = vPrime.union(e.head)
                    edgesUsed += 1
                    break
        return ordering


class DirectedFHyperGraph(DirectedHyperGraph):

    def __init__(self, nodes=set(), hyperedges=set()):
        try:
            for e in hyperedges:
                assert isinstance(e, DirectedFHyperEdge)
        except:
            raise ValueError("Invalid f-hyperedge set")
        HyperGraph.__init__(self, nodes, hyperedges)

    def __gen_diagnonal_matrix(self, xs, dtype='float16'):
        M = numpy.memmap(TemporaryFile(), dtype=dtype,
                         mode='w+', shape=(len(xs), len(xs)))
        for i, x in enumerate(xs):
            M[i, i] = x
        return M

    def __incidence_matrix(self, vs, hes, ag):
        M = numpy.memmap(TemporaryFile(), dtype='uint8',
                         mode='w+', shape=(len(vs), len(hes)))

        def incidence_row(v):
            return [int(v in ag(he)) for he in hes]

        for i, v in enumerate(vs):
            M[i, :] = incidence_row(v)
        return M

    def incidence_matrices(self, ns, hes):
        return (self.__incidence_matrix(ns, hes, attrgetter('tail')),
                self.__incidence_matrix(ns, hes, attrgetter('head')))

    def __vertex_degree(self, v, hes, ag):
        weights = (he.weight for he in hes if v in ag(he))
        return sum(weights)

    def __vertex_degree_matrix(self, hes, ag):
        return self.__gen_diagnonal_matrix(
            [self.__vertex_degree(v, hes, ag) for v in self.nodes])

    def positive_vertex_degree_matrix(self, hes):
        return self.__vertex_degree_matrix(hes, attrgetter('tail'))

    def negative_edge_degree_matrix(self, hes):
        len_heads = [len(he.head) for he in hes]
        return self.__gen_diagnonal_matrix(len_heads, 'uint8')

    def weight_matrix(self, hes):
        return self.__gen_diagnonal_matrix([he.weight for (he, e) in hes])

    def _transition_matrix(self):
        hes = sorted(self.hyperedges)
        ns = self.nodes
        H_tail, H_head = self.incidence_matrices(ns, hes)
        print "Computed incidence matrices"

        D_v_tail = self.positive_vertex_degree_matrix(hes)
        print "Computed + vertex matrix"

        D_e_head = self.edge_degree_matrices(hes)
        print "Computed - edge matrix"

        W = self.weight_matrix(hes)
        print "Computed weight matrix"

        P = numpy.memmap(TemporaryFile(), dtype='float16',
                         mode='w+', shape=(len(ns), len(ns)))
        P1 = numpy.memmap(TemporaryFile(), dtype='float16',
                          mode='w+', shape=(len(ns), len(hes)))
        P2 = numpy.memmap(TemporaryFile(), dtype='float16',
                          mode='w+', shape=(len(hes), len(hes)))

        print "Allocated temp matrices"

        # VxV * VxE = VxE
        numpy.dot(inv(D_v_tail), H_tail, out=P1)
        print "1"

        # ExE * ExE = ExE
        numpy.dot(W, inv(D_e_head), out=P2)
        print "2"

        # VxE * ExE = VxE
        numpy.dot(P1, P2, out=P2)
        print "3"

        # VxE * ExV = VxV
        numpy.dot(P2, H_head.T, out=P)
        return P

    def __transition_value(self, hes, ns, i, j):
        valSum = 0
        vertex_degree = self.__vertex_degree(ns[i], hes, attrgetter('tail'))
        for he in hes:
            val = he.weight * int(ns[i] in he.tail)
            val /= vertex_degree
            val *= int(ns[j] in he.head) / len(he.head)
            valSum += val
        return valSum

    def transition_matrix(self):
        hes = sorted(self.hyperedges)
        if self.node_ordering is None:
            self.node_ordering = id
        ns = self.nodes
        len_ns = len(self.nodes)
        # filename = path.join(mkdtemp(), 'transition_matrix.dat')
        # P = numpy.memmap(filename, dtype='float32',
        #                 mode='w+', shape=(len_ns, len_ns))
        P = numpy.zeros((len_ns, len_ns))
        if self.node_ordering is None:
            self.node_ordering = id
        for i in xrange(len_ns):
            for j in xrange(len_ns):
                P[i, j] = self.__transition_value(hes, ns, i, j)
            print i
        return P
