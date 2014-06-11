"""
.. module:: directed_hypergraph
   :synopsis: Defines DirectedHypergraph class for the basic properties
            of a directed hypergraph, along with the relevant structures
            regarding nodes, hyperedges, adjacency, etc.

"""

from __future__ import absolute_import


class DirectedHypergraph(object):
    """
    DirectedHypergraph class provides a basic directed hypergraph object
    and typical functions for the basic properties of the structure.

    TODO: Put a lot of information here about the structures (mostly the
        ones instantiated by the constuctor).

    """

    def __init__(self):  # , hyperedges=None, node_ordering=None):
        """
        Constructor for the DirectedHypergraph class.

        """
        self._node_attributes = {}
        self._hyperedge_attributes = {}
        self._forward_star = {}
        self._backward_star = {}
        self._successors = {}
        self._predecessors = {}
        self._assigned_hyperedges = 0

    def _combine_attribute_arguments(self, attr_dict, attr):
        """Combines attr_dict and attr dictionaries, by updating attr_dict
            with attr.

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
        return attr_dict

    def add_node(self, node, attr_dict=None, **attr):
        """Adds a node to the graph, along with any related attributes
           of the node.

        :param node: reference of the node.
        :param attr_dict: dictionary of attributes of the node.
        :param **attr: keyword arguments of attributes of the node; takes
                    precedence over attr_dict.
        :raises: AttributeError

        """
        attr_dict = self._combine_attribute_arguments(attr_dict, attr)

        # If the node hasn't previously been added, add it along
        # with its attributes
        if node not in self._node_attributes:
            self._node_attributes[node] = attr_dict
            self._forward_star[node] = set()
            self._backward_star[node] = set()
        # Otherwise, just update the node's attributes
        else:
            self._node_attributes[node].update(attr_dict)

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
        attr_dict = self._combine_attribute_arguments(attr_dict, attr)

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
        attr_dict = self._combine_attribute_arguments(attr_dict, attr)

        # Use frozensets for tail and head sets to allow for hashable keys
        frozen_tail = frozenset(tail)
        frozen_head = frozenset(head)

        if frozen_tail not in self._successors:
            self._successors[frozen_tail] = {}
        if frozen_head not in self._predecessors:
            self._predecessors[frozen_head] = {}

        is_new_hyperedge = frozen_head not in self._successors[frozen_tail]
        if is_new_hyperedge:
            # Add tail and head nodes to graph (if not already present)
            self.add_nodes(frozen_head)
            self.add_nodes(frozen_tail)

            # Create new hyperedge name to use as reference for that hyperedge
            self._assigned_hyperedges += 1
            hyperedge_name = "e" + str(self._assigned_hyperedges)

            # Add edge to the forward-star and to the backward-star for each
            # node in the tail and head sets, respectively
            for node in frozen_tail:
                self._forward_star[node].add(hyperedge_name)
            for node in frozen_head:
                self._backward_star[node].add(hyperedge_name)

            # Add the edge as the successors and predecessors of the tail set
            # and head set, respectively
            self._successors[frozen_tail][frozen_head] = hyperedge_name
            self._predecessors[frozen_head][frozen_tail] = hyperedge_name

            self._hyperedge_attributes[hyperedge_name] = \
                {'tail': tail, 'head': head}
        else:
            hyperedge_name = self._successors[frozen_tail][frozen_head]

        self._hyperedge_attributes[hyperedge_name].update(attr_dict)
