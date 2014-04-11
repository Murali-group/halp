from copy import deepcopy

from . import node
from . import hyperedge


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
        '''
        try:
            assert isinstance(n, node.Node)
        except AssertionError:
            raise ValueError('Invalid node %s' % n)

        self._nodes.add(node)

    def remove_hypernode(self, n):
        '''
        Removes a hypernode from the graph.

        Should this remove all of the connected edges as well?
        '''
        pass

    def add_hyperedge(self, h):
        '''
        Adds a hyperedge to the graph.
        '''

        try:
            assert isinstance(h, hyperedge.HyperEdge)
        except AssertionError:
            raise ValueError('Invalid hyperedge %s' % h)

        self._hyperedges.add(h)
        self._nodes.update(h.head)
        if isinstance(h.tail, set):
            self._nodes.update(h.tail)
        else:
            self._nodes.add(h.tail)

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


class DirectedHyperGraph(HyperGraph):
    pass


class DirectedHyperArcGraph(HyperGraph):
    pass


class UndirectedHyperGraph(HyperGraph):
    pass
