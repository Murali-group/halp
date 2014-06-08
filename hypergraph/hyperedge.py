"""
.. module:: hyperedge
   :synopsis: Defines the base "parent" Hyperedge class, as well as all other
              subclasses that are specific types of hyperedges

"""

from __future__ import absolute_import
from copy import deepcopy


class Hyperedge:
    """
    Hyperedge class provides the basic structure underlying hyperedges as well
    as the basic methods to access their fundamental properties.

    .. note::
    Although it implicitly models a directed hyperedge since it contains a
    head and tail node set, it is still used as the parent class for the
    UndirectedHyperedge class by ignoring the tail node set.
    Thus, Hyperedge can be used either as a directed or an
    undirected hyperedge.

    """

    def __init__(self, head=set(), tail=set(), weight=0):
        """
        Hyperedge class constructor.
        :param head: set of nodes in the head of the hyperedge.
        :type head: set.
        :param tail: set of nodes in the tail of the hyperedge.
        :type tail: set.
        :param weight: weight of the hyperedge.
        :type weight: int.

        """

        self._head = head
        self._tail = tail
        self._weight = weight

    @property
    def head(self):
        """
        Returns the head set of the hyperedge.
        :returns: set -- set of nodes in the head of the hyperedge.

        """

        return self._head

    @head.setter
    def head(self, value):
        """
        Sets the head of the hyperedge.
        :param value: node-set to set as the head of the hyperedge.
        :type value: set.

        """

        self._head = value

    @property
    def tail(self):
        """
        Returns the tail set of the hyperedge.
        :returns: set -- set of nodes in the tail of the hyperedge.

        """

        return self._tail

    @tail.setter
    def tail(self, value):
        """
        Sets the tail of the hyperedge
        :param value: node-set to set as the tail of the hyperedge.
        :type value: set.

        """

        self._tail = value

    @property
    def weight(self):
        """
        Returns the weight of the hyperedge.
        :returns: int -- weight of this hyperedge.

        """

        return self._weight

    @weight.setter
    def weight(self, value):
        """
        Sets the weight of the hyperedge.
        :param value: weight to set the hyperedge.
        :type value: int.

        """

        self._weight = value

    def cardinality(self):
        """
        Returns the total number of nodes in the hyperedge.
        :returns: int -- sum of the cardinalies of the head and tail sets.

        """

        return self.cardinalityHead() + self.cardinalityTail()

    def cardinalityHead(self):
        """
        Returns the total number of nodes in the head of the hyperedge.
        :returns: int -- cardinality of the head set.

        """

        return len(self._head)

    def cardinalityTail(self):
        """
        Returns the total number of nodes in the tail of this hyperedge.
        :returns: int -- cardinality of the tail set.

        """

        return len(self._tail)

    def copy(self):
        """
        Returns a deep copy of the hyperedge (consequently, its member nodes).
        :returns: Hyperedge -- deep copy of the hyperedge.

        """

        return deepcopy(self)

    def __contains__(self, n):
        """
        Returns whether the hyperedge contains a specific node n.
        :returns: bool -- does the hyperedge contain node n

        """

        try:
            return n in self.head() or n in self.tail()
        except TypeError:
            # TODO: consider allowing n to be the name (string) of the node
            return False

    def __str__(self):
        """
        Returns overriden Hyperedge to-string as:
            head: str(head_set) tail: str(tail_set) hyperedge_weight
        :returns: str -- hyperedge representation string.

        """

        return "head:" + str(self._head) + " tail:" + \
            str(self._tail) + " weight: " + str(self._weight)
        #return 'Tail: %s, Head: %s, weight: %s' % (self._tail, self._head,
        #                                           self._weight)

    def __repr__(self):
        """
        Returns overriden Hyperedge representation to be equivalent to __str__.
        :returns: str -- hyperedge representation as __str__.

        """

        return str(self)
        #return str((self._head,  self._tail, self._weight))

    def __lt__(self, other):
        """
        Returns overriden Hyperedge less-than to compare on weight.
        :returns: bool -- whether self.weight < other.weight.

        """

        return self.weight < other.weight

    def __gt__(self, other):
        """
        Returns overriden Hyperedge greater-than to compare on weight.
        :returns: bool -- whether self.weight > other.weight.

        """

        return self.weight > other.weight

    def __le__(self, other):
        """
        Returns overriden Hyperedge less-than-or-equals to compare on weight.
        :returns: bool -- whether self.weight <= other.weight.

        """

        return self.weight <= other.weight

    def __ge__(self, other):
        """
        Returns overriden Hyperedge greater-than-or-equals to compare
        on weight.
        :returns: bool -- whether self.weight >= other.weight.

        """

        return self.weight >= other.weight


