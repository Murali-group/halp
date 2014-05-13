from __future__ import absolute_import
from Queue import PriorityQueue
from collections import deque

from .hypergraph import HyperGraph
from copy import deepcopy

from .node import Node
from .hyperedge import HyperEdge, DirectedFHyperEdge, DirectedBHyperEdge

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
            eQueue.put((len(Q[e]),e))

        while len(vPrime) > 0:
            x = eQueue.get()
            a = x[1]
            #print "chose", a
            if len(Q[a]) == 0:
                continue
            v = next(iter(Q[a]))
            #print "     chose", v
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
            #print rootNodes
            eQueue = PriorityQueue()
            for e in ePrime:
                Q[e] = Q[e].difference(Q[a])
                if len(Q[e]) == 0:
                    import sys
                    MAX_VAL = sys.maxsize
                    eQueue.put((MAX_VAL, e))
                else:
                    eQueue.put((len(Q[e]),e))
        ordering.insert(0,rootNodes)
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

        for i in range(1,len(tree)):
            if i % 2 == 1:
                tree_edges.add(tree[i])
            else:
                non_root_nodes.add(tree[i])
                predecessor[tree[i]] = tree[i-1]

        ex_edges = self.hyperedges.difference(tree_edges)

        for node in root_nodes:
            flow[node] = 0

        for e in ex_edges:
            verts = e.head.union(e.tail)
            for v in verts:
                mult = 0
                if v in e.head:
                    mult = 1
                elif v in e.tail:
                    mult = - e.weight
                demand[v] = demand[v] - (mult*flow[e])

        unvisited = {}
        leaves = non_root_nodes
        for node in self.nodes:
            count = 0
            for e in tree_edges:
                if node in e.head.union(e.tail):
                    count += 1
                leaves = leaves.difference(e.tail)
            unvisited[node] = count

        queue = list(leaves)
        while queue.count != 0:
            v = queue.pop(0)
            e = predecessor[v]
            v_mult = 0
            if v in e.head:
                v_mult = 1
            elif v in e.tail:
                v_mult = e.weight
            flow[e] = demand[v] / v_mult
            for w in e.head.union(e.tail):
                if v == w:
                    continue
                if w in e.head:
                    w_mult = 1
                elif w in e.tail:
                    w_mult = e.weight
                demand[w] = demand[w] - w_mult * flow[e]
                unvisited[w] = unvisited[w] - 1
                if unvisited[w] == 1 and w not in root_nodes:
                    queue.append(w)
        for v in root_nodes:
            demand[v] = -1 * demand[v]

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
        for i in range(1,len(tree)):
            if i % 2 == 1:
                tree_edges.add(tree[i])
            else:
                non_root_nodes.add(tree[i])
                predecessor[tree[i]] = tree[i-1]

        ex_edges = self.hyperedges.difference(tree_edges)

        for e in ex_edges:
            cost[e] = 0

        for v in root_nodes:
            for e in self.hyperedges:
                if v in e.head.union(e.tail):
                    mult = 0
                    if v in e.head:
                        mult = 1
                    elif v in e.tail:
                        mult = - e.weight
                    cost[e] = cost[e] - (mult*potential[v])

        unvisited = {}
        branches = tree_edges
        for e in self.hyperedges:
            unvisited[e] = e.head.union(e.tail).intersection(non_root_nodes)
            if len(unvisited[e]) > 1:
                branches.remove(e)

        queue = list(branches)
        while queue.count != 0:
            e = queue.pop(0)
            v = unvisited[e].pop()
            e_mult = 0
            if v in e.head:
                e_mult = 1
            elif v in e.tail:
                e_mult = e.weight
            potential[v] = cost[e] / e_mult
            for f in e.hyperedges:
                if f == e:
                    continue
                f_mult = 0
                if v in f.head:
                    f_mult = 1
                elif v in f.tail:
                    f_mult = f.weight
                cost[f] = cost[f] - f_mult * potential[v]
                unvisited[f].remove(v)
                if len(unvisited[f]) == 1 and f not in ex_edges:
                    queue.append(f)
        for e in ex_edges:
            cost[e] = -1 * cost[e]

class DirectedBHyperTree(DirectedBHyperGraph):

    def __init__(self, rootNodes=set(), nonRootNodes=set(), hyperedges=set()):
        DirectedBHyperGraph.__init__(self, rootNodes.union(nonRootNodes), hyperedges)
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
            queue.append((n,set([n])))
        while len(queue) > 0:
            curNode, curPath = queue.popleft()
            for e in self.hyperedges:
                if curNode in e.tail:
                    for newNode in e.head:
                        print newNode, " from ", curNode, "(", curPath, ")"
                        if newNode in curPath:
                            return False
                        queue.appendleft((newNode,curPath.union(set([newNode]))))
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


