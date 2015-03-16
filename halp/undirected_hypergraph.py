"""
.. module:: undirected_hypergraph
   :synopsis: Defines UndirectedHypergraph class for the basic properties
            of an undirected hypergraph, along with the relevant structures
            regarding nodes, hyperedges, adjacency, etc.

"""

import copy


class UndirectedHypergraph(object):
    """
    The UndirectedHypergraph class provides an undirected hypergraph object
    and associated functions for basic properties of undirected hypergraphs.

    An undirected hypergraph contains nodes and undirected hyperedges. Each
    undirected hyperedge simply connects a set of nodes. An undirected
    hypergraph is a special case of an undirected graph, where each edge
    connects exactly 2 nodes. The set of nodes cannot be empty.

    A node is simply any hashable type. See "add_node" or "add_nodes" for
    more details.

    An undirected hyperedge is any iterable container of nodes.
    This class assigns (upon adding) and refers to each hyperedge by an
    internal ID. See "add_hyperedge" or "add_hyperedges" for more details.

    Self-loops and parallel (multi-) hyperedges are not allowed.

    :note: This class uses several data structures to store a undirected
        hypergraph. Since these structures must stay in sync (see: __init__),
        we highly recommend that only the public methods be used for accessing
        and modifying the hypergraph.

    Examples:
    Create an empty undirected hypergraph (no nodes or hyperedges).

    >>> H = UndirectedHypergraph()

    Add nodes (with or without attributes) to the hypergraph
    one at a time (see: add_node) or several at a time (see: add_nodes).

    >>> H.add_nodes(["A", "B", "C", "D"], {color: "black"})

    Add hyperedges to the hypergraph one at a time (see: add_hyperedge)
    or several at a time (see: add_hyperedges).

    >>> H.add_hyperedges(["A", "B"], ("A", "C", "D"))

    Update attributes of existing nodes and hyperedges by simulating adding the
    node or hyperedge again, with the [potentially new] attribute appended.

    >>> H.add_node("A", label="sink")
    >>> H.add_hyperedge(["A", "C", "D"], weight=5)

    """

    def __init__(self):
        """
        Constructor for the UndirectedHypergraph class.
        Initializes all internal data structures used for the rapid
        execution of most of the fundamental hypergraph queries.

        """
        # _node_attributes: a dictionary mapping a node (any hashable type)
        # to a dictionary of attributes of that node.
        #
        # Provides O(1) time access to the attributes of a node.
        #
        # Used in the implementation of methods such as add_node and
        # get_node_attributes.
        #
        self._node_attributes = {}

        # _hyperedge_attributes: a dictionary mapping a hyperedge ID
        # (initially created by the call to add_hyperedge or add_hyperedges)
        # to a dictionary of attributes of that hyperedge.
        # Given a hyperedge ID, _hyperedge_attributes[hyperedge_id] stores
        # the nodes of the hyperedge as specified by the user (as "nodes")
        # and the weight of the hyperedge (as "weight").
        # For internal purposes, it also stores the frozenset version of
        # the nodes (as "__frozen_nodes").
        #
        # Provides O(1) time access to the attributes of a hyperedge.
        #
        # Used in the implementation of methods such as add_hyperedge and
        # get_hyperedge_attributes.
        #
        self._hyperedge_attributes = {}

        # The star of a node is the set of hyperedges such that the
        # node is a member of.
        #
        # _star: a dictionary mapping a node to the set of hyperedges
        # that are in that node's star.
        #
        # Provides O(1) time access to a reference to the set of hyperedges
        # that a node is a member of.
        #
        # Used in the implementation of methods such as add_node and
        # remove_hyperedge.
        #
        self._star = {}

        # _node_set_to_hyperedge: a dictionary mapping a set of nodes to the ID
        # of the hyperedge they compose. We represent the node set by a
        # frozenset, so that the structure is hashable.
        #
        # Provides O(1) time access to the ID of the hyperedge that
        # a specific frozenset of nodes composes.
        #
        self._node_set_to_hyperedge = {}

        # _current_hyperedge_id: an int representing the hyperedge ID that
        # was most recently assigned by the class (since users don't
        # name/ID their own hyperedges); hyperedges being added are issued
        # ID "e"+_current_hyperedge_id.
        #
        # Since the class takes responsibility for giving hyperedges
        # their IDs (i.e. a unique identifier; could be alternatively viewed
        # as a unique name, label, etc.), the class keeps track of the issued
        # IDs. A consecutive issuing of integer IDs to the hyperedges is a
        # simple strategy to ensure their uniqueness while allowing for
        # readability.
        #
        # e.g., _current_hyperedge_id = 4  implies that 4 hyperedges have
        # been added to the hypergraph, and that "e4" was the most recently
        # assigned hyperedge.
        #
        # Note: An hyperedge, once added, will receive a unique ID. If this
        # hyperedge is removed and subsequently re-added, it will not receive
        # the same ID as it was issued when it was originally added.
        #
        self._current_hyperedge_id = 0

    def _combine_attribute_arguments(self, attr_dict, attr):
        # Note: Code & comments unchanged from DirectedHypergraph
        """Combines attr_dict and attr dictionaries, by updating attr_dict
            with attr.

        :param attr_dict: dictionary of attributes of the node.
        :param attr: keyword arguments of attributes of the node;
                    attr's values will override attr_dict's values
                    if both are provided.
        :returns: dict -- single dictionary of [combined] attributes.
        :raises: AttributeError -- attr_dict argument must be a dictionary.

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

    def has_node(self, node):
        # Note: Code & comments unchanged from DirectedHypergraph
        """Determines if a specific node is present in the hypergraph.

        :param node: reference to the node whose presence is being checked.
        :returns: bool -- true iff the node exists in the hypergraph.

        """
        return node in self._node_attributes

    def add_node(self, node, attr_dict=None, **attr):
        """Adds a node to the graph, along with any related attributes
           of the node.

        :param node: reference to the node being added.
        :param attr_dict: dictionary of attributes of the node.
        :param attr: keyword arguments of attributes of the node;
                    attr's values will override attr_dict's values
                    if both are provided.
        :note: Following the NetworkX model, we allow both a dictionary
            of attributes to be passed in by the user as well as key-value
            pairs of attributes to be passed in by the user to provide
            greater flexibility. This pattern is followed in methods such
            as add_nodes, add_hyperedge, and add_hyperedges.


        Examples:
        ::

            >>> H = UndirectedHypergraph()
            >>> attributes = {label: "positive"}
            >>> H.add_node("A", attributes)
            >>> H.add_node("B", label="negative")
            >>> H.add_node("C", attributes, root=True)

        """
        attr_dict = self._combine_attribute_arguments(attr_dict, attr)

        # If the node hasn't previously been added, add it along
        # with its attributes
        if not self.has_node(node):
            self._node_attributes[node] = attr_dict
            self._star[node] = set()
        # Otherwise, just update the node's attributes
        else:
            self._node_attributes[node].update(attr_dict)

    def add_nodes(self, nodes, attr_dict=None, **attr):
        # Note: Code & comments unchanged from DirectedHypergraph
        """Adds multiple nodes to the graph, along with any related attributes
            of the nodes.

        :param nodes: iterable container to either references of the nodes
                    OR tuples of (node reference, attribute dictionary);
                    if an attribute dictionary is provided in the tuple,
                    its values will override both attr_dict's and attr's
                    values.
        :param attr_dict: dictionary of attributes shared by all the nodes.
        :param attr: keyword arguments of attributes of the node;
                    attr's values will override attr_dict's values
                    if both are provided.

        See also:
        add_node

        Examples:
        ::

            >>> H = UndirectedHypergraph()
            >>> attributes = {label: "positive"}
            >>> node_list = ["A",
                             ("B", {label="negative"}),
                             ("C", {root=True})]
            >>> H.add_nodes(node_list, attributes)

        """
        attr_dict = self._combine_attribute_arguments(attr_dict, attr)

        for node in nodes:
            # Note: This won't behave properly if the node is actually a tuple
            if type(node) is tuple:
                # See ("B", {label="negative"}) in the documentation example
                new_node, node_attr_dict = node
                # Create a new dictionary and load it with node_attr_dict and
                # attr_dict, with the former (node_attr_dict) taking precedence
                new_dict = attr_dict.copy()
                new_dict.update(node_attr_dict)
                self.add_node(new_node, new_dict)
            else:
                # See "A" in the documentation example
                self.add_node(node, attr_dict.copy())

    def remove_node(self, node):
        """Removes a node and its attributes from the hypergraph. Removes
        every hyperedge that contains this node.

        :param node: reference to the node being added.
        :raises: ValueError -- No such node exists.

        Examples:
        ::

            >>> H = UndirectedHypergraph()
            >>> H.add_node("A", label="positive")
            >>> H.remove_node("A")

        """
        if not self.has_node(node):
            raise ValueError("No such node exists.")

        # Loop over every hyperedge in the star of the node;
        # i.e., over every hyperedge that contains the node
        for hyperedge_id in self._star[node]:
            frozen_nodes = \
                self._hyperedge_attributes[hyperedge_id]["__frozen_nodes"]
            # Remove the node set composing the hyperedge
            del self._node_set_to_hyperedge[frozen_nodes]
            # Remove this hyperedge's attributes
            del self._hyperedge_attributes[hyperedge_id]

        # Remove node's star
        del self._star[node]

        # Remove node's attributes dictionary
        del self._node_attributes[node]

    def remove_nodes(self, nodes):
        # Note: Code unchanged from DirectedHypergraph
        """Removes multiple nodes and their attributes from the graph. If
        the nodes are part of any hyperedges, those hyperedges are removed
        as well.

        :param nodes: iterable container to either references of the nodes
                    OR tuples of (node reference, attribute dictionary);
                    if an attribute dictionary is provided in the tuple,
                    its values will override both attr_dict's and attr's
                    values.

        See also:
        remove_node

        Examples:
        ::

            >>> H = UndirectedHypergraph()
            >>> attributes = {label: "positive"}
            >>> node_list = ["A",
                             ("B", {label="negative"}),
                             ("C", {root=True})]
            >>> H.add_nodes(node_list, attributes)
            >>> H.remove_nodes(["A", "B", "C"])

        """
        for node in nodes:
            self.remove_node(node)

    def get_node_set(self):
        # Note: Code and comments unchanged from DirectedHypergraph
        """Returns the set of nodes that are currently in the hypergraph.

        :returns: set -- all nodes currently in the hypergraph

        """
        return set(self._node_attributes.keys())

    def node_iterator(self):
        # Note: Code and comments unchanged from DirectedHypergraph
        """Provides an iterator over the nodes.

        """
        return iter(self._node_attributes)

    def get_node_attribute(self, node, attribute_name):
        # Note: Code and comments unchanged from DirectedHypergraph
        """Given a node and the name of an attribute, get a copy
        of that node's attribute.

        :param node: reference to the node to retrieve the attribute of.
        :param attribute_name: name of the attribute to retrieve.
        :returns: attribute value of the attribute_name key for the
                specified node.
        :raises: ValueError -- No such node exists.
        :raises: ValueError -- No such attribute exists.

        """
        if not self.has_node(node):
            raise ValueError("No such node exists.")
        elif attribute_name not in self._node_attributes[node]:
            raise ValueError("No such attribute exists.")
        else:
            return copy.\
                copy(self._node_attributes[node][attribute_name])

    def get_node_attributes(self, node):
        # Note: Code and comments unchanged from DirectedHypergraph
        """Given a node, get a dictionary with copies of that node's
        attributes.

        :param node: reference to the node to retrieve the attributes of.
        :returns: dict -- copy of each attribute of the specified node.
        :raises: ValueError -- No such node exists.

        """
        if not self.has_node(node):
            raise ValueError("No such node exists.")
        attributes = {}
        for attr_name, attr_value in self._node_attributes[node].items():
            attributes[attr_name] = copy.copy(attr_value)
        return attributes

    def _assign_next_hyperedge_id(self):
        # Note: Code and comments unchanged from DirectedHypergraph
        """Returns the next [consecutive] ID to be assigned
            to a hyperedge.
        :returns: str -- hyperedge ID to be assigned.

        """
        self._current_hyperedge_id += 1
        return "e" + str(self._current_hyperedge_id)

    def add_hyperedge(self, nodes, attr_dict=None, **attr):
        """Adds a hyperedge to the hypergraph, along with any related
            attributes of the hyperedge.
            This method will automatically add any node from the node set
            that was not in the hypergraph.
            A hyperedge without a "weight" attribute specified will be
            assigned the default value of 1.

        :param nodes: iterable container of references to nodes in the
                    hyperedge to be added.
        :param attr_dict: dictionary of attributes of the hyperedge being
                        added.
        :param attr: keyword arguments of attributes of the hyperedge;
                    attr's values will override attr_dict's values
                    if both are provided.
        :returns: str -- the ID of the hyperedge that was added.
        :raises: ValueError -- nodes arguments cannot be empty.

        Examples:
        ::

            >>> H = UndirectedHypergraph()
            >>> x = H.add_hyperedge(["A", "B", "C"])
            >>> y = H.add_hyperedge(("A", "D"), weight=2)
            >>> z = H.add_hyperedge(set(["B", "D"]), {color: "red"})

        """
        attr_dict = self._combine_attribute_arguments(attr_dict, attr)

        # Don't allow empty node set (invalid hyperedge)
        if not nodes:
            raise ValueError("nodes argument cannot be empty.")

        # Use frozensets for node sets to allow for hashable keys
        frozen_nodes = frozenset(nodes)

        is_new_hyperedge = not self.has_hyperedge(frozen_nodes)
        if is_new_hyperedge:
            # Add nodes to graph (if not already present)
            self.add_nodes(frozen_nodes)

            # Create new hyperedge name to use as reference for that hyperedge
            hyperedge_id = self._assign_next_hyperedge_id()

            # For each node in the node set, add hyperedge to the node's star
            for node in frozen_nodes:
                self._star[node].add(hyperedge_id)

            # Add the hyperedge ID as the hyperedge that the node set composes
            self._node_set_to_hyperedge[frozen_nodes] = hyperedge_id

            # Assign some special attributes to this hyperedge. We assign
            # a default weight of 1 to the hyperedge. We also store the
            # original node set in order to return them exactly as the
            # user passed them into add_hyperedge.
            self._hyperedge_attributes[hyperedge_id] = \
                {"nodes": nodes, "__frozen_nodes": frozen_nodes, "weight": 1}
        else:
            # If its not a new hyperedge, just get its ID to update attributes
            hyperedge_id = self._node_set_to_hyperedge[frozen_nodes]

        # Set attributes and return hyperedge ID
        self._hyperedge_attributes[hyperedge_id].update(attr_dict)
        return hyperedge_id

    def add_hyperedges(self, hyperedges, attr_dict=None, **attr):
        """Adds multiple hyperedges to the graph, along with any related
            attributes of the hyperedges.
            If any node of a hyperedge has not previously been added to the
            hypergraph, it will automatically be added here.
            Hyperedges without a "weight" attribute specified will be
            assigned the default value of 1.

        :param hyperedges: iterable container to references of the node sets
        :param attr_dict: dictionary of attributes shared by all
                    the hyperedges being added.
        :param attr: keyword arguments of attributes of the hyperedges;
                    attr's values will override attr_dict's values
                    if both are provided.
        :returns: list -- the IDs of the hyperedges added in the order
                    specified by the hyperedges container's iterator.

        See also:
        add_hyperedge

        Examples:
        ::

            >>> H = UndirectedHypergraph()
            >>> hyperedge_list = (["A", "B", "C"],
                                  ("A", "D"),
                                  set(["B", "D"]))
            >>> hyperedge_ids = H.add_hyperedges(hyperedge_list)

        """
        attr_dict = self._combine_attribute_arguments(attr_dict, attr)

        hyperedge_ids = []

        for nodes in hyperedges:
            hyperedge_id = self.add_hyperedge(nodes, attr_dict.copy())
            hyperedge_ids.append(hyperedge_id)

        return hyperedge_ids

    def remove_hyperedge(self, hyperedge_id):
        """Removes a hyperedge and its attributes from the hypergraph.

        :param hyperedge_id: ID of the hyperedge to be removed.
        :raises: ValueError -- No such hyperedge exists.

        Examples:
        ::

            >>> H = UndirectedHypergraph()
            >>> hyperedge_list = (["A", "B", "C"],
                                  ("A", "D"),
                                  set(["B", "D"]))
            >>> hyperedge_ids = H.add_hyperedges(hyperedge_list)
            >>> H.remove_hyperedge(hyperedge_ids[0])
            >>> BD_id = H.get_hyperedge_id(set(["B", "D"]))
            >>> H.remove_hyperedge(BD_id)

        """
        if not self.has_hyperedge_id(hyperedge_id):
            raise ValueError("No such hyperedge exists.")

        frozen_nodes = \
            self._hyperedge_attributes[hyperedge_id]["__frozen_nodes"]

        # Remove this hyperedge from the star of every node in the hyperedge
        for node in frozen_nodes:
            self._star[node].remove(hyperedge_id)

        # Remove this set as the composer of the hyperedge
        del self._node_set_to_hyperedge[frozen_nodes]

        # Remove hyperedge's attributes dictionary
        del self._hyperedge_attributes[hyperedge_id]

    def remove_hyperedges(self, hyperedge_ids):
        # Note: Code unchanged from DirectedHypergraph
        """Removes a set of hyperedges and their attributes from
        the hypergraph.

        :param hyperedge_ids: iterable container of IDs of the hyperedges
                        to be removed.
        :raises: ValueError -- No such hyperedge exists.

        See also:
        remove_hyperedge

        Examples:
        ::

            >>> H = UndirectedHypergraph()
            >>> hyperedge_list = (["A", "B", "C"],
                                  ("A", "D"),
                                  set(["B", "D"]))
            >>> hyperedge_ids = H.add_hyperedges(hyperedge_list)
            >>> H.remove_hyperedges(hyperedge_ids)

        """
        for hyperedge_id in hyperedge_ids:
            self.remove_hyperedge(hyperedge_id)

    def has_hyperedge(self, nodes):
        # Note: Code and comments unchanged from DirectedHypergraph
        """Given a set of nodes, returns whether there is a hyperedge in the
        hypergraph that is precisely composed of those nodes.

        :param nodes: iterable container of references to nodes in the
                    hyperedge being checked.
        :returns: bool -- true iff a hyperedge exists composed of the
                specified nodes.
        """
        frozen_nodes = frozenset(nodes)
        return frozen_nodes in self._node_set_to_hyperedge

    def has_hyperedge_id(self, hyperedge_id):
        # Note: Code and comments unchanged from DirectedHypergraph
        """Determines if a hyperedge referenced by hyperedge_id
        exists in the hypergraph.

        :param hyperedge_id: ID of the hyperedge whose existence is
                            being checked.
        :returns: bool -- true iff a hyperedge exists that has id hyperedge_id.

        """
        return hyperedge_id in self._hyperedge_attributes

    def get_hyperedge_id_set(self):
        # Note: Code and comments unchanged from DirectedHypergraph
        """Returns the set of IDs of hyperedges that are currently
        in the hypergraph.

        :returns: set -- all IDs of hyperedges currently in the hypergraph

        """
        return set(self._hyperedge_attributes.keys())

    def hyperedge_id_iterator(self):
        # Note: Code and comments unchanged from DirectedHypergraph
        """Provides an iterator over the list of hyperedge IDs.

        """
        return iter(self._hyperedge_attributes)

    def get_hyperedge_id(self, nodes):
        """From a set of nodes, returns the ID of the hyperedge that this
        set comprises.

        :param nodes: iterable container of references to nodes in the
                    the hyperedge to be added
        :returns: str -- ID of the hyperedge that has that the specified
                node set comprises.
        :raises: ValueError -- No such hyperedge exists.

        Examples:
        ::

            >>> H = UndirectedHypergraph()
            >>> hyperedge_list = (["A", "B", "C"],
                                  ("A", "D"),
                                  set(["B", "D"]))
            >>> hyperedge_ids = H.add_hyperedges(hyperedge_list)
            >>> x = H.get_hyperedge_id(["A", "B", "C"])

        """
        frozen_nodes = frozenset(nodes)

        if not self.has_hyperedge(frozen_nodes):
            raise ValueError("No such hyperedge exists.")

        return self._node_set_to_hyperedge[frozen_nodes]

    def get_hyperedge_attribute(self, hyperedge_id, attribute_name):
        # Note: Code unchanged from DirectedHypergraph
        """Given a hyperedge ID and the name of an attribute, get a copy
        of that hyperedge's attribute.

        :param hyperedge_id: ID of the hyperedge to retrieve the attribute of.
        :param attribute_name: name of the attribute to retrieve.
        :returns: attribute value of the attribute_name key for the
                specified hyperedge.
        :raises: ValueError -- No such hyperedge exists.
        :raises: ValueError -- No such attribute exists.

        Examples:
        ::

            >>> H = UndirectedHypergraph()
            >>> hyperedge_list = (["A", "B", "C"],
                                  ("A", "D"),
                                  set(["B", "D"]))
            >>> hyperedge_ids = H.add_hyperedges(hyperedge_list)
            >>> attribute = H.get_hyperedge_attribute(hyperedge_ids[0])

        """
        if not self.has_hyperedge_id(hyperedge_id):
            raise ValueError("No such hyperedge exists.")
        elif attribute_name not in self._hyperedge_attributes[hyperedge_id]:
            raise ValueError("No such attribute exists.")
        else:
            return copy.\
                copy(self._hyperedge_attributes[hyperedge_id][attribute_name])

    def get_hyperedge_attributes(self, hyperedge_id):
        """Given a hyperedge ID, get a dictionary of copies of that hyperedge's
        attributes.

        :param hyperedge_id: ID of the hyperedge to retrieve the attributes of.
        :returns: dict -- copy of each attribute of the specified hyperedge_id
                (except the private __frozen_nodes entry).
        :raises: ValueError -- No such hyperedge exists.

        """
        if not self.has_hyperedge_id(hyperedge_id):
            raise ValueError("No such hyperedge exists.")
        dict_to_copy = self._hyperedge_attributes[hyperedge_id].items()
        attributes = {}
        for attr_name, attr_value in dict_to_copy:
            if attr_name != "__frozen_nodes":
                attributes[attr_name] = copy.copy(attr_value)
        return attributes

    def get_hyperedge_nodes(self, hyperedge_id):
        """Given a hyperedge ID, get a copy of that hyperedge's nodes.

        :param hyperedge_id: ID of the hyperedge to retrieve the nodes from.
        :returns: a copy of the container of nodes that the user provided
                for the hyperedge referenced as hyperedge_id.

        """
        return self.get_hyperedge_attribute(hyperedge_id, "nodes")

    def get_hyperedge_weight(self, hyperedge_id):
        # Note: Code and comments unchanged from DirectedHypergraph
        """Given a hyperedge ID, get that hyperedge's weight.

        :param hyperedge: ID of the hyperedge to retrieve the weight from.
        :returns: int -- the weight of the hyperedge referenced as
                hyperedge_id.

        """
        return self.get_hyperedge_attribute(hyperedge_id, "weight")

    def get_star(self, node):
        """Given a node, get a copy of that node's star, that is, the set of
        hyperedges that the node belongs to.

        :param node: node to retrieve the star of.
        :returns: set -- set of hyperedge_ids for the hyperedges
                        in the node's star.
        :raises: ValueError -- No such node exists.

        """
        if node not in self._node_attributes:
            raise ValueError("No such node exists.")
        return self._star[node].copy()

    def copy(self):
        # Note: Code unchanged from DirectedHypergraph
        """Creates a new UndirectedHypergraph object with the same node and
        hyperedge structure.
        Copies of the nodes' and hyperedges' attributes are stored
        and used in the new hypergraph.

        :returns: UndirectedHypergraph -- a new hypergraph that is a copy of
                the current hypergraph

        """
        return self.__copy__()

    def __copy__(self):
        """Creates a new UndirectedHypergraph object with the same node and
        hyperedge structure.
        Copies of the nodes' and hyperedges' attributes are stored
        and used in the new hypergraph.

        :returns: UndirectedHypergraph -- a new hypergraph that is a copy of
                the current hypergraph

        """
        new_H = UndirectedHypergraph()

        # Loop over every node and its corresponding attribute dict
        # in the original hypergraph's _node_attributes dict
        for node, attr_dict in self._node_attributes.items():
            # Create a new dict for that node to store that node's attributes
            new_H._node_attributes[node] = {}
            # Loop over each attribute of that node in the original hypergraph
            # and, for each key, copy the corresponding value into the new
            # hypergraph's dictionary using the same key
            for attr_name, attr_value in attr_dict.items():
                new_H._node_attributes[node][attr_name] = \
                    copy.copy(attr_value)

        # Loop over every hyperedge_id and its corresponding attribute dict
        # in the original hypergraph's _hyperedge_attributes dict
        for hyperedge_id, attr_dict in self._hyperedge_attributes.items():
            # Create a new dict for that node to store that node's attributes
            new_H._hyperedge_attributes[hyperedge_id] = {}
            # Loop over each attribute of that hyperedge in the original
            # hypergraph and, for each key, copy the corresponding value
            # the new hypergraph's dictionary
            for attr_name, attr_value in attr_dict.items():
                new_H.\
                    _hyperedge_attributes[hyperedge_id][attr_name] = \
                    copy.copy(attr_value)

        # Copy the original hypergraph's nodes' stars
        new_H._star = self._star.copy()
        for node in self._node_attributes.keys():
            new_H._star[node] = self._star[node].copy()

        # Copy the original hypergraph's composed hyperedges
        for frozen_nodes, hyperedge_id in self._node_set_to_hyperedge.items():
            new_H._node_set_to_hyperedge[frozen_nodes] = \
                copy.copy(hyperedge_id)

        # Start assigning edge labels at the same
        new_H._current_hyperedge_id = self._current_hyperedge_id

        return new_H

    # TODO: make reading more extensible (attributes, variable ordering, etc.)
    def read(self, file_name, delim=',', sep='\t'):
        """Reads an undirected hypergraph from a file, where nodes are
        represented as strings.
        Each column is separated by "sep", and the individual nodes are
        delimited by "delim".
        The header line is currently ignored, but columns should be of
        the format:
        node1[delim]..nodeM[sep]weight

        As a concrete example, an arbitrary line with delim=',' and
        sep='    ' (4 spaces) may look like:
        ::

            x1,x2,x3,x5    12

        which defines a hyperedge of weight 12 from a node set containing
        nodes "x1", "x2", "x3", and "x5".

        """
        in_file = open(file_name, 'r')

        # Skip the header line
        in_file.readline()

        line_number = 2
        for line in in_file.readlines():
            line = line.strip()
            # Skip empty lines
            if not line:
                continue

            words = line.split(sep)
            if not (1 <= len(words) <= 2):
                raise \
                    IOError("Line {} ".format(line_number) +
                            "contains {} ".format(len(words)) +
                            "columns -- must contain only 1 or 2.")

            nodes = set(words[0].split(delim))
            if len(words) == 2:
                weight = float(words[1].split(delim)[0])
            else:
                weight = 1
            self.add_hyperedge(nodes, weight=weight)

            line_number += 1

        in_file.close()

    # TODO: make writing more extensible (attributes, variable ordering, etc.)
    def write(self, file_name, delim=',', sep='\t'):
        """Writes an undirected hypergraph from a file, where nodes are
        represented as strings.
        Each column is separated by "sep", and the individual nodes are
        delimited by "delim".
        The header line is currently ignored, but columns should be of
        the format:
        node1[delim]..nodeM[sep]node1[delim]..nodeN[sep]weight

        As a concrete example, an arbitrary line with delim=',' and
        sep='    ' (4 spaces) may look like:
        ::

            x1,x2,x3,x5    12

        which defines a hyperedge of weight 12 from a node set containing
        nodes "x1", "x2", "x3", and "x5".

        """
        out_file = open(file_name, 'w')

        # write first header line
        out_file.write("nodes" + sep + "weight\n")

        for hyperedge_id in self.get_hyperedge_id_set():
            line = ""
            # Write each node to the line, separated by delim
            for node in self.get_hyperedge_nodes(hyperedge_id):
                line += node + delim
            # Remove last (extra) delim
            line = line[:-1]

            # Write the weight to the line and end the line
            line += sep + str(self.get_hyperedge_weight(hyperedge_id)) + "\n"

            out_file.write(line)

        out_file.close()
