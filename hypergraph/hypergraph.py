from __future__ import absolute_import

from copy import deepcopy

from .node import Node
from .hyperedge import HyperEdge, UndirectedHyperEdge


class HyperGraph:

    def __init__(self, nodes=set(), hyperedges=set()):
        self._nodes = nodes
        self._hyperedges = hyperedges

    @property
    def nodes(self):
        '''
        Returns the nodes of the graph
        '''
        return self._nodes

    @property
    def hyperedges(self):
        '''
        Returns the edges of the graph.
        '''
        return self._hyperedges

    def add_node(self, n):
        '''
            Adds a node to the graph.
            Can be called with node object or with node name
            This method chooses the right function to call to hide
            this task from the user.
            usage:
                graph.add_node(nodeObject)
            or
                graph.add_node('x1')
        '''
        if (isinstance(n, Node)):
            self.__add_node_by_object(n)
        elif (isinstance(n, str)):
            self.__add_node_by_name(n)
        else:
            raise ValueError(
                'Invalid arguments type{}'.format(n))

    def __add_node_by_name(self, nodeName):
        '''
            Add a node given the node name
        '''
        if (self.get_node_by_name(nodeName) is None):
            self.nodes.add(Node(nodeName))
        else:
            raise Exception(
                'Node not added, Duplicate Node name: {}'.format(nodeName))

    def __add_node_by_object(self, n):
        '''
        Adds a node Object to the graph.
        '''
        try:
            assert isinstance(n, Node)
        except AssertionError:
            raise ValueError('Invalid node {}'.format(n))

        if (self.get_node_by_name(n.name) is None):
            self.nodes.add(n)
        else:
            raise Exception(
                'Node not added, Duplicate Node name: {}'.format(n.name))

    def get_node_by_name(self, nodeName):
        '''
        Get node by nodeName, otherwise returns None
        Node names should be unique
        '''
        for n in self.nodes:
            if n.name == nodeName:
                return n
        return None

    def get_nodes_by_name(self, node_names):
        '''
        Takes a set of names and returns the corresponding set of node objects
        '''
        node_set = set()
        for node in self.nodes:
            if node.name in node_names:
                node_set.add(node)
        return node_set

    def get_node_names(self):
        '''
        Helper function to return the names of all the nodes in the graph
        '''
        name_set = set()
        for node in self.nodes:
            name_set.add(node.name)
        return name_set

    def remove_hypernode(self, n):
        '''
        Removes a hypernode from the graph.

        Should this remove all of the connected edges as well?
        '''
        pass

    ''' ------------------------------------------------------ '''

    def add_hyperedge(self, *args):
        '''
        Adds a hyperedge to the graph.
        Can be called with HyperEdge object or with edge names
        This method chooses the right class to call to hide this task
        complexity from the user.
        usage:
            graph.add_hypergraph(hypergraph)
        or
            directedGraph.add_hypergraph(head, tail, weight)
            where:
                head = {'x1', 'x2', ...}
                tail = {'x4', 'x6', ...}
         or
            undirectedGraph.add_hypergraph(nodes, weight)
            where:
                nodes = {'x1', 'x2', ...}
        '''
        if (len(args) == 1):
            if (isinstance(args[0], HyperEdge)):
                self.add_hyperedgeByObject(args[0])
            else:
                self.add_hyperedgeByNames(args[0])
        elif (len(args) == 2):
            self.add_hyperedgeByNames(args[0], args[1])
        elif (len(args) == 3):
            self.add_hyperedgeByNames(args[0], args[1], args[2])
        else:
            raise ValueError(
                'Invalid number of arguments {}'.format(len(args)))

    def add_hyperedgeByNames(self, **args):
        '''
            Add a hypergraph given the nodes names of the edge
            implimented in directed/undirected classes
        '''
        pass

    def add_hyperedgeByObject(self, h):
        '''
        Adds a hyperedge to the graph as a class h of HyperEdge.
        '''
        try:
            assert isinstance(h, HyperEdge)
        except AssertionError:
            # raise ValueError('Invalid hyperedge %s' % h)
            raise ValueError('Invalid hyperedge {}'.format(h))

        self._hyperedges.add(h)
        '''
        # nodes will be already be added before the edge
        self._nodes.update(h.head)
        if isinstance(h.tail, set):
            self._nodes.update(h.tail)
        else:
            self._nodes.add(h.tail)
        '''

    def remove_hyperedge(self, h):
        '''
        Removes a hyperedge from the graph
        '''
        self.hyperedges.remove(h)

    def copy(self):
        '''
        Returns a copy of the graph
        '''
        return deepcopy(self)

    def read(self):
        pass

    def write(self):
        pass

    def printGraph(self):
        pass


class DirectedHyperArcGraph(HyperGraph):
    pass