class DirectedHyperedge(Hyperedge):
    """
    Extension of the Hyperedge class to explicitly signal the use of a
    directed hyperedge; used for all algorithms on directed hypergraphs.

    """

    def __init__(self, head=set(), tail=set(), weight=0):
        """
        DirectedHyperedge class constructor.
        :param head: set of nodes in the head of the hyperedge.
        :type head: set.
        :param tail: set of nodes in the tail of the hyperedge.
        :type tail: set.
        :param weight: weight of the hyperedge.
        :type weight: int.

        """

        Hyperedge.__init__(self, head, tail, weight)

    def __eq__(self, other):
        """
        Returns overriden DirectedHyperedge equality to be true iff both the
        head sets and both the tail sets are equal.
        :returns: bool -- whether hyperedges are equal based on head
                          and tail sets.

        """

        return self.head == other.head and self.tail == other.tail

    def __hash__(self):
        """
        Returns overriden DirectedHyperedge hash to be its cardinality.
        :returns: int -- hash of the node object.

        """

        # TODO: choose a better hash function
        return self.cardinality()


class BHyperedge(DirectedHyperedge):
    """
    Extension of the DirectedHyperedge class to explicitly signal the use of a
    B-hyperedge (that is, the head set contains only a single node); used for
    all algorithms on B-hypergraphs.

    """

    def __init__(self, head, tail=set(), weight=0):
        """
        BHyperedge class constructor.
        :param head: set containing the node in the head of the hyperedge.
        :type head: set.
        :param tail: set of nodes in the tail of the hyperedge.
        :type tail: set.
        :param weight: weight of the hyperedge.
        :type weight: int.

        """

        try:
            if (head is None):
                head = set()
            if (type(head) is not set):
                head = set(head)
            assert len(head) <= 1
        except:
            raise ValueError("Invalid hyperedge head", head)

        Hyperedge.__init__(self, head, tail, weight)


class FHyperedge(DirectedHyperedge):
    """
    Extension of the DirectedHyperedge class to explicitly signal the use of an
    F-hyperedge (that is, the tail set contains only a single node); used for
    all algorithms on F-hypergraphs.

    """

    def __init__(self, head=set(), tail=None, weight=0):
        """
        FHyperedge class constructor.
        :param head: set of nodes in the head of the hyperedge.
        :type head: set.
        :param tail: set containing the node in the tail of the hyperedge.
        :type tail: set.
        :param weight: weight of the hyperedge.
        :type weight: int.

        """

        try:
            if (tail is None):
                tail = set()
            if (type(tail) is not set):
                tail = set(tail)
            assert len(tail) <= 1
        except:
            raise ValueError("Invalid hyperedge tail", tail)

        Hyperedge.__init__(self, head, tail, weight)


class UndirectedHyperedge(Hyperedge):
    '''
    Extension of the Hypergraph class to explicitly signal the use of an
    undirected hyperedge (a single set of connected nodes); used for all
    algorithms on undirected hypergraphs.

    Since the Hypergraph class contains a head and tail set for nodes,
    undirectedness is accomplished by ignoring the (empty) tail set and
    storing all nodes in the head set, which is referred to as "nodes".
    Then, head- and tail-specific properties are disabled by raising exceptions
    when called.

    '''

    def __init__(self, nodes=set(), weight=0):
        """
        UndirectedHyperedge class constructor.
        :param nodes: set of nodes in the hyperedge.
        :type head: set.
        :param weight: weight of the hyperedge.
        :type weight: int.

        """

        Hyperedge.__init__(self, nodes, set(), weight)

    @property
    def nodes(self):
        """
        Returns the hyperedge's nodes
        :returns: set -- set of nodes in the hyperedge

        """

        return self._head

    @nodes.setter
    def nodes(self, value):
        """
        Sets the node-set of the hyperedge.
        :param value: nodes to set as the node-set of the hyperedge.
        :type value: set.

        """

        self._head = value

    @property
    def head(self):
        # TODO: also disable head setter?
        """
        Disables head getter
        :raises: AttributeError

        """

        raise AttributeError("Undirected hyperedges have no head attribute")

    @property
    def tail(self):
        # TODO: also disable tail setter?
        """
        Disables tail getter
        :raises: AttributeError

        """

        raise AttributeError("Undirected hyperedges have no tail attribute")

    '''
    def __str__(self):
    	"""
        Returns overriden Hyperedge to-string as:
            head: str(head_set) tail: str(tail_set) hyperedge_weight
        :returns: str -- hyperedge representation string.
        """

        return 'nodes: %s, weight: %s' % (self._nodes, self._weight)

    def __repr__(self):
    	"""
        Returns overriden Hyperedge representation to be equivalent to __str__.
        :returns: str -- hyperedge representation as __str__.

        """

        return str((self.nodes, self.weight))
    '''

    def __eq__(self, other):
        """
        Returns overriden UndirectedHyperedge equality to be true iff both the
        node-sets and weights are the same
        :returns: bool -- whether hyperedges are equal based on node-sets
                          and weights

        """

        return (self.nodes == other.nodes) and (self.weight == other.weight)

    def __hash__(self):
        """
        Returns overriden UndirectedHyperedge hash to be its cardinality.
        :returns: int -- hash of the node object.

        """

        # TODO: choose a better hash function
        return len(self.nodes)
