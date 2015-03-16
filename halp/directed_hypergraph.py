"""
.. module:: directed_hypergraph
   :synopsis: Defines DirectedHypergraph class for the basic properties
            of a directed hypergraph, along with the relevant structures
            regarding nodes, hyperedges, adjacency, etc.

"""

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

    Self-loops are allowed, but parallel (multi) hyperedges are not.

    :note: This class uses several data structures to store a directed
        hypergraph. Since these structures must stay in sync (see: __init__),
        we highly recommend that only the public methods be used for accessing
        and modifying the hypergraph.

    Examples:
    Create an empty directed hypergraph (no nodes or hyperedges):

    >>> H = DirectedHypergraph()

    Add nodes (with or without attributes) to the hypergraph
    one at a time (see: add_node) or several at a time (see: add_nodes):

    >>> H.add_nodes(["A", "B", "C", "D"], {color: "black"})

    Add hyperedges (with or without attributes) to the hypergraph one
    at a time (see: add_hyperedge) or several at a time (see: add_hyperedges):

    >>> H.add_hyperedges((["A"], ["B"]), (["A", "B"], ["C", "D"]))

    Update attributes of existing nodes and hyperedges by simulating adding the
    node or hyperedge again, with the [potentially new] attribute appended:

    >>> H.add_node("A", label="sink")
    >>> H.add_hyperedge((["A", "B"], ["C", "D"]), weight=5)

    """

    def __init__(self):
        """Constructor for the DirectedHypergraph class.
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
        # the tail and head (as "__frozen_tail" and "__frozen_head").
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

        Examples:
        ::

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
        :param attr: keyword arguments of attributes of the node;
                    attr's values will override attr_dict's values
                    if both are provided.

        See also:
        add_node

        Examples:
        ::

            >>> H = DirectedHypergraph()
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
        every hyperedge that contains this node in either the head or the tail.

        :param node: reference to the node being added.
        :raises: ValueError -- No such node exists.

        Examples:
        ::

            >>> H = DirectedHypergraph()
            >>> H.add_node("A", label="positive")
            >>> H.remove_node("A")

        """
        if not self.has_node(node):
            raise ValueError("No such node exists.")

        # Remove every hyperedge which is in the forward star of the node
        forward_star = self.get_forward_star(node)
        for hyperedge_id in forward_star:
            self.remove_hyperedge(hyperedge_id)

        # Remove every hyperedge which is in the backward star of the node
        # but that is not also in the forward start of the node (to handle
        # overlapping hyperedges)
        backward_star = self.get_backward_star(node)
        for hyperedge_id in backward_star - forward_star:
            self.remove_hyperedge(hyperedge_id)

        # Remove node's forward and backward star
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

        See also:
        remove_node

        Examples:
        ::

            >>> H = DirectedHypergraph()
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
        """Returns the set of nodes that are currently in the hypergraph.

        :returns: set -- all nodes currently in the hypergraph

        """
        return set(self._node_attributes.keys())

    def node_iterator(self):
        """Provides an iterator over the nodes.

        """
        return iter(self._node_attributes)

    def get_node_attribute(self, node, attribute_name):
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
        """Returns the next [consecutive] ID to be assigned
            to a hyperedge.
        :returns: str -- hyperedge ID to be assigned.

        """
        self._current_hyperedge_id += 1
        return "e" + str(self._current_hyperedge_id)

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
        :param attr: keyword arguments of attributes of the hyperedge;
                    attr's values will override attr_dict's values
                    if both are provided.
        :returns: str -- the ID of the hyperedge that was added.
        :raises: ValueError -- tail and head arguments cannot both be empty.

        Examples:
        ::

            >>> H = DirectedHypergraph()
            >>> x = H.add_hyperedge(["A", "B"], ["C", "D"])
            >>> y = H.add_hyperedge(("A", "C"), ("B"), 'weight'=2)
            >>> z = H.add_hyperedge(set(["D"]),
                                    set(["A", "C"]),
                                    {color: "red"})

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
                {"tail": tail, "__frozen_tail": frozen_tail,
                 "head": head, "__frozen_head": frozen_head,
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
            If any node in the tail or head of any hyperedge has not
            previously been added to the hypergraph, it will automatically
            be added here. Hyperedges without a "weight" attribute specified
            will be assigned the default value of 1.

        :param hyperedges: iterable container to either tuples of
                    (tail reference, head reference) OR tuples of
                    (tail reference, head reference, attribute dictionary);
                    if an attribute dictionary is provided in the tuple,
                    its values will override both attr_dict's and attr's
                    values.
        :param attr_dict: dictionary of attributes shared by all
                    the hyperedges.
        :param attr: keyword arguments of attributes of the hyperedges;
                    attr's values will override attr_dict's values
                    if both are provided.
        :returns: list -- the IDs of the hyperedges added in the order
                    specified by the hyperedges container's iterator.

        See also:
        add_hyperedge

        Examples:
        ::

            >>> H = DirectedHypergraph()
            >>> xyz = hyperedge_list = ((["A", "B"], ["C", "D"]),
                                        (("A", "C"), ("B"), {'weight': 2}),
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

    def remove_hyperedge(self, hyperedge_id):
        """Removes a hyperedge and its attributes from the hypergraph.

        :param hyperedge_id: ID of the hyperedge to be removed.
        :raises: ValueError -- No such hyperedge exists.

        Examples:
        ::

            >>> H = DirectedHypergraph()
            >>> xyz = hyperedge_list = ((["A"], ["B", "C"]),
                                        (("A", "B"), ("C"), {'weight': 2}),
                                        (set(["B"]), set(["A", "C"])))
            >>> H.add_hyperedges(hyperedge_list)
            >>> H.remove_hyperedge(xyz[0])

        """
        if not self.has_hyperedge_id(hyperedge_id):
            raise ValueError("No such hyperedge exists.")

        frozen_tail = \
            self._hyperedge_attributes[hyperedge_id]["__frozen_tail"]
        frozen_head = \
            self._hyperedge_attributes[hyperedge_id]["__frozen_head"]

        # Remove this hyperedge from the forward-star of every tail node
        for node in frozen_tail:
            self._forward_star[node].remove(hyperedge_id)
        # Remove this hyperedge from the backward-star of every head node
        for node in frozen_head:
            self._backward_star[node].remove(hyperedge_id)

        # Remove frozen_head as a successor of frozen_tail
        del self._successors[frozen_tail][frozen_head]
        # If that tail is no longer the tail of any hyperedge, remove it
        # from the successors dictionary
        if self._successors[frozen_tail] == {}:
            del self._successors[frozen_tail]
        # Remove frozen_tail as a predecessor of frozen_head
        del self._predecessors[frozen_head][frozen_tail]
        # If that head is no longer the head of any hyperedge, remove it
        # from the predecessors dictionary
        if self._predecessors[frozen_head] == {}:
            del self._predecessors[frozen_head]

        # Remove hyperedge's attributes dictionary
        del self._hyperedge_attributes[hyperedge_id]

    def remove_hyperedges(self, hyperedge_ids):
        """Removes a set of hyperedges and their attributes from
        the hypergraph.

        :param hyperedge_ids: iterable container of IDs of the hyperedges
                        to be removed.
        :raises: ValueError -- No such hyperedge exists.

        See also:
        remove_hyperedge

        Examples:
        ::

            >>> H = DirectedHypergraph()
            >>> hyperedge_list = ((["A"], ["B", "C"]),
                                  (("A", "B"), ("C"), {'weight': 2}),
                                  (set(["B"]), set(["A", "C"])))
            >>> hyperedge_ids = H.add_hyperedges(hyperedge_list)
            >>> H.remove_hyperedges(hyperedge_ids)

        """
        for hyperedge_id in hyperedge_ids:
            self.remove_hyperedge(hyperedge_id)

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

    def get_hyperedge_id_set(self):
        """Returns the set of IDs of hyperedges that are currently
        in the hypergraph.

        :returns: set -- all IDs of hyperedges currently in the hypergraph

        """
        return set(self._hyperedge_attributes.keys())

    def hyperedge_id_iterator(self):
        """Provides an iterator over the list of hyperedge IDs.

        """
        return iter(self._hyperedge_attributes)

    def get_hyperedge_id(self, tail, head):
        """From a tail and head set of nodes, returns the ID of the hyperedge
        that these sets comprise.

        :param tail: iterable container of references to nodes in the
                    tail of the hyperedge to be added
        :param head: iterable container of references to nodes in the
                    head of the hyperedge to be added
        :returns: str -- ID of the hyperedge that has that the specified
                tail and head sets comprise.
        :raises: ValueError -- No such hyperedge exists.

        Examples:
        ::

            >>> H = DirectedHypergraph()
            >>> hyperedge_list = (["A"], ["B", "C"]),
                                  (("A", "B"), ("C"), {weight: 2}),
                                  (set(["B"]), set(["A", "C"])))
            >>> hyperedge_ids = H.add_hyperedges(hyperedge_list)
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
        :raises: ValueError -- No such attribute exists.

        Examples:
        ::

            >>> H = DirectedHypergraph()
            >>> hyperedge_list = (["A"], ["B", "C"]),
                                  (("A", "B"), ("C"), {weight: 2}),
                                  (set(["B"]), set(["A", "C"])))
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
                (except the private __frozen_tail and __frozen_head entries).
        :raises: ValueError -- No such hyperedge exists.

        """
        if not self.has_hyperedge_id(hyperedge_id):
            raise ValueError("No such hyperedge exists.")
        dict_to_copy = self._hyperedge_attributes[hyperedge_id].items()
        attributes = {}
        for attr_name, attr_value in dict_to_copy:
            if attr_name not in ("__frozen_tail", "__frozen_head"):
                attributes[attr_name] = copy.copy(attr_value)
        return attributes

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

    # TODO: Make this a property of the hypergraph that stays updated with
    # the hypergraph, for constant-time calls.
    def is_B_hypergraph(self):
        """Indicates whether the hypergraph is a B-hypergraph.
        In a B-hypergraph, all hyperedges are B-hyperedges -- that is, every
        hyperedge has exactly one node in the head.

        :returns: bool -- True iff the hypergraph is a B-hypergraph.

        """
        for hyperedge_id in self._hyperedge_attributes:
            head = self.get_hyperedge_head(hyperedge_id)
            if len(head) > 1:
                return False
        return True

    # TODO: Make this a property of the hypergraph that stays updated with
    # the hypergraph, for constant-time calls.
    def is_F_hypergraph(self):
        """Indicates whether the hypergraph is an F-hypergraph.
        In an F-hypergraph, all hyperedges are F-hyperedges -- that is, every
        hyperedge has exactly one node in the tail.

        :returns: bool -- True iff the hypergraph is an F-hypergraph.

        """
        for hyperedge_id in self._hyperedge_attributes:
            tail = self.get_hyperedge_tail(hyperedge_id)
            if len(tail) > 1:
                return False
        return True

    # TODO: Make this a property of the hypergraph that stays updated with
    # the hypergraph, for constant-time calls.
    def is_BF_hypergraph(self):
        """Indicates whether the hypergraph is a BF-hypergraph.
        A BF-hypergraph consists of only B-hyperedges and F-hyperedges.
        See "is_B_hypergraph" or "is_F_hypergraph" for more details.

        :returns: bool -- True iff the hypergraph is an F-hypergraph.

        """
        for hyperedge_id in self._hyperedge_attributes:
            tail = self.get_hyperedge_tail(hyperedge_id)
            head = self.get_hyperedge_head(hyperedge_id)
            if len(tail) > 1 and len(head) > 1:
                return False
        return True

    def copy(self):
        """Creates a new DirectedHypergraph object with the same node and
        hyperedge structure.
        Copies of the nodes' and hyperedges' attributes are stored
        and used in the new hypergraph.

        :returns: DirectedHypergraph -- a new hypergraph that is a copy of
                the current hypergraph

        """
        return self.__copy__()

    def __copy__(self):
        """Creates a new DirectedHypergraph object with the same node and
        hyperedge structure.
        Copies of the nodes' and hyperedges' attributes are stored
        and used in the new hypergraph.

        :returns: DirectedHypergraph -- a new hypergraph that is a copy of
                the current hypergraph

        """
        new_H = DirectedHypergraph()

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

        # Copy the original hypergraph's forward star and backward star
        new_H._backward_star = self._backward_star.copy()
        for node in self._node_attributes.keys():
            new_H._backward_star[node] = \
                self._backward_star[node].copy()
            new_H._forward_star[node] = \
                self._forward_star[node].copy()

        # Copy the original hypergraph's successors
        for frozen_tail, successor_dict in self._successors.items():
            new_H._successors[frozen_tail] = successor_dict.copy()
        # Copy the original hypergraph's predecessors
        for frozen_head, predecessor_dict in self._predecessors.items():
            new_H._predecessors[frozen_head] = predecessor_dict.copy()

        # Start assigning edge labels at the same
        new_H._current_hyperedge_id = self._current_hyperedge_id

        return new_H

    def get_symmetric_image(self):
        """Creates a new DirectedHypergraph object that is the symmetric
        image of this hypergraph (i.e., identical hypergraph with all
        edge directions reversed).
        Copies of each of the nodes' and hyperedges' attributes are stored
        and used in the new hypergraph.

        :returns: DirectedHypergraph -- a new hypergraph that is the symmetric
                image of the current hypergraph.

        """
        new_H = self.copy()

        # No change to _node_attributes necessary, as nodes remain the same

        # Reverse the tail and head (and __frozen_tail and __frozen_head) for
        # every hyperedge
        for hyperedge_id in self.get_hyperedge_id_set():
            attr_dict = new_H._hyperedge_attributes[hyperedge_id]
            attr_dict["tail"], attr_dict["head"] = \
                attr_dict["head"], attr_dict["tail"]
            attr_dict["__frozen_tail"], attr_dict["__frozen_head"] = \
                attr_dict["__frozen_head"], attr_dict["__frozen_tail"]

        # Reverse the definition of forward star and backward star
        new_H._forward_star, new_H._backward_star = \
            new_H._backward_star, new_H._forward_star

        # Reverse the definition of successor and predecessor
        new_H._successors, new_H._predecessors = \
            new_H._predecessors, new_H._successors

        return new_H

    def get_induced_subhypergraph(self, nodes):
        """Gives a new hypergraph that is the subhypergraph of the current
        hypergraph induced by the provided set of nodes. That is, the induced
        subhypergraph's node set corresponds precisely to the nodes provided,
        and the coressponding hyperedges in the subhypergraph are only those
        from the original graph consist of tail and head sets that are subsets
        of the provided nodes.

        :param nodes: the set of nodes to find the induced subhypergraph of.
        :returns: DirectedHypergraph -- the subhypergraph induced on the
                provided nodes.

        """
        sub_H = self.copy()
        sub_H.remove_nodes(sub_H.get_node_set() - set(nodes))
        return sub_H

    # TODO: make reading more extensible (attributes, variable ordering, etc.)
    def read(self, file_name, delim=',', sep='\t'):
        """Read a directed hypergraph from a file, where nodes are
        represented as strings.
        Each column is separated by "sep", and the individual
        tail nodes and head nodes are delimited by "delim".
        The header line is currently ignored, but columns should be of
        the format:
        tailnode1[delim]..tailnodeM[sep]headnode1[delim]..headnodeN[sep]weight

        As a concrete example, an arbitrary line with delim=',' and
        sep='    ' (4 spaces) may look like:
        ::

            x1,x2    x3,x4,x5    12

        which defines a hyperedge of weight 12 from a tail set containing
        nodes "x1" and "x2" to a head set containing nodes "x3", "x4", and "x5"

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
            if not (2 <= len(words) <= 3):
                raise \
                    IOError("Line {} ".format(line_number) +
                            "contains {} ".format(len(words)) +
                            "columns -- must contain only 2 or 3.")

            tail = set(words[0].split(delim))
            head = set(words[1].split(delim))
            if len(words) == 3:
                weight = float(words[2].split(delim)[0])
            else:
                weight = 1
            self.add_hyperedge(tail, head, weight=weight)

            line_number += 1

        in_file.close()

    # TODO: make writing more extensible (attributes, variable ordering, etc.)
    def write(self, file_name, delim=',', sep='\t'):
        """Write a directed hypergraph to a file, where nodes are
        represented as strings.
        Each column is separated by "sep", and the individual
        tail nodes and head nodes are delimited by "delim".
        The header line is currently ignored, but columns should be of
        the format:
        tailnode1[delim]..tailnodeM[sep]headnode1[delim]..headnodeN[sep]weight

        As a concrete example, an arbitrary line with delim=',' and
        sep='    ' (4 spaces) may look like:
        ::

            x1,x2    x3,x4,x5    12

        which defines a hyperedge of weight 12 from a tail set containing
        nodes "x1" and "x2" to a head set containing nodes "x3", "x4", and "x5"

        """
        out_file = open(file_name, 'w')

        # write first header line
        out_file.write("tail" + sep + "head" + sep + "weight\n")

        for hyperedge_id in self.get_hyperedge_id_set():
            line = ""
            # Write each tail node to the line, separated by delim
            for tail_node in self.get_hyperedge_tail(hyperedge_id):
                line += tail_node + delim
            # Remove last (extra) delim
            line = line[:-1]

            # Add sep between columns
            line += sep

            # Write each head node to the line, separated by delim
            for head_node in self.get_hyperedge_head(hyperedge_id):
                line += head_node + delim
            # Remove last (extra) delim
            line = line[:-1]

            # Write the weight to the line and end the line
            line += sep + str(self.get_hyperedge_weight(hyperedge_id)) + "\n"

            out_file.write(line)

        out_file.close()

    def _check_hyperedge_attributes_consistency(self):
        """Consistency Check 1: consider all hyperedge IDs listed in
        _hyperedge_attributes

        :raises: ValueError -- detected inconsistency among dictionaries

        """
        # required_attrs are attributes that every hyperedge must have.
        required_attrs = ['weight', 'tail', 'head',
                          '__frozen_tail', '__frozen_head']

        # Get list of hyperedge_ids from the hyperedge attributes dict
        hyperedge_ids_from_attributes = set(self._hyperedge_attributes.keys())

        # Perform consistency checks on each hyperedge id.
        for hyperedge_id in hyperedge_ids_from_attributes:

            # Check 1.1: make sure every hyperedge id has a weight,
            # tail, head, frozen tail, and frozen head
            hyperedge_attr_dict = self._hyperedge_attributes[hyperedge_id]
            for required_attr in required_attrs:
                if required_attr not in hyperedge_attr_dict:
                    raise ValueError(
                        'Consistency Check 1.1 Failed: hyperedge ' +
                        'attribute dictionary for hyperedge_id ' +
                        '%s is missing required attribute %s' %
                        (hyperedge_id, required_attr))

            # Check 1.2: make sure frozenset(tail) == __frozen_tail
            if frozenset(hyperedge_attr_dict['tail']) != \
               hyperedge_attr_dict['__frozen_tail']:
                raise ValueError(
                    'Consistency Check 1.2 Failed: frozenset ' +
                    'tail is different from __frozen_tail ' +
                    'attribute for hyperedge id %s' % (hyperedge_id))

            # Check 1.3: make sure frozenset(head) == __frozen_head
            if frozenset(hyperedge_attr_dict['head']) != \
               hyperedge_attr_dict['__frozen_head']:
                raise ValueError(
                    'Consistency Check 1.3 Failed: frozenset ' +
                    'head is different from __frozen_head ' +
                    'attribute for hyperedge id %s' % (hyperedge_id))

            # get tail and head frozenset
            tailset = hyperedge_attr_dict['__frozen_tail']
            headset = hyperedge_attr_dict['__frozen_head']

            # Check 1.4: make sure successors dictionary contains the
            # hyperedge id. Need to also check that tailset and
            # headset are entries into the dict.
            if tailset not in self._successors or \
               headset not in self._successors[tailset] or \
               self._successors[tailset][headset] != hyperedge_id:
                raise ValueError(
                    'Consistency Check 1.4 Failed: hyperedge ' +
                    'id %s not in self._successors.' % (hyperedge_id))

            # Check 1.5: make sure predecessors dictionary contains
            # the hyperedge id. Need to also check that headset and
            # tailset are entries into the dict.
            if headset not in self._predecessors or \
               tailset not in self._predecessors[headset] or \
               self._predecessors[headset][tailset] != hyperedge_id:
                raise ValueError(
                    'Consistency Check 1.5 Failed: hyperedge ' +
                    'id %s not in self._predecessors.' % (hyperedge_id))

            # Check 1.6: make sure every tail node in tailset
            # contains the hyperedge_id in the forward star.
            for tail_node in tailset:
                if hyperedge_id not in self._forward_star[tail_node]:
                    raise ValueError(
                        'Consistency Check 1.6 Failed: hyperedge ' +
                        'id ' + hyperedge_id + ' is not in the ' +
                        'forward star of tail node ' + tail_node)

            # Check 1.7: make sure every head node in headset
            # contains the hyperedge_id in the backward star.
            for head_node in headset:
                if hyperedge_id not in self._backward_star[head_node]:
                    raise ValueError(
                        'Consistency Check 1.7 Failed: hyperedge ' +
                        'id ' + hyperedge_id + ' is not in the ' +
                        'backward star of head node ' + tail_node)

    def _check_node_attributes_consistency(self):
        """Consistency Check 2: consider all nodes listed in
        _node_attributes

        :raises: ValueError -- detected inconsistency among dictionaries

        """
        # Get list of nodes from the node attributes dict
        nodes_from_attributes = set(self._node_attributes.keys())

        # Perform consistency checks on each node.
        for node in nodes_from_attributes:

            # Check 2.1: make sure that the forward star for the node
            # exists.
            if node not in self._forward_star:
                raise ValueError(
                    'Consistency Check 2.1 Failed: node ' +
                    '%s not in forward star dict' % (str(node)))

            # Check 2.2: make sure that the backward star for the node
            # exists.
            if node not in self._backward_star:
                raise ValueError(
                    'Consistency Check 2.2 Failed: node ' +
                    '%s not in backward star dict' % (str(node)))

            # Get backward star and forward star
            node_fstar = self._forward_star[node]
            node_bstar = self._backward_star[node]

            # Check 2.3: make sure every hyperedge id in the forward
            # star contains the node in the tail
            for hyperedge_id in node_fstar:
                if hyperedge_id not in self._hyperedge_attributes or \
                   node not in \
                   self._hyperedge_attributes[hyperedge_id]['tail']:
                    raise ValueError(
                        'Consistency Check 2.3 Failed: node %s ' % str(node) +
                        'has hyperedge id %s in the forward ' % hyperedge_id +
                        'star, but %s is not in the tail of ' % str(node) +
                        '%s' % hyperedge_id)

            # Check 2.4: make sure every hyperedge id in the backward
            # star contains the node in the head
            for hyperedge_id in node_bstar:
                if hyperedge_id not in self._hyperedge_attributes or \
                   node not in \
                   self._hyperedge_attributes[hyperedge_id]['head']:
                    raise ValueError(
                        'Consistency Check 2.4 Failed: node %s ' % str(node) +
                        'has hyperedge id %s in the forward ' % hyperedge_id +
                        'star, but %s is not in the tail of ' % str(node) +
                        '%s' % hyperedge_id)

    def _check_predecessor_successor_consistency(self):
        """Consistency Check 3: predecessor/successor symmetry

        :raises: ValueError -- detected inconsistency among dictionaries

        """
        # Check 3.1: ensure that predecessors has the same headsets
        # that successors has
        predecessor_heads = set(self._predecessors.keys())
        successor_heads = set()
        for key, value in self._successors.items():
            successor_heads |= set(value.keys())
        if predecessor_heads != successor_heads:
            raise ValueError(
                'Consistency Check 3.1 Failed: successors and predecessors ' +
                'do not contain the same head sets \n' +
                'predecessor heads: %s \n' % (predecessor_heads) +
                'successor heads: %s' % (successor_heads))

        # Check 3.2: ensure that predecessors has the same tailsets
        # that successors has
        predecessor_tails = set()
        successor_tails = set(self._successors.keys())
        for key, value in self._predecessors.items():
            predecessor_tails |= set(value.keys())
        if successor_tails != predecessor_tails:
            raise ValueError(
                'Consistency Check 3.2 Failed: successors and predecessors ' +
                'do not contain the same tail sets \n' +
                'predecessor tails: %s \n' % (predecessor_tails) +
                'successor tails: %s' % (successor_tails))

        # Check 3.3: iterate through predecessors; check successor
        # symmetry
        for headset in self._predecessors.keys():
            for tailset in self._predecessors[headset].keys():
                if self._predecessors[headset][tailset] != \
                        self._successors[tailset][headset]:
                    raise ValueError(
                        'Consistency Check 3.3 Failed: ' +
                        'headset = %s, ' % headset +
                        'tailset = %s, ' % tailset +
                        'but predecessors[headset][tailset] = ' +
                        '%s ' % self._predecessors[headset][tailset] +
                        'and successors[tailset][headset] = ' +
                        '%s ' % self._successors[tailset][headset])

    def _check_hyperedge_id_consistency(self):
        """Consistency Check 4: check for misplaced hyperedge ids

        :raises: ValueError -- detected inconsistency among dictionaries

        """
        # Get list of hyperedge_ids from the hyperedge attributes dict
        hyperedge_ids_from_attributes = set(self._hyperedge_attributes.keys())

        # get hyperedge ids in the forward star
        forward_star_hyperedge_ids = set()
        for hyperedge_id_set in self._forward_star.values():
            forward_star_hyperedge_ids.update(hyperedge_id_set)

        # get hyperedge ids in the backward star
        backward_star_hyperedge_ids = set()
        for hyperedge_id_set in self._backward_star.values():
            backward_star_hyperedge_ids.update(hyperedge_id_set)

        # Check 4.1: hyperedge ids in the forward star must be the
        # same as the hyperedge ids from attributes
        if forward_star_hyperedge_ids != hyperedge_ids_from_attributes:
            raise ValueError(
                'Consistency Check 4.1 Failed: hyperedge ids ' +
                'are different in the forward star ' +
                'values and the hyperedge ids from ' +
                'attribute keys.')

        # Check 4.2: hyperedge ids in the backward star must be the
        # same as the hyperedge ids from attributes
        if backward_star_hyperedge_ids != hyperedge_ids_from_attributes:
            raise ValueError(
                'Consistency Check 4.2 Failed: hyperedge ids ' +
                'are different in the backward star ' +
                'values and the hyperedge ids from ' +
                'attribute keys.')

        # Note that by Check 4.1 and 4.2, forward_star_hyperedge_ids =
        # backward_star_hyperedge_ids

        # get hyperedge ids in the predecessors dict
        predecessor_hyperedge_ids = set()
        for all_tails_from_predecessor in self._predecessors.values():
            for hyperedge_id in all_tails_from_predecessor.values():
                predecessor_hyperedge_ids.add(hyperedge_id)

        # get hyperedge ids in the successors dict
        successor_hyperedge_ids = set()
        for all_heads_from_successor in self._successors.values():
            for hyperedge_id in all_heads_from_successor.values():
                successor_hyperedge_ids.add(hyperedge_id)

        # Check 4.3: hyperedge ids in the predecessor dict must be the
        # same as the hyperedge ids from attributes
        if predecessor_hyperedge_ids != hyperedge_ids_from_attributes:
            raise ValueError(
                'Consistency Check 4.3 Failed: hyperedge ids are ' +
                'different in the predecessor values and ' +
                'hyperedge ids from attribute keys.')

        # Check 4.4: hyperedge ids in the successor dict must be the
        # same as the hyperedge ids from attributes
        if successor_hyperedge_ids != hyperedge_ids_from_attributes:
            raise ValueError(
                'Consistency Check 4.4 Failed: hyperedge ids are ' +
                'different in the successor values and ' +
                'hyperedge ids from attribute keys.')

        # Note that by Check 4.3 and 4.4, predecessor_hyperedge_ids =
        # successor_hyperedge_ids

        # Note that by Check 4.1 - 4.4,
        # predecessor_hyperedge_ids = successor_hyperedge_ids =
        # forward_star_hyperedge_ids = backward_star_hyperedge_ids

    def _check_node_consistency(self):
        """Consistency Check 5: check for misplaced nodes

        :raises: ValueError -- detected inconsistency among dictionaries

        """
        # Get list of nodes from the node attributes dict
        nodes_from_attributes = set(self._node_attributes.keys())

        # Get list of hyperedge_ids from the hyperedge attributes dict
        hyperedge_ids_from_attributes = set(self._hyperedge_attributes.keys())

        # Check 5.1: all nodes in the forward star must be in the
        # nodes from attributes
        forward_diff = set(self._forward_star.keys()) - nodes_from_attributes
        if forward_diff != set():
            raise ValueError(
                'Consistency Check 5.1 Failed: nodes %s ' % forward_diff +
                '(from forward star keys) is not in the node ' +
                'attribute dict.')

        # Check 5.2: all nodes in the backward star must be in the
        # nodes from attributes
        backward_diff = set(self._backward_star.keys()) - nodes_from_attributes
        if backward_diff != set():
            raise ValueError(
                'Consistency Check 5.2 Failed: node %s ' % backward_diff +
                '(from backward star keys) is not in the node ' +
                'attribute dict.')

        # Note that, by Check 5.1 and 5.2, self._forward_star.keys() =
        # self._backward_star.keys().

        # Check 5.3: all nodes in hyperedge_attributes dictionary must
        # be in the nodes from attributes.
        for hyperedge_id in hyperedge_ids_from_attributes:
            for tailnode in \
                    self._hyperedge_attributes[hyperedge_id]['tail']:
                if tailnode not in nodes_from_attributes:
                    raise ValueError(
                        'Consistency Check 5.3.1 Failed: tail ' +
                        'node %s of ' % tailnode +
                        'of hyperedge id %s ' % hyperedge_id +
                        'is not in node attribute dict')

            for headnode in self._hyperedge_attributes[hyperedge_id]['head']:
                if headnode not in nodes_from_attributes:
                    raise ValueError(
                        'Consistency Check 5.3.2 Failed: head ' +
                        'node %s of ' % headnode +
                        'of hyperedge id %s ' % hyperedge_id +
                        'is not in node attribute dict')

        # get set of nodes in predecessor dictionary.
        # adds both nodes in headset and nodes in tailset.
        nodes_in_predecessor_dict = set()
        for headset in self._predecessors.keys():
            nodes_in_predecessor_dict.update(headset)
            for tailset in self._predecessors[headset].keys():
                nodes_in_predecessor_dict.update(tailset)

        # get set of nodes in successor dictionary.
        # adds both nodes in headset and nodes in tailset.
        nodes_in_successor_dict = set()
        for headset in self._successors.keys():
            nodes_in_successor_dict.update(headset)
            for tailset in self._successors[headset].keys():
                nodes_in_successor_dict.update(tailset)

        # Check 5.4: the set of nodes in successor dict is the same as
        # the set of nodes in the predecessor dict
        if nodes_in_predecessor_dict != nodes_in_successor_dict:
            raise ValueError(
                'Consistency Check 5.4 Failed: nodes in ' +
                'successor dict are different than nodes ' +
                'in predecessor dict')

        # Check 5.5: all nodes in predecessor and successor dict must
        # be in the nodes from attributes (since 5.4 ensures they're the same)
        for node in nodes_in_predecessor_dict:
            if node not in nodes_from_attributes:
                raise ValueError(
                    'Consistency Check 5.5 Failed: node %s ' % node +
                    'from predecessor or successor dictionary ' +
                    'is not in node attribute dict')

    def _check_consistency(self):
        """Compares the contents of the six dictionaries and ensures
        that they are consistent with each other, raising a ValueError
        if there is any inconsistency among the dictionaries. This
        function is used in testing when modifying hypergraphs. The
        consistency checks are divided into the following groups:

        1. hyperedge_id consistency (using hyperedge_attribute keys)
        2. node consistency (using node_attribute keys)
        3. successor/predecessor symmetry
        4. check for misplaced hyperedge ids
        5. check for misplaced nodes

        """
        # TODO: is ValueError the proper exception to raise? Should
        # we make a new exception ("ConsistencyException")?

        # TODO: many of these for loops can be replaced by list
        # comprehension; however the errors currently report the exact
        # condition that fails. Using list comprehension would allow
        # us to report which check fails, but not which node/hyperedge
        # id/etc.x

        self._check_hyperedge_attributes_consistency()
        self._check_node_attributes_consistency()
        self._check_predecessor_successor_consistency()
        self._check_hyperedge_id_consistency()
        self._check_node_consistency()
