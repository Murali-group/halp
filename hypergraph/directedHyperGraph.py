from __future__ import absolute_import

from .hypergraph import HyperGraph
from copy import deepcopy

from .node import Node
from .hyperedge import HyperEdge, DirectedFHyperEdge, DirectedBHyperEdge

'''----------------------- Directed HyperGraph -----------------------------'''


class DirectedHyperGraph(HyperGraph):

    def __init__(self, nodes=set(), hyperedges=set()):
        HyperGraph.__init__(self, nodes, hyperedges)

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
                weight = 0

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


class DirectedBHyperGraph(DirectedHyperGraph):

    def __init__(self, nodes=set(), hyperedges=set()):
        HyperGraph.__init__(self, nodes, hyperedges)
        try:
            for e in hyperedges:
                assert isinstance(e, DirectedBHyperEdge)
        except:
            raise ValueError("Invalid b-hyperedge set")



class DirectedBHyperTree(DirectedBHyperGraph):

    def __init__(self, rootNodes=set(), nonRootNodes=set(), hyperedges=set()):
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
        self.rootNodes = rootNodes
        self.nonRootNodes = nonRootNodes
        DirectedBHyperGraph.__init__(self, rootNodes.union(nonRootNodes), hyperedges)

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
