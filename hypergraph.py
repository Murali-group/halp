from copy import deepcopy

from node import Node
from hyperedge import HyperEdge


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
            assert isinstance(n, Node)
        except AssertionError:
            raise ValueError('Invalid node %s' % n)

        self._nodes.add(n)

    def get_node_by_name(self, nodeName):
        '''
        Get node by nodeName, otherwise returns None
        Node names should be unique
        '''
        for n in self.nodes:
            if n.name == nodeName:
                return n
        return None


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
            assert isinstance(h, HyperEdge)
        except AssertionError:
            #raise ValueError('Invalid hyperedge %s' % h)
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
    
    def printGraph(self):
        i = 1
        for h in self._hyperedges:
            print("Edge {}: Tail: {}, Head: {}".format(i, h.tail, h.head))
            i +=1


class DirectedHyperGraph(HyperGraph):
    pass


class DirectedHyperArcGraph(HyperGraph):
    pass


class UndirectedHyperGraph(HyperGraph):
    pass
