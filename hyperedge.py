from copy import deepcopy
from node import Node

class HyperEdge:

    def __init__(self, head=set(), tail=set(), weight=0):
        self._head = head
        self._weight = weight
        self._tail = tail

    @property
    def weight(self):
        '''
        Returns the weight of the edge
        '''
        return self._weight

    @property
    def tail(self):
        '''
        Returns the edge tail
        '''
        return self._tail

    @property
    def head(self):
        '''
        Returns the edge head
        '''
        return self._head

    def __contains__(self, n):
        '''
        Returns true if edge contains the node.
        '''
        try:
            return n in self.head() or n in self.tail()
        except TypeError:
            return False

    def copy(self):
        '''
        Returns a copy of the edge
        '''
        return deepcopy(self)


class DirectedHyperArc(HyperEdge):

    def __init__(self, head=set(), tail=None, weight=0):
        try:
            assert isinstance(tail, node.Node)
        except:
            raise ValueError("Invalid tail node %s", tail)
        HyperEdge.__init__(head, tail, weight)


class DirectedHyperEdge(HyperEdge):

    def __init__(self, head=set(), tail=set(), weight=0):
        HyperEdge.__init__(head, tail, weight)
