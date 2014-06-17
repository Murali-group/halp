"""
.. module:: directed_hypergraph
   :synopsis: Defines DirectedHypergraph class for the basic properties
            of a directed hypergraph, along with the relevant structures
            regarding nodes, hyperedges, adjacency, etc.

"""

from __future__ import absolute_import
import copy


class DirectedHypergraph(object):
    """
    The DirectedHypergraph class provides a directed hypergraph object
    and associated functions for basic properties of directed hypergraphs.

    A directed hypergraph contains nodes and hyperedges. Each hyperedge
    connects a tail set of nodes to a head set of nodes. The tail and head
    cannot both be empty.

    A node is simply any hashable type. See "add_node" or "add_nodes" for
    more details.

    A directed hyperedge is a tuple of the tail nodes and the head nodes.
    This class assigns (upon adding) and refers to each hyperedge by an
    internal ID. See "add_hyperedge" or "add_hyperedges" for more details.

    :note: This class uses several data structures to store a directed
        hypergraph. Since these structures must stay in sync (see: __init__),
        we highly recommend that only the public methods be used for accessing
        and modifying the hypergraph.

    Examples
    --------
    Create an empty graph (no nodes or hyperedges).

    >>> H = DirectedHypergraph()

    Add nodes (with or without attributes) to the hypergraph
    one at a time (see: add_node) or several at a time (see: add_nodes).

    >>> H.add_nodes(["A", "B", "C", "D"], {color: "black"})

    Add hyperedges (with or without attributes) to the hypergraph one
    at a time (see: add_hyperedge) or several at a time (see: add_hyperedges).

    >>> H.add_hyperedges((["A"], ["B"]), (["A", "B"], ["C", "D"]))

    Add attributes of nodes and hyperedges by [re]adding the node
    or hyperedge with the [potentially new] attribute appended.

    >>> H.add_node("A", label="sink")
    >>> H.add_hyperedge((["A", "B"], ["C", "D"]), weight=5)

    """

    def __init__(self):
        """
        Constructor for the DirectedHypergraph class.
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
        # the tail of the hyperedge as specified by the user (as "tail"),
        # the head of the hyperedge as specified by the user (as "head"),
        # and the weight of the hyperedge (as "weight").
        # For internal purposes, it also stores the frozenset versions of
        # the tail and head (as "_frozen_tail" and "_frozen_head").
        #
        # Provides O(1) time access to the attributes of a hyperedge.
        #
        # Used in the implementation of methods such as add_hyperedge and
        # get_hyperedge_attributes.
        #
        self._hyperedge_attributes = {}

        # The forward star of a node is the set of hyperedges such that the
        # node is in the tail of each hyperedge in that set.
        #
        # _forward_star: a dictionary mapping a node to the set of hyperedges
        # that are in that node's forward star.
        #
        # Provides O(1) time access to a reference to the set of outgoing
        # hyperedges from a node.
        #
        # Used in the implementation of methods such as add_node and
        # remove_hyperedge.
        #
        self._forward_star = {}

        # The backward star of a node is the set of hyperedges such that the
        # node is in the head of each hyperedge in that set.
        #
        # _backward_star: a dictionary mapping a node to the set of hyperedges
        # that are in that node's backward star.
        #
        # Provides O(1) time access to a reference to the set of incoming
        # hyperedges from a node.
        #
        # Used in the implementation of methods such as add_node and
        # remove_hyperedge.
        #
        self._backward_star = {}

        # _successors: a 2-dimensional dictionary mapping (first) a tail set
        # and (second) a head set of a hyperedge to the ID of the corresponding
        # hyperedge. We represent each tail set and each head set by a
        # frozenset, so that the structure is hashable.
        #
        # Provides O(1) time access to the ID of the of the hyperedge
        # connecting a specific tail frozenset to a specific head frozenset.
        # Given a tail frozenset, it also provides O(1) time access to a
        # reference to the dictionary mapping head frozensets to hyperedge IDs;
        # these hyperedges are precisely those in the forward star of this
        # tail frozenset.
        #
        self._successors = {}

        # _predecessors: a 2-dimensional dictionary mapping (first) a head set
        # and (second) a tail set of a hyperedge to the ID of the corresponding
        # hyperedge. We represent each tail set and each head set by a
        # frozenset, so that the structure is hashable.
        #
        # Provides O(1) time access to the ID of the of the hyperedge
        # connecting a specific head frozenset to a specific tail frozenset.
        # Given a head frozenset, it also provides O(1) time access to a
        # reference to the dictionary mapping tail frozensets to hyperedge IDs;
        # these hyperedges are precisely those in the backward star of this
        # head frozenset.
        #
        self._predecessors = {}

        # _current_hyperedge_id: an int representing the hyperedge ID that
        # was most recently assigned by the class (since users don't
        # name/ID their own hyperedges); hyperedges being added are issued
        # ID "e"+_current_hyperedge_id.
        #
        # Since the class takes responsibility for giving hyperedges
        # their IDs (i.e. a unique identifier; could be alternatively viewed
        # as a unique name, label, etc.), the issued IDs need to be kept
        # track of. A consecutive issuing of integer IDs to the hyperedges is a
        # simple strategy to ensure their uniqueness and allow for
        # intuitive readability.
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
        """Combines attr_dict and attr dictionaries, by updating attr_dict
            with attr.

        :param attr_dict: dictionary of attributes of the node.
        :param **attr: keyword arguments of attributes of the node;
                    attr's values will override attr_dict's values
                    if both are provided.
        :returns: dict -- single dictionary of [combined] attributes.
        :raises: AttributeError - attr_dict argument must be a dictionary.

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
        return node in self._node_attributes

    def add_node(self, node, attr_dict=None, **attr):
        """Adds a node to the graph, along with any related attributes
           of the node.

        :param node: reference to the node being added.
        :param attr_dict: dictionary of attributes of the node.
        :param **attr: keyword arguments of attributes of the node;
                    attr's values will override attr_dict's values
                    if both are provided.

        Examples
        --------
        >>> H = DirectedHypergraph()
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
            self._forward_star[node] = set()
            self._backward_star[node] = set()
        # Otherwise, just update the node's attributes
        else:
            self._node_attributes[node].update(attr_dict)

    def add_nodes(self, nodes, attr_dict=None, **attr):
        """Adds multiple nodes to the graph, along with any related attributes
            of the nodes.

        :param nodes: iterable container to either references of the nodes
                    OR tuples of (node reference, attribute dictionary);
                    if an attribute dictionary is provided in the tuple,
                    its values will override both attr_dict's and attr's
                    values.
        :param attr_dict: dictionary of attributes shared by all the nodes.
        :param **attr: keyword arguments of attributes of the node;
                    attr's values will override attr_dict's values
                    if both are provided.

        See also
        --------
        add_node

        Examples
        --------
        >>> H = DirectedHypergraph()
        >>> attributes = {label: "positive"}
        >>> node_list = ["A", ("B", {label="negative"}), ("C", {root=True})]
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

    def _assign_next_hyperedge_id(self):
        """Returns the next [consecutive] ID to be assigned
            to a hyperedge.
        :returns: str -- hyperedge ID to be assigned.

        """
        self._current_hyperedge_id += 1
        return "e" + str(self._current_hyperedge_id)

    def has_hyperedge(self, tail, head):
        """Given a tail and head set of nodes, returns whether there
        is a hyperedge in the hypergraph that connects the tail set
        to the head set.

        :param tail: iterable container of references to nodes in the
                    tail of the hyperedge being checked.
        :param head: iterable container of references to nodes in the
                    head of the hyperedge being checked.
        :returns: bool -- true iff a hyperedge exists connecting the
                specified tail set to the specified head set.
        """
        frozen_tail = frozenset(tail)
        frozen_head = frozenset(head)
        return frozen_tail in self._successors and \
            frozen_head in self._successors[frozen_tail]

    def has_hyperedge_id(self, hyperedge_id):
        """Determines if a hyperedge referenced by hyperedge_id
        exists in the hypergraph.

        :param hyperedge_id: ID of the hyperedge whose existence is
                            being checked.
        :returns: bool -- true iff a hyperedge exists that has id hyperedge_id.

        """
        return hyperedge_id in self._hyperedge_attributes

    def add_hyperedge(self, tail, head, attr_dict=None, **attr):
        """Adds a hyperedge to the hypergraph, along with any related
            attributes of the hyperedge.
            This method will automatically add any node from the tail and
            head that was not in the hypergraph.
            A hyperedge without a "weight" attribute specified will be
            assigned the default value of 1.

        :param tail: iterable container of references to nodes in the
                    tail of the hyperedge to be added.
        :param head: iterable container of references to nodes in the
                    head of the hyperedge to be added.
        :param attr_dict: dictionary of attributes shared by all
                    the hyperedges.
        :param **attr: keyword arguments of attributes of the hyperedge;
                    attr's values will override attr_dict's values
                    if both are provided.
        :returns: str -- the ID of the hyperedge that was added.
        :raises: ValueError - tail and head arguments cannot both be empty.

        Examples
        --------
        >>> H = DirectedHypergraph()
        >>> x = H.add_hyperedge(["A", "B"], ["C", "D"])
        >>> y = H.add_hyperedge(("A", "C"), ("B"), weight=2)
        >>> z = H.add_hyperedge(set(["D"]), set(["A", "C"])), {color: "red"})

        """
        attr_dict = self._combine_attribute_arguments(attr_dict, attr)

        # Don't allow both empty tail and head containers (invalid hyperedge)
        if not tail and not head:
        	raise ValueError("tail and head arguments \
                             cannot both be empty.")

        # Use frozensets for tail and head sets to allow for hashable keys
        frozen_tail = frozenset(tail)
        frozen_head = frozenset(head)

        # Initialize a successor dictionary for the tail and head, respectively
        if frozen_tail not in self._successors:
            self._successors[frozen_tail] = {}
        if frozen_head not in self._predecessors:
            self._predecessors[frozen_head] = {}

        is_new_hyperedge = not self.has_hyperedge(frozen_tail, frozen_head)
        if is_new_hyperedge:
            # Add tail and head nodes to graph (if not already present)
            self.add_nodes(frozen_head)
            self.add_nodes(frozen_tail)

            # Create new hyperedge name to use as reference for that hyperedge
            hyperedge_id = self._assign_next_hyperedge_id()

            # Add hyperedge to the forward-star and to the backward-star
            # for each node in the tail and head sets, respectively
            for node in frozen_tail:
                self._forward_star[node].add(hyperedge_id)
            for node in frozen_head:
                self._backward_star[node].add(hyperedge_id)

            # Add the hyperedge as the successors and predecessors
            # of the tail set and head set, respectively
            self._successors[frozen_tail][frozen_head] = hyperedge_id
            self._predecessors[frozen_head][frozen_tail] = hyperedge_id

            # Assign some special attributes to this hyperedge. We assign
            # a default weight of 1 to the hyperedge. We also store the
            # original tail and head sets in order to return them exactly
            # as the user passed them into add_hyperedge.
            self._hyperedge_attributes[hyperedge_id] = \
                {"tail": tail, "_frozen_tail": frozen_tail,
                 "head": head, "_frozen_head": frozen_head,
                 "weight": 1}
        else:
            # If its not a new hyperedge, just get its ID to update attributes
            hyperedge_id = self._successors[frozen_tail][frozen_head]

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

        :param hyperedges: iterable container to either references
                    of the hyperedges OR tuples of
                    (tail reference, head reference, attribute dictionary);
                    if an attribute dictionary is provided in the tuple,
                    its values will override both attr_dict's and attr's
                    values.
        :param attr_dict: dictionary of attributes shared by all
                    the hyperedges.
        :param **attr: keyword arguments of attributes of the hyperedges;
                    attr's values will override attr_dict's values
                    if both are provided.
        :returns: list -- the IDs of the hyperedges added in the order
                    specified by the container's iterator.

        See also
        --------
        add_hyperedge

        Examples
        --------
        >>> H = DirectedHypergraph()
        >>> xyz = hyperedge_list = (["A", "B"], ["C", "D"]), \
                                    (("A", "C"), ("B"), {weight: 2}), \
                                    (set(["D"]), set(["A", "C"])))
        >>> H.add_hyperedges(hyperedge_list)

        """
        attr_dict = self._combine_attribute_arguments(attr_dict, attr)

        hyperedge_ids = []

        for hyperedge in hyperedges:
            if len(hyperedge) == 3:
                # See ("A", "C"), ("B"), {weight: 2}) in the
                # documentation example
                tail, head, hyperedge_attr_dict = hyperedge
                # Create a new dictionary and load it with node_attr_dict and
                # attr_dict, with the former (node_attr_dict) taking precedence
                new_dict = attr_dict.copy()
                new_dict.update(hyperedge_attr_dict)
                hyperedge_id = self.add_hyperedge(tail, head, new_dict)
            else:
                # See (["A", "B"], ["C", "D"]) in the documentation example
                tail, head = hyperedge
                hyperedge_id = \
                    self.add_hyperedge(tail, head, attr_dict.copy())
            hyperedge_ids.append(hyperedge_id)

        return hyperedge_ids

    def remove_node(self, node):
        """Removes a node and its attributes from the hypergraph. Removes
        every hyperedge that contains this node in either the head or the tail.

        :param node: reference to the node being added.
        :raises: ValueError - No such node exists.

        Examples
        --------
        >>> H = DirectedHypergraph()
        >>> H.add_node("A", label="positive")
        >>> H.remove_node("A")

        """
        if not self.has_node(node):
            raise ValueError("No such node exists.")

        # Loop over every hyperedge in the forward star of the node;
        # i.e., over every hyperedge that contains the node in the tail
        frozen_tails = set()
        for hyperedge_id in \
                self._forward_star[node]:
            # Compute the frozenset for the tail and head of hyperedge_id
            frozen_tail = \
                self._hyperedge_attributes[hyperedge_id]["_frozen_tail"]
            frozen_head = \
                self._hyperedge_attributes[hyperedge_id]["_frozen_head"]
            frozen_tails.add(frozen_tail)
            # Remove this hyperedge from the _successors dict. Note that
            # after completion of this loop, _successors[frozen_tail]
            # will be empty
            del self._successors[frozen_tail][frozen_head]
            # Remove this hyperedge from the _predecessors dict
            del self._predecessors[frozen_head][frozen_tail]
            # Remove this hyperedge's attributes
            del self._hyperedge_attributes[hyperedge_id]
        # Remove _successors[frozen_tail] dicts for all tails that
        # contain the node
        for frozen_tail in frozen_tails:
            del self._successors[frozen_tail]

        # Loop over every hyperedge in the back star of the node that is
        # not also in the forward star of the node (to handle overlapping
        # hyperedges); i.e., over every hyperedge that contains the node
        # in the tail
        frozen_heads = set()
        for hyperedge_id in \
                self._backward_star[node].difference(self._forward_star[node]):
            # Compute the frozenset for the tail and head of hyperedge_id
            frozen_head = \
                self._hyperedge_attributes[hyperedge_id]["_frozen_head"]
            frozen_tail = \
                self._hyperedge_attributes[hyperedge_id]["_frozen_tail"]
            frozen_heads.add(frozen_head)
            # Remove this hyperedge from the _predecessors dict. Note that
            # after completion of this loop, _predecessors[frozen_tail]
            # will be empty
            del self._predecessors[frozen_head][frozen_tail]
            # Remove this hyperedge from the _successors dict
            del self._successors[frozen_tail][frozen_head]
            # Remove this hyperedge's attributes
            del self._hyperedge_attributes[hyperedge_id]
        # Remove _predecessors[frozen_head] dicts for all heads that
        # contain the node
        for frozen_head in frozen_heads:
            del self._predecessors[frozen_head]

        # Remove node's forward- and backward-star
        del self._forward_star[node]
        del self._backward_star[node]

        # Remove node's attributes dictionary
        del self._node_attributes[node]

    def remove_nodes(self, nodes):
        """Removes multiple nodes and their attributes from the graph. If
        the nodes are part of any hyperedges, those hyperedges are removed
        as well.

        :param nodes: iterable container to either references of the nodes
                    OR tuples of (node reference, attribute dictionary);
                    if an attribute dictionary is provided in the tuple,
                    its values will override both attr_dict's and attr's
                    values.

        See also
        --------
        remove_node

        Examples
        --------
        >>> H = DirectedHypergraph()
        >>> attributes = {label: "positive"}
        >>> node_list = ["A", ("B", {label="negative"}), ("C", {root=True})]
        >>> H.add_nodes(node_list, attributes)
        >>> H.remove_nodes(["A", "B", "C"])

        """
        for node in nodes:
            self.remove_node(node)

    def remove_hyperedge(self, hyperedge_id):
        """Removes a hyperedge and its attributes from the hypergraph.

        :param hyperedge_id: ID of the hyperedge to be removed.
        :raises: ValueError - No such hyperedge exists.

        Examples
        --------
        >>> H = DirectedHypergraph()
        >>> xyz = hyperedge_list = (["A"], ["B", "C"]), \
                                    (("A", "B"), ("C"), {weight: 2}), \
                                    (set(["B"]), set(["A", "C"])))
        >>> H.add_hyperedges(hyperedge_list)
        >>> H.remove_hyperedge(xyz[0])

        """
        if not self.has_hyperedge_id(hyperedge_id):
            raise ValueError("No such hyperedge exists.")

        # Get frozen tail and head of this hyperedge
        frozen_tail = \
            self._hyperedge_attributes[hyperedge_id]["_frozen_tail"]
        frozen_head = \
            self._hyperedge_attributes[hyperedge_id]["_frozen_head"]

        # Remove this hyperedge from the forward-star of every tail node
        for node in frozen_tail:
            self._forward_star[node].remove(hyperedge_id)
        # Remove this hyperedge from the backward-star of every head node
        for node in frozen_head:
            self._backward_star[node].remove(hyperedge_id)

        # Remove frozen_head as a successor of frozen_tail
        del self._successors[frozen_tail][frozen_head]
        # Remove frozen_tail as a predecessor of frozen_head
        del self._predecessors[frozen_head][frozen_tail]

        # Remove hyperedge's attributes dictionary
        del self._hyperedge_attributes[hyperedge_id]

    def remove_hyperedges(self, hyperedge_ids):
        """Removes a set of hyperedges and their attributes from
        the hypergraph.

        :param hyperedge_ids: iterable container of IDs of the hyperedges
                        to be removed.
        :raises: ValueError - No such hyperedge exists.

        See also
        --------
        remove_hyperedge

        Examples
        --------
        >>> H = DirectedHypergraph()
        >>> xyz = hyperedge_list = (["A"], ["B", "C"]), \
                                    (("A", "B"), ("C"), {weight: 2}), \
                                    (set(["B"]), set(["A", "C"])))
        >>> H.add_hyperedges(hyperedge_list)
        >>> H.remove_hyperedges(xyz)

        """
        for hyperedge_id in hyperedge_ids:
            self.remove_hyperedge(hyperedge_id)

    def get_hyperedge_id(self, tail, head):
        """From a tail and head set of nodes, returns the ID of the hyperedge
        that these sets comprise.

        :param tail: iterable container of references to nodes in the
                    tail of the hyperedge to be added
        :param head: iterable container of references to nodes in the
                    head of the hyperedge to be added
        :returns: str -- ID of the hyperedge that has that the specified
                tail and head sets comprise.
        :raises: ValueError - No such hyperedge exists.

        Examples
        --------
        >>> H = DirectedHypergraph()
        >>> xyz = hyperedge_list = (["A"], ["B", "C"]), \
                                    (("A", "B"), ("C"), {weight: 2}), \
                                    (set(["B"]), set(["A", "C"])))
        >>> H.add_hyperedges(hyperedge_list)
        >>> x = H.get_hyperedge_id(["A"], ["B", "C"])

        """
        frozen_tail = frozenset(tail)
        frozen_head = frozenset(head)

        if not self.has_hyperedge(frozen_tail, frozen_head):
            raise ValueError("No such hyperedge exists.")

        return self._successors[frozen_tail][frozen_head]

    def get_hyperedge_attribute(self, hyperedge_id, attribute_name):
        """Given a hyperedge ID and the name of an attribute, get a copy
        of that hyperedge's attribute.

        :param hyperedge_id: ID of the hyperedge to retrieve the attribute of.
        :param attribute_name: name of the attribute to retrieve.
        :returns: attribute value of the attribute_name key for the
                specified hyperedge.
        :raises: ValueError -- No such hyperedge exists.
                            -- No such attribute exists.

        Examples
        --------
        >>> H = DirectedHypergraph()
        >>> xyz = hyperedge_list = (["A"], ["B", "C"]), \
                                    (("A", "B"), ("C"), {weight: 2}), \
                                    (set(["B"]), set(["A", "C"])))
        >>> H.add_hyperedges(hyperedge_list)
        >>> attribute = H.get_hyperedge_attribute(xyz[0])

        """
        if not self.has_hyperedge_id(hyperedge_id):
            raise ValueError("No such hyperedge exists.")
        elif attribute_name not in self._hyperedge_attributes[hyperedge_id]:
            raise ValueError("No such attribute exists.")
        else:
            return copy.\
                copy(self._hyperedge_attributes[hyperedge_id][attribute_name])

    def get_hyperedge_tail(self, hyperedge_id):
        """Given a hyperedge ID, get a copy of that hyperedge's tail.

        :param hyperedge_id: ID of the hyperedge to retrieve the tail from.
        :returns: a copy of the container of nodes that the user provided
                as the tail to the hyperedge referenced as hyperedge_id.

        """
        return self.get_hyperedge_attribute(hyperedge_id, "tail")

    def get_hyperedge_head(self, hyperedge_id):
        """Given a hyperedge ID, get a copy of that hyperedge's head.

        :param hyperedge: ID of the hyperedge to retrieve the head from.
        :returns: a copy of the container of nodes that the user provided
            as the head to the hyperedge referenced as hyperedge_id.

        """
        return self.get_hyperedge_attribute(hyperedge_id, "head")

    def get_hyperedge_weight(self, hyperedge_id):
        """Given a hyperedge ID, get that hyperedge's weight.

        :param hyperedge: ID of the hyperedge to retrieve the weight from.
        :returns: a the weight of the hyperedge referenced as hyperedge_id.

        """
        return self.get_hyperedge_attribute(hyperedge_id, "weight")

    def get_node_attribute(self, node, attribute_name):
        """Given a node and the name of an attribute, get a copy
        of that node's attribute.

        :param node: reference to the node to retrieve the attribute of.
        :param attribute_name: name of the attribute to retrieve.
        :returns: attribute value of the attribute_name key for the
                specified node.
        :raises: ValueError -- No such node exists.
                            -- No such attribute exists.

        """
        if not self.has_node(node):
            raise ValueError("No such node exists.")
        elif attribute_name not in self._node_attributes[node]:
            raise ValueError("No such attribute exists.")
        else:
            return copy.\
                copy(self._node_attributes[node][attribute_name])

    def get_forward_star(self, node):
        """Given a node, get a copy of that node's forward star.

        :param node: node to retrieve the forward-star of.
        :returns: set -- set of hyperedge_ids for the hyperedges
                        in the node's forward star.
        :raises: ValueError -- No such node exists.

        """
        if node not in self._node_attributes:
            raise ValueError("No such node exists.")
        return self._forward_star[node].copy()

    def get_backward_star(self, node):
        """Given a node, get a copy of that node's backward star.

        :param node: node to retrieve the backward-star of.
        :returns: set -- set of hyperedge_ids for the hyperedges
                in the node's backward star.
        :raises: ValueError -- No such node exists.

        """
        if node not in self._node_attributes:
            raise ValueError("No such node exists.")
        return self._backward_star[node].copy()

    def get_successors(self, tail):
        """Given a tail set of nodes, get a list of edges of which the node
        set is the tail of each edge.

        :param tail: set of nodes that correspond to the tails of some
                        (possibly empty) set of edges.
        :returns: set -- hyperedge_ids of the hyperedges that have tail
                in the tail.

        """
        frozen_tail = frozenset(tail)
        # If this node set isn't any tail in the hypergraph, then it has
        # no successors; thus, return an empty list
        if frozen_tail not in self._successors:
            return set()

        return set(self._successors[frozen_tail].values())

    def get_predecessors(self, head):
        """Given a head set of nodes, get a list of edges of which the node set
        is the head of each edge.

        :param head: set of nodes that correspond to the heads of some
                        (possibly empty) set of edges.
        :returns: set -- hyperedge_ids of the hyperedges that have head
                in the head.
        """
        frozen_head = frozenset(head)
        # If this node set isn't any head in the hypergraph, then it has
        # no predecessors; thus, return an empty list
        if frozen_head not in self._predecessors:
            return set()

        return set(self._predecessors[frozen_head].values())
