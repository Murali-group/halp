from __future__ import absolute_import


class DirectedHypergraph(object):

    def __init__(self):  # , hyperedges=None, node_ordering=None):
        self._node_attributes = {}
        self._hyperedge_attributes = {}
        self._forward_star = {}
        self._backward_star = {}
        self._successors = {}
        self._predecessors = {}
        self._assigned_hyperedges = 0

    @property
    def node_attributes(self):
        return self._node_attributes

    @node_attributes.setter
    def node_attributes(self, value):
        self._node_attributes = value

    @property
    def hyperedge_attributes(self):
        return self._hyperedge_attributes

    @hyperedge_attributes.setter
    def hyperedge_attributes(self, value):
        self._hyperedge_attributes = value

    @property
    def forward_star(self):
        return self._forward_star

    @forward_star.setter
    def forward_star(self, value):
        self._forward_star = value

    @property
    def backward_star(self):
        return self._backward_star

    @backward_star.setter
    def backward_star(self, value):
        self._backward_star = value

    @property
    def successors(self):
        return self._successors

    @successors.setter
    def successors(self, value):
        self._successors = value

    @property
    def predecessors(self):
        return self._predecessors

    @predecessors.setter
    def predecessors(self, value):
        self._predecessors = value

    def add_node(self, node, attr_dict=None, **attr):
        """Adds a node to the graph, along with any related attributes
           of the node.

        :param node: reference of the node.
        :param attr_dict: dictionary of attributes of the node.
        :param **attr: keyword arguments of attributes of the node; takes
                    precedence over attr_dict.
        :raises: AttributeError

        """
        # If no attribute dict was passed, treat the keyword
        # arguments as the dict
        if attr_dict is None:
            attr_dict = attr
        # Otherwise, combine the passed attribute dict with
        # the keyword arguments
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise AttributeError("attr_dict argument \
                                     must be a dictionary.")

        # If the node hasn't previously been added, add it along
        # with its attributes
        if node not in self.node_attributes:
            self.node_attributes[node] = attr_dict
            self.forward_star[node] = set()
            self.backward_star[node] = set()
        # Otherwise, just update the node's attributes
        else:
            self.node_attributes[node].update(attr_dict)

    def add_nodes(self, nodes, attr_dict=None, **attr):
        """Adds multiple nodes to the graph, along with any related attributes
            of the nodes.

        :param nodes: iterable container to either references of the nodes
                    OR tuples of (node reference, attribute dictionary); takes
                    precedence over attr_dict and **attr
        :param attr_dict: dictionary of attributes shared by all the nodes.
        :param **attr: keyword arguments of attributes of all the nodes; takes
                    precedence over attr_dict.
        :raises: AttributeError

        """
        # If no attribute dict was passed, treat the keyword
        # arguments as the dict
        if attr_dict is None:
            attr_dict = attr
        # Otherwise, combine the passed attribute dict with the
        # keyword arguments
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise AttributeError("attr_dict argument \
                                     must be a dictionary.")

        for node in nodes:
            # Note: This won't behave properly if the node is actually a tuple
            if type(node) is tuple:
                new_node, node_attr_dict = node
                # Create a new dictionary and load it with node_attr_dict and
                # attr_dict, with the former (node_attr_dict) taking precedence
                new_dict = attr_dict.copy()
                new_dict.update(node_attr_dict)
                self.add_node(new_node, new_dict)
            else:
                self.add_node(node, attr_dict.copy())

    def add_hyperedge(self, tail, head, attr_dict=None, **attr):
        """Adds hyperedges to the graph, along with any related attributes
            of the hyperedge.

        :param tail: iterable container of references to nodes in the
                    tail of the hyperedge to be added
        :param head: iterable container of references to nodes in the
                    head of the hyperedge to be added
        :param attr_dict: dictionary of attributes shared by all the nodes.
        :param **attr: keyword arguments of attributes of all the nodes; takes
                    precedence over attr_dict.
        :raises: AttributeError

        """
        # If no attribute dict was passed, treat the keyword
        # arguments as the dict
        if attr_dict is None:
            attr_dict = attr
        # Otherwise, combine the passed attribute dict with the
        # keyword arguments
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise AttributeError("attr_dict argument \
                                     must be a dictionary.")

        # Use frozensets for tail and head sets to allow for hashable keys
        frozen_tail = frozenset(tail)
        frozen_head = frozenset(head)

        if frozen_tail not in self.successors:
            self.successors[frozen_tail] = {}
        if frozen_head not in self.predecessors:
            self.predecessors[frozen_head] = {}

        is_new_hyperedge = frozen_head not in self.successors[frozen_tail]
        if is_new_hyperedge:
            # Add tail and head nodes to graph (if not already present)
            self.add_nodes(frozen_head)
            self.add_nodes(frozen_tail)

            # Create new hyperedge name to use as reference for that hyperedge
            self._assigned_hyperedges += 1
            hyperedge_name = "e" + str(self._assigned_hyperedges)

            # Add edge to the backward-star and to the forward-star for each
            # node in the tail and head sets, respectively
            for node in frozen_tail:
                self.backward_star[node].add(hyperedge_name)
            for node in frozen_head:
                self.forward_star[node].add(hyperedge_name)

            # Add the edge as the successors and predecessors of the tail set
            # and head set, respectively
            self.successors[frozen_tail][frozen_head] = hyperedge_name
            self.predecessors[frozen_head][frozen_tail] = hyperedge_name

            self.hyperedge_attributes[hyperedge_name] = \
                {'tail': tail, 'head': head}
        else:
            hyperedge_name = self.successors[frozen_tail][frozen_head]

        self.hyperedge_attributes[hyperedge_name].update(attr_dict)
