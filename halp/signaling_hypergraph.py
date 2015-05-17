"""
.. module:: signaling_hypergraph
   :synopsis: Defines SignalingHypergraph class for the basic properties
            of a signaling hypergraph, along with the relevant structures
            regarding nodes, hypernodes, signaling hyperedges, adjacency, etc.

"""

import copy


class SignalingHypergraph(object):
    """
    The SignalingHypergraph class provides a signaling hypergraph object
    and associated functions for basic properties of signaling hypergraphs.

    A signaling hypergraph contains nodes, hypernodes, and signaling
    hyperedges. A hypernode is a set of nodes. Each signaling hyperedge
    connects a tail set of hypernodes to a head set of hypernodes, and has an
    associated set of positive regulators (a set of hypernodes) and an
    associated set of negative regulators (a set of hypernodes).
    The head set cannot be empty, and the union of the tail set, the positive
    regulator set, and the negative regulator set cannot be empty.

    A node is simply any hashable type. See "add_node" or "add_nodes" for
    more details.

    A hypernode is also any hashable type, which is associated with a set
    of nodes. See "add_hypernode" or "add_hypernodes" for more details.

    A signaling hyperedge is defined by a four-tuple: the tail hypernodes, the head
    hypernodes, the positive regulator hypernodes, and the negative regulator
    hypernodes. Upon the addition of each hyperedge, the class assigns and refers to
    each signaling hyperedge by
    an internal ID. See "add_hyperedge" or "add_hyperedges" for more details.

    When adding a hyperedge, the class allows hypernodes to appear in any of
    the four sets.
    
    The class allows adding multiple hyperedges with the same tail and head sets
    to be added if they have different regulator sets.

    :note: This class uses several data structures to store a signaling
        hypergraph. Since these structures must stay in sync (see: __init__),
        we highly recommend that only the public methods be used for accessing
        and modifying the hypergraph.

    """

    def __init__(self):
        """Constructor for the SignalingHypergraph class.
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

        # _hypernode_attributes: a dictionary mapping a hypernode (any
        # hashable type) to a dictionary of attributes of that hypernode.
        #
        # Provides O(1) time access to the attributes of a hypernode.
        #
        # Used in the implementation of methods such as add_hypernode and
        # get_hypernode_attributes.
        #
        self._hypernode_attributes = {}

        # _hyperedge_attributes: a dictionary mapping a hyperedge ID
        # (initially created by the call to add_hyperedge or add_hyperedges)
        # to a dictionary of attributes of that hyperedge.
        # Given a hyperedge ID, _hyperedge_attributes[hyperedge_id] stores
        # the tail of the hyperedge as specified by the user (as "tail"),
        # the head of the hyperedge as specified by the user (as "head"),
        # the positive regulators of the hyperedge as specified by the
        # user (as "pos_regs"), and
        # the negative regulators of the hyperedge as specified by the
        # user (as "neg_regs").
        # For internal purposes, it also stores the frozenset versions of
        # the tail and head (as "__frozen_tail", "__frozen_head",
        # "__frozen_pos_regs", and "__frozen_neg_regs").
        #
        # Provides O(1) time access to the attributes of a hyperedge.
        #
        # Used in the implementation of methods such as add_hyperedge and
        # get_hyperedge_attributes.
        #
        self._hyperedge_attributes = {}

        # _hyperedge_id_map: a dictionary mapping a tuple of
        # (frozen_tail, frozen_head, frozen_pos_regs, frozen_neg_regs)
        # to the id of the hyperedge defined by that tuple.
        #
        # Provides O(1) time access to the ID of a hyperedge.
        #
        self._hyperedge_id_map = {}

        # The forward star of a hypernode is the set of hyperedges such that
        # the hypernode is in the tail of each hyperedge in that set.
        #
        # _forward_star: a dictionary mapping a hypernode to the set of
        # hyperedges that are in that hypernode's forward star.
        #
        # Provides O(1) time access to a reference to the set of outgoing
        # hyperedges from a hypernode.
        #
        # Used in the implementation of methods such as add_hypernode and
        # remove_hyperedge.
        #
        self._forward_star = {}

        # The backward star of a hypernode is the set of hyperedges such that
        # the hypernode is in the head of each hyperedge in that set.
        #
        # _backward_star: a dictionary mapping a hypernode to the set of
        # hyperedges that are in that hypernode's backward star.
        #
        # Provides O(1) time access to a reference to the set of incoming
        # hyperedges from a hypernode.
        #
        # Used in the implementation of methods such as add_hypernode and
        # remove_hyperedge.
        #
        self._backward_star = {}

        # The positive regulation star of a hypernode is the set of hyperedges
        # such that the hypernode is a positive regulator of each hyperedge in
        # that set.
        #
        # _positive_regulation_star: a dictionary mapping a hypernode
        # to the set of hyperedges that are in that hypernode's
        # positive regulation star.
        #
        # Provides O(1) time access to a reference to the set of positively
        # regulated hyperedges by a hypernode.
        #
        # Used in the implementation of methods such as add_hypernode and
        # remove_hyperedge.
        #
        self._positive_regulation_star = {}

        # The negative regulation star of a hypernode is the set of hyperedges
        # such that the hypernode is a negative regulator of each hyperedge in
        # that set.
        #
        # _negative_regulation_star: a dictionary mapping a hypernode
        # to the set of hyperedges that are in that hypernode's
        # negative regulation star.
        #
        # Provides O(1) time access to a reference to the set of negatively
        # regulated hyperedges by a hypernode.
        #
        # Used in the implementation of methods such as add_hypernode and
        # remove_hyperedge.
        #
        self._negative_regulation_star = {}

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

        # _positive_regulations: a dictionary mapping a frozen positive
        # regulator set of hypernodes to the set IDs of the hyperedges
        # that they positively regulate. We represent each regulator set
        # by a frozenset, so that the structure is hashable.
        #
        # Provides O(1) time access to the set of IDs of the of the hyperedges
        # being positively regulated by a specific frozenset of positive
        # regulators.
        #
        self._positive_regulations = {}

        # _negative_regulations: a dictionary mapping a frozen negative
        # regulator set of hypernodes to the set IDs of the hyperedges
        # that they negatively regulate. We represent each regulator set
        # by a frozenset, so that the structure is hashable.
        #
        # Provides O(1) time access to the set of IDs of the of the hyperedges
        # being negatively regulated by a specific frozenset of negative
        # regulators.
        #
        self._negative_regulations = {}

        # _current_hyperedge_id: an int representing the hyperedge ID that
        # was most recently assigned by the class (since users don't
        # name/ID their own hyperedges); hyperedges being added are issued
        # ID "e"+_current_hyperedge_id.
        #
        # Since the class takes responsibility for giving hyperedges
        # their IDs (i.e. a unique identifier; could be alternatively viewed
        # as a unique name, label, etc.), it needs to keep track of the issued
        # IDs need to be kept. Issuing consecutive of integer IDs to the
        # hyperedges is a simple strategy to ensure their uniqueness and allow for
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

        :param node: reference to the node.
        :returns: bool -- true iff the node exists in the hypergraph.

        """
        return node in self._node_attributes

    def add_node(self, node, attr_dict=None, **attr):
        """Adds a node to the graph, along with any related attributes
           of the node.

        :param node: reference to the node.
        :param attr_dict: dictionary of attributes of the node.
        :param attr: keyword arguments of attributes of the node;
                    attr's values will override attr_dict's values
                    if both are provided.

        Examples:
        ::

            >>> H = SignalingHypergraph()
            >>> attributes = {label: "positive"}
            >>> H.add_node("A", attributes)
            >>> H.add_node("B", label="negative")
            >>> H.add_node("C", attributes, root=True)

        """
        attr_dict = self._combine_attribute_arguments(attr_dict, attr)

        # If the node hasn't previously been added, add it along
        # with its attributes
        if not self.has_node(node):
            attr_dict["__in_hypernodes"] = set()
            self._node_attributes[node] = attr_dict
        # Otherwise, just update the node's attributes
        else:
            self._node_attributes[node].update(attr_dict)

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

        :param node: reference to the node.
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

        :param node: reference to the node.
        :returns: dict -- copy of each attribute of the specified node.
        :raises: ValueError -- No such node exists.

        """
        if not self.has_node(node):
            raise ValueError("No such node exists.")
        attributes = {}
        for attr_name, attr_value in self._node_attributes[node].items():
            if attr_name != "__in_hypernodes":
                attributes[attr_name] = copy.copy(attr_value)
        return attributes

    def get_hypernodes_containing_node(self, node):
        """Given a node, get the set of the hypernodes that contain it.

        :param node: reference to the node.
        :returns: set -- set of hypernodes that contain the node.
        :raises: ValueError -- No such node exists.

        """
        if not self.has_node(node):
            raise ValueError("No such node exists.")
        containing_hypernodes = \
            self.get_node_attribute(hypernode, "__in_hypernodes")
        return copy.copy(containing_hypernodes)

    def has_hypernode(self, hypernode):
        """Determines if a specific hypernode is present in the hypergraph.

        :param hypernode: reference to hypernode.
        :returns: bool -- true iff the hypernode exists in the hypergraph.

        """
        return hypernode in self._hypernode_attributes

    def _add_hypernode_membership(self, node, hypernode):
        """Adds the given hypernode into the node's "membership" structure,
        indicating that this node is a member of the given hypernode.

        :param node: reference to the node.
        :param hypernode: reference to the hypernode that the given node is
                        a member of.
        :raises: ValueError -- No such node exists.
        :raises: ValueError -- No such hypernode exists.

        """
        if not self.has_node(node):
            raise ValueError("No such node exists.")
        if not self.has_hypernode(hypernode):
            raise ValueError("No such hypernode exists.")

        self._node_attributes[node]["__in_hypernodes"].add(hypernode)

    def _remove_hypernode_membership(self, node, hypernode):
        """Removes the given hypernode from the node's "membership" structure,
        indicating that this node is no longer a member of the given hypernode.

        :param node: reference to the node.
        :param hypernode: reference to the hypernode that the given node is
                        no longer a member of.
        :raises: ValueError -- No such node exists.
        :raises: ValueError -- No such hypernode exists.

        """
        if not self.has_node(node):
            raise ValueError("No such node exists.")
        if not self.has_hypernode(hypernode):
            raise ValueError("No such hypernode exists.")

        self._node_attributes[node]["__in_hypernodes"].remove(hypernode)

    def add_hypernode(self, hypernode, composing_nodes,
                      attr_dict=None, **attr):
        """Adds a hypernode to the hypergraph, along with any related
        attributes of the hypernode.

        :param hypernode: reference to the hypernode being added.
        :param nodes: container of nodes that compose the hypernode.
                    If this is None and hypernode is already present,
                    then just update the attributes of the hypernode.
        :param in_hypernodes: set of references to the hypernodes that the
                    node being added is a member of.
        :param attr_dict: dictionary of attributes of the node.
        :param attr: keyword arguments of attributes of the node;
                    attr's values will override attr_dict's values
                    if both are provided.

        """
        attr_dict = self._combine_attribute_arguments(attr_dict, attr)

        # If the hypernode hasn't previously been added, add it along
        # with its attributes
        if not self.has_hypernode(hypernode):
            if composing_nodes is None:
                raise ValueError(
                    "Hypernode must be composed of at least one node.")
            attr_dict["__composing_nodes"] = composing_nodes
            self._hypernode_attributes[hypernode] = attr_dict
            self._forward_star[hypernode] = set()
            self._backward_star[hypernode] = set()
            self._positive_regulation_star[hypernode] = set()
            self._negative_regulation_star[hypernode] = set()
        # Otherwise, just update the hypernode's attributes
        else:
            self._hypernode_attributes[hypernode].update(attr_dict)
            hyp_attrs = self._hypernode_attributes[hypernode]
            if composing_nodes is not None and composing_nodes != \
               hyp_attrs["__composing_nodes"]:
                raise ValueError("Cannot alter a hypernode's composing nodes.")

        # For every "composing node" added to this hypernode, update
        # those nodes attributes to be members of this hypernode
        for node in composing_nodes:
            _add_hypernode_membership(node, hypernode)

    def add_hypernodes(self, hypernodes, node_mapping,
                       attr_dict=None, **attr):
        """Adds multiple hypernodes to the hypergraph, along with any related
        attributes of the hypernodes.

        :param hypernodes: iterable container to references of the hypernodes.
        :param node_mapping: dictionary mapping  hypernodes to the nodes that
                        they are composed of. Must contain at least the new
                        hypernodes as keys.
        :param attr_dict: dictionary of attributes shared by all the nodes.
        :param attr: keyword arguments of attributes of the node;
                    attr's values will override attr_dict's values
                    if both are provided.
        """
        attr_dict = self._combine_attribute_arguments(attr_dict, attr)

        for hypernode in hypernodes:
            composing_nodes = None
            if hypernode in node_mapping:
                composing_nodes = node_mapping[hypernode]
            self.add_hypernode(hypernode, composing_nodes, attr_dict.copy())

    def get_hypernode_set(self):
        """Returns the set of hypernodes that are currently in the hypergraph.

        :returns: set -- all hypernodes currently in the hypergraph.

        """
        return set(self._hypernode_attributes.keys())

    def hypernode_iterator(self):
        """Provides an iterator over the hypernodes.

        """
        return iter(self._hypernode_attributes)

    def get_hypernode_attribute(self, hypernode, attribute_name):
        """Given a hypernode and the name of an attribute, get a copy
        of that hypernode's attribute.

        :param hypernode: reference to the hypernode to retrieve
                        the attribute of.
        :param attribute_name: name of the attribute to retrieve.
        :returns: attribute value of the attribute_name key for the
                specified hypernode.
        :raises: ValueError -- No such hypernode exists.
        :raises: ValueError -- No such attribute exists.

        """
        if not self.has_hypernode(hypernode):
            raise ValueError("No such hypernode exists.")
        elif attribute_name not in self._hypernode_attributes[node]:
            raise ValueError("No such attribute exists.")
        else:
            return copy.\
                copy(self._hypernode_attributes[hypernode][attribute_name])

    def get_hypernode_attributes(self, hypernode):
        """Given a hypernode, get a dictionary with copies of that
        hypernode's attributes.

        :param hypernode: reference to the hypernode to retrieve
                        the attributes of.
        :returns: dict -- copy of each attribute of the specified hypernode.
        :raises: ValueError -- No such hypernode exists.

        """
        if not self.has_hypernode(hypernode):
            raise ValueError("No such hypernode exists.")
        attributes = {}
        attr_items = self._hypernode_attributes[hypernode].items()
        for attr_name, attr_value in attr_items:
            if attr_name != "__composing_nodes":
                attributes[attr_name] = copy.copy(attr_value)
        return attributes

    def get_nodes_in_hypernode(self, hypernode):
        """Given a hypernode, get the set of the nodes that compose it.

        :param hypernode: reference to the hypernode to retrieve the
                        composing nodes from.
        :returns: set -- set of nodes that compose the hypernode.
        :raises: ValueError -- No such hypernode exists.

        """
        if not self.has_hypernode(hypernode):
            raise ValueError("No such hypernode exists.")
        composing_nodes = \
            self.get_hypernode_attribute(hypernode, "__composing_nodes")
        return copy.copy(composing_nodes)

    def _assign_next_hyperedge_id(self):
        """Returns the next [consecutive] ID to be assigned
            to a hyperedge.

        :returns: str -- hyperedge ID to be assigned.

        """
        self._current_hyperedge_id += 1
        return "e" + str(self._current_hyperedge_id)

    def _is_valid_hyperedge(self, hyperedge_tuple):
        """Checks if this combination of sets forms a valid hyperedge.

        :param hyperedge_tuple: tuple of four iterable containers,
                            representing the tail, head, positive
                            regulator, and negative regulator sets,
                            repsectively.
        :returns: bool -- true iff this hyperedge tuple represents a
                valid hyperedge.

        """
        tail, head, pos_regs, neg_regs = hyperedge_tuple
        # A hyperedge is valid iff the following hold:
        #   - the union of the tail and regulator sets is non-empty
        #   - the head is non-empty
        if not tail.union(pos_regs).union(neg_regs) and not head:
            return False

    def add_hyperedge(self, tail, head,
                      pos_regs=set(), neg_regs=set(),
                      node_mapping=None, attr_dict=None, **attr):
        """Adds a hyperedge to the hypergraph, along with any related
        attributes of the hyperedge.
        This method will automatically add any hypernode from the tail, head,
        positive regulator, or negative regulator sets that was not already
        in the hypergraph.
        A hyperedge without a "weight" attribute specified will be
        assigned the default value of 1.

        :param tail: iterable container of references to hypernodes in the
                    tail of the hyperedge to be added.
        :param head: iterable container of references to hypernodes in the
                    head of the hyperedge to be added.
        :param pos_regs: iterable container of references to hypernodes that
                    are positive regulators for the hyperedge.
        :param neg_regs: iterable container of references to hypernodes that
                    are negative regulators for the hyperedge.
        :param attr_dict: dictionary of attributes shared by all
                    the hyperedges.
        :param attr: keyword arguments of attributes of the hyperedge;
                    attr's values will override attr_dict's values
                    if both are provided.
        :returns: str -- the ID of the hyperedge that was added.
        :raises: ValueError -- tail and head arguments cannot both be empty.

        """
        attr_dict = self._combine_attribute_arguments(attr_dict, attr)

        # Use frozensets for tail and head sets to allow for hashable keys
        frozen_tail = frozenset(tail)
        frozen_head = frozenset(head)
        frozen_pos_regs = frozenset(pos_regs)
        frozen_neg_regs = frozenset(neg_regs)

        h_edge = (frozen_tail, frozen_head, frozen_pos_regs, frozen_neg_regs)

        if not self._is_valid_hyperedge(tail, head, pos_regs, neg_regs):
            raise ValueError("tail and head arguments \
                              cannot both be empty.")

        # Initialize a successor dictionary for the tail and head, respectively
        if frozen_tail not in self._successors:
            self._successors[frozen_tail] = set()
        if frozen_head not in self._predecessors:
            self._predecessors[frozen_head] = set()
        # Initialize a regulations dictionary for the positive regulators and
        # negative regulators, respectively
        if frozen_pos_regs not in self._positive_regulations:
            self._positive_regulations[frozen_pos_regs] = set()
        if frozen_neg_regs not in self._negative_regulations:
            self._negative_regulations[frozen_neg_regs] = set()

        is_new_hyperedge = not self.has_hyperedge(h_edge)
        if is_new_hyperedge:
            # Add hypernodes contained in the hyperedge to the
            # hypergraph (if not already present)
            hypernodes = tail.union(head).union(pos_regs).union(neg_regs)
            self.add_hypernodes(hypernodes, node_mapping)

            # Create new hyperedge ID to use as reference for that hyperedge
            h_id = self._assign_next_hyperedge_id()

            # Map this hyperedge to this hyperedge ID
            self._hyperedge_id_map[h_edge] = h_id

            # Add hyperedge to the forward-star and to the backward-star
            # for each hypernode in the tail and head sets, respectively
            for hypernode in tail:
                self._forward_star[hypernode].add(h_id)
            for hypernode in head:
                self._backward_star[hypernode].add(h_id)
            # Add hyperedge to the positive-regulation-star and to the
            # negative-regulation-star for each hypernode in the pos_regs
            # and neg_regs sets, respectively
            for hypernode in pos_regs:
                self._positive_regulation_star[hypernode].add(h_id)
            for hypernode in neg_regs:
                self._negative_regulation_star[hypernode].add(h_id)

            # Add the hyperedge as the successors and predecessors
            # of the tail set and head set, respectively
            self._successors[frozen_tail].add(h_id)
            self._predecessors[frozen_head].add(h_id)
            # Add the hyperedge as a regulation of the positive regulator
            # set and negative regulator set, respectively
            self._positive_regulations[frozen_pos_regs].add(h_id)
            self._negative_regulations[frozen_neg_regs].add(h_id)

            # Assign some special attributes to this hyperedge. We assign
            # a default weight of 1 to the hyperedge. We also store the
            # original tail, head, positive regulator, and negative regulator
            # sets in order to return them exactly as the user passed them
            # into add_hyperedge.
            self._hyperedge_attributes[h_id] = \
                {"tail": tail, "__frozen_tail": frozen_tail,
                 "head": head, "__frozen_head": frozen_head,
                 "pos_regs": pos_regs, "__frozen_pos_regs": frozen_pos_regs,
                 "neg_regs": neg_regs, "__frozen_neg_regs": frozen_neg_regs,
                 "weight": 1}
        else:
            # If its not a new hyperedge, just get its hyperedge ID
            h_id = self._hyperedge_id_map[h_edge]

        # Set attributes and return hyperedge ID
        self._hyperedge_attributes[h_id].update(attr_dict)
        return h_id

    def get_hyperedge_id(self, hyperedge_tuple):
        """From the hyperedge tuple of tail, head, positive regulator,
        and negative regulator sets of hypernodes, returns the ID of
        the hyperedge that these sets comprise.

        :param hyperedge_tuple: tuple of four iterable containers,
                            representing the tail, head, positive
                            regulator, and negative regulator sets,
                            repsectively.
        :returns: str -- ID of the hyperedge that has that the specified
                tail and head sets comprise.
        :raises: ValueError -- No such hyperedge exists.

        """
        tail, head, pos_regs, neg_regs = hyperedge_tuple
        frozen_tail = frozenset(tail)
        frozen_head = frozenset(head)
        frozen_pos_regs = frozenset(pos_regs)
        frozen_neg_regs = frozenset(neg_regs)
        h_edge = (frozen_tail, frozen_head, frozen_pos_regs, frozen_neg_regs)

        if not self.has_hyperedge(h_edge):
            raise ValueError("No such hyperedge exists.")

        return self._hyperedge_id_map[h_edge]

    def has_hyperedge(self, hyperedge_tuple):
        """From the hyperedge tuple of tail, head, positive regulator,
        and negative regulator sets of hypernodes, returns whether the
        hyperedge that these sets comprise exists in the hypergraph.

        :param hyperedge_tuple: tuple of four iterable containers (as
                            they were passed in to the library),
                            representing the tail, head, positive
                            regulator, and negative regulator sets,
                            repsectively.
        :returns: bool -- true iff hyperedge is in the hypergraph.

        """
        frozen_tail = frozenset(tail)
        frozen_head = frozenset(head)
        frozen_pos_regs = frozenset(pos_regs)
        frozen_neg_regs = frozenset(neg_regs)
        h_edge = (frozen_tail, frozen_head, frozen_pos_regs, frozen_neg_regs)
        return h_edge in self._hyperedge_id_map

    def has_hyperedge_id(self, hyperedge_id):
        """Returns whether the given hyperedge ID represents a hyperedge
        that is currently in the hypergraph.

        :param hyperedge_id: hyperedge ID to check.
        :returns: bool -- true iff hyperedge ID is in the hypergraph.
        :raises: ValueError -- No such hyperedge exists.

        """
        return hyperedge_id in self._hyperedge_attributes

    def get_hyperedge_id_set(self):
        """Returns the set of IDs of hyperedges that are currently
        in the hypergraph.

        :returns: set -- all IDs of hyperedges currently in the hypergraph.

        """
        return set(self._hypernode_attributes.keys())

    def hypernode_iterator(self):
        """Provides an iterator over the hyperedge IDs.

        """
        return iter(self._hypernode_attributes)

    def remove_hyperedge(self, hyperedge_id):
        """Removes a hyperedge and its attributes from the hypergraph.

        :param hyperedge_id: ID of the hyperedge to be removed.
        :raises: ValueError -- No such hyperedge exists.

        """
        # Ensure hyperedge exists in the hypergraph
        if not self.has_hyperedge_id(hyperedge_id):
            raise ValueError("No such hyperedge exists.")

        h_attrs = self._hyperedge_attributes[hyperedge_id]
        frozen_tail = h_attrs["__frozen_tail"]
        frozen_head = h_attrs["__frozen_head"]
        frozen_pos_regs = h_attrs["__frozen_pos_regs"]
        frozen_neg_regs = h_attrs["__frozen_neg_regs"]
        h_edge = (frozen_tail, frozen_head, frozen_pos_regs, frozen_neg_regs)

        # Remove hyperedge from hyperedge->id map
        del self._hyperedge_id_map[h_edge]

        # Remove hyperedge ID from forward and backward stars for every
        # hypernode in the tail and head sets, respectively
        for hypernode in frozen_tail:
            self._forward_star[hypernode].remove(hyperedge_id)
        for hypernode in frozen_head:
            self._backward_star[hypernode].remove(hyperedge_id)
        # Remove hyperedge ID from forward and backward stars for every
        # hypernode in the tail and head sets, respectively
        for hypernode in frozen_pos_regs:
            self._positive_regulation_star[hypernode].remove(hyperedge_id)
        for hypernode in frozen_neg_regs:
            self._negative_regulation_star[hypernode].remove(hyperedge_id)

        # Remove the hyperedge as the successors and predecessors
        # of the tail set and head set, respectively
        self._successors[frozen_tail].remove(hyperedge_id)
        self._predecessors[frozen_head].remove(hyperedge_id)
        # Remove the hyperedge as a regulation of the positive regulator
        # set and negative regulator set, respectively
        self._positive_regulations[frozen_pos_regs].remove(hyperedge_id)
        self._negative_regulations[frozen_neg_regs].remove(hyperedge_id)

        # Remove hyperedge id from the attributes dictionary
        del self._hyperedge_attributes[hyperedge_id]

    def get_hyperedge_attribute(self, hyperedge_id, attribute_name):
        """Given a hyperedge_id and the name of an attribute, get a copy
        of that hyperedge's attribute.

        :param hyperedge_id: reference to the ID of the hyperedge to
                        retrieve the attribute of.
        :param attribute_name: name of the attribute to retrieve.
        :returns: attribute value of the attribute_name key for the
                specified hypernode.
        :raises: ValueError -- No such hyperedge exists.
        :raises: ValueError -- No such attribute exists.

        """
        if not self.has_hyperedge_id(hyperedge_id):
            raise ValueError("No such hyperedge exists.")
        elif attribute_name not in self._hypernode_attributes[node]:
            raise ValueError("No such attribute exists.")
        else:
            return copy.\
                copy(self._hyperedge_attributes[hyperedge_id][attribute_name])

    def get_hypernode_attributes(self, hyperedge_id):
        """Given a hyperedge ID, get a dictionary with copies of that
        hyperedge's attributes.

        :param hyperedge: reference to the ID of the hyperedge to retrieve
                        the attributes of.
        :returns: dict -- copy of each attribute of the specified hyperedge.
        :raises: ValueError -- No such hyperedge exists.

        """
        if not self.has_hyperedge_id(hyperedge_id):
            raise ValueError("No such hyperedge exists.")
        attributes = {}
        attr_items = self._hyperedge_attributes[hyperedge_id].items()
        internal_names = ("__frozen_tail", "__frozen_head",
                          "__frozen_pos_regs", "__frozen_neg_regs")
        for attr_name, attr_value in attr_items:
            if attr_name not in internal_names:
                attributes[attr_name] = copy.copy(attr_value)
        return attributes

    def get_hyperedge_tuple(self, hyperedge_id):
        """From the hyperedge id, returns a tuple of the tail, head,
        positive regulator, and negative regulator sets of hypernodes.

        :returns: tuple -- tuple of four iterable containers,
                    representing the tail, head, positive
                    regulator, and negative regulator sets,
                    repsectively.
        :param hyperedge_tuple: ID of the hyperedge that has that the
                specified tail and head sets comprise.
        :raises: ValueError -- No such hyperedge exists.

        """
        if not self.has_hyperedge_id(hyperedge_id):
            raise ValueError("No such hyperedge exists.")

        attrs = self.get_hyperedge_attributes(hyperedge_id)
        tail = attrs["tail"]
        head = attrs["head"]
        pos_regs = attrs["pos_regs"]
        neg_regs = attrs["neg_regs"]

        return (tail, head, pos_regs, neg_regs)

    def get_hyperedge_tail(self, hyperedge_id):
        """Given a hyperedge ID, get a copy of that hyperedge's tail.

        :param hyperedge_id: ID of the hyperedge to retrieve the tail from.
        :returns: a copy of the container of hypernodes that the user provided
                as the tail to the hyperedge referenced as hyperedge_id.

        """
        return self.get_hyperedge_attribute(hyperedge_id, "tail")

    def get_hyperedge_head(self, hyperedge_id):
        """Given a hyperedge ID, get a copy of that hyperedge's head.

        :param hyperedge: ID of the hyperedge to retrieve the head from.
        :returns: a copy of the container of hypernodes that the user provided
            as the head to the hyperedge referenced as hyperedge_id.

        """
        return self.get_hyperedge_attribute(hyperedge_id, "head")

    def get_hyperedge_positive_regulators(self, hyperedge_id):
        """Given a hyperedge ID, get a copy of that hyperedge's
        positive regulators.

        :param hyperedge: ID of the hyperedge to retrieve the positive
                        regulators from.
        :returns: a copy of the container of hypernodes that the user provided
            as the positive regulators to the hyperedge referenced as
            hyperedge_id.

        """
        return self.get_hyperedge_attribute(hyperedge_id, "pos_regs")

    def get_hyperedge_negative_regulators(self, hyperedge_id):
        """Given a hyperedge ID, get a copy of that hyperedge's
        negative regulators.

        :param hyperedge: ID of the hyperedge to retrieve the negative
                        regulators from.
        :returns: a copy of the container of hypernodes that the user provided
            as the negative regulators to the hyperedge referenced as
            hyperedge_id.

        """
        return self.get_hyperedge_attribute(hyperedge_id, "neg_regs")

    def get_hyperedge_weight(self, hyperedge_id):
        """Given a hyperedge ID, get that hyperedge's weight.

        :param hyperedge: ID of the hyperedge to retrieve the weight from.
        :returns: a the weight of the hyperedge referenced as hyperedge_id.

        """
        return self.get_hyperedge_attribute(hyperedge_id, "weight")

    def remove_hypernode(self, hypernode):
        """Removes a hypernode and its attributes from the hypergraph. Removes
        every hyperedge that contains this hypernode in either the tail,
        head, positive regulator, or negative regulator sets.

        :param hypernode: reference to the hypernode being removed.
        :raises: ValueError -- No such hypernode exists.

        """
        # Ensure hypernode exists in the hypergraph
        if not self.has_hypernode(hypernode):
            raise ValueError("No such hypernode exists.")

        # Remove all hyperedges which contains this hypernode
        forward_star = self.get_forward_star(hypernode)
        backward_star = self.get_backward_star(hypernode)
        positive_regulator_star = self.get_positive_regulator_star(hypernode)
        negative_regulator_star = self.get_negative_regulator_star(hypernode)
        hyperedge_ids = forward_star.\
            union(backward_star).\
            union(positive_regulator_star).\
            union(negative_regulator_star)
        for hyperedge_id in hyperedge_ids:
            self.remove_hyperedge(hyperedge_id)

        # Remove hypernode's forward and backward star
        del self._forward_star[hypernode]
        del self._backward_star[hypernode]
        # Remove hypernode's positive and negative regulator star
        del self._positive_regulator_star[hypernode]
        del self._negative_regulator_star[hypernode]

        # Disassociate this hypernode from the nodes that compose it
        nodes = self._hypernode_attributes[hypernode][__composing_nodes]
        for node in nodes:
            _remove_hypernode_membership(node, hypernode)

        # Remove hypernode's attributes dictionary
        del self._hypernode_attributes[hypernode]

    def remove_node(self, node):
        """Removes a node and its attributes from the hypergraph. Removes
        every hypernode that contains this hypernode, and in turn removes
        every hyperedge that contains the removed hypernodes in either the
        tail, head, positive regulator, or negative regulator sets.

        :param node: reference to the node being removed.
        :raises: ValueError -- No such node exists.

        """
        # Ensure node exists in the hypergraph
        if not self.has_node(node):
            raise ValueError("No such node exists.")

        for hypernode in self._node_attributes["__in_hypernodes"]:
            self.remove_hypernode(hypernode)

        # Remove node's attributes dictionary
        del self._node_attributes[node]

    def get_forward_star(self, hypernode):
        """Given a hypernode, get a copy of that hypernode's forward star.

        :param hypernode: hypernode to retrieve the forward-star of.
        :returns: set -- set of hyperedge_ids for the hyperedges
                        in the hypernode's forward star.
        :raises: ValueError -- No such hypernode exists.

        """
        if hypernode not in self._hypernode_attributes:
            raise ValueError("No such hypernode exists.")
        return self._forward_star[hypernode].copy()

    def get_backward_star(self, hypernode):
        """Given a hypernode, get a copy of that hypernode's backward star.

        :param hypernode: hypernode to retrieve the backward-star of.
        :returns: set -- set of hyperedge_ids for the hyperedges
                in the hypernode's backward star.
        :raises: ValueError -- No such hypernode exists.

        """
        if hypernode not in self._hypernode_attributes:
            raise ValueError("No such hypernode exists.")
        return self._backward_star[hypernode].copy()

    def get_positive_regulator_star(self, hypernode):
        """Given a hypernode, get a copy of that hypernode's positive
        regulator-star.

        :param hypernode: hypernode to retrieve the positive regulator-star of.
        :returns: set -- set of hyperedge_ids for the hyperedges
                in the hypernode's positive regulator-star.
        :raises: ValueError -- No such hypernode exists.

        """
        if hypernode not in self._hypernode_attributes:
            raise ValueError("No such hypernode exists.")
        return self._positive_regulator_star[hypernode].copy()

    def get_negative_regulator_star(self, hypernode):
        """Given a hypernode, get a copy of that hypernode's negative
        regulator-star.

        :param hypernode: hypernode to retrieve the negative regulator-star of.
        :returns: set -- set of hyperedge_ids for the hyperedges
                in the hypernode's negative regulator-star.
        :raises: ValueError -- No such hypernode exists.

        """
        if hypernode not in self._hypernode_attributes:
            raise ValueError("No such hypernode exists.")
        return self._negative_regulator_star[hypernode].copy()

    def get_successors(self, tail):
        """Given a tail set of hypernodes, get a list of hyperedge IDs of
        which the hypernode set is the tail of each hyperedge.

        :param tail: set of hypernodes that correspond to the tails of some
                        (possibly empty) set of hyperedges.
        :returns: set -- hyperedge_ids of the hyperedges that have tail
                in the tail.

        """
        frozen_tail = frozenset(tail)
        # If this hypernode set isn't any tail in the hypergraph, then it has
        # no successors; thus, return an empty list
        if frozen_tail not in self._successors:
            return set()

        return set(self._successors[frozen_tail].values())

    def get_predecessors(self, head):
        """Given a head set of hypernodes, get a list of hyperedge IDs of
        which the hypernode set is the head of each hyperedge.

        :param head: set of hypernodes that correspond to the heads of some
                        (possibly empty) set of hyperedges.
        :returns: set -- hyperedge_ids of the hyperedges that have head
                in the head.

        """
        frozen_head = frozenset(head)
        # If this hypernode set isn't any head in the hypergraph, then it has
        # no predecessors; thus, return an empty list
        if frozen_head not in self._predecessors:
            return set()

        return set(self._predecessors[frozen_head].values())

    def get_positive_regulations(self, pos_regs):
        """Given a positive regulator set of hypernodes, get a list
        of hyperedge IDs of which the hypernode set positively
        regulates each hyperedge.

        :param pos_regs: set of hypernodes that correspond to the positive
                        regulators of some (possibly empty) set of hyperedges.
        :returns: set -- hyperedge_ids of the hyperedges that have pos_regs
                as the positive regulators.

        """
        frozen_pos_regs = frozenset(pos_regs)
        # If this hypernode set isn't any positive regulator set in the
        # hypergraph, then it has no positive regulations;
        # thus, return an empty list
        if frozen_pos_regs not in self._positive_regulations:
            return set()

        return set(self._positive_regulations[frozen_pos_regs].values())

    def get_negative_regulations(self, neg_regs):
        """Given a negative regulator set of hypernodes, get a list
        of hyperedge IDs of which the hypernode set negatively
        regulates each hyperedge.

        :param neg_regs: set of hypernodes that correspond to the negative
                        regulators of some (possibly empty) set of hyperedges.
        :returns: set -- hyperedge_ids of the hyperedges that have neg_regs
                as the negative regulators.

        """
        frozen_neg_regs = frozenset(neg_regs)
        # If this hypernode set isn't any negative regulator set in the
        # hypergraph, then it has no negative regulations;
        # thus, return an empty list
        if frozen_neg_regs not in self._negative_regulations:
            return set()

        return set(self._negative_regulations[frozen_neg_regs].values())

    def read(self, hyperedge_filename, node_mapping_filename,
             delim=',', sep='\t'):
        """Read a signaling hypergraph from a file, where nodes and
        hypernodes are represented as strings.
        Each column is separated by "sep", and the individual
        tail, head, positive regulator, and negative regulator hypernodes
        are delimited by "delim".
        The header line is currently ignored, but columns (in a single row)
        should be of the format:
        tailhypernode1[delim]..tailhypernodeM[sep]
        headhypernode1[delim]..headhypernodeM[sep]
        posreghypernode1[delim]..posreghypernodeM[sep]
        negreghypernode1[delim]..negreghypernodeM[sep]weight

        As a concrete example, an arbitrary line with delim=',' and
        sep='    ' (4 spaces) may look like:
        ::

            x1,x2    x3,x4,x5    x6    x7,x8    12

        which defines a hyperedge of weight 12 from a tail set containing
        hypernodes "x1" and "x2" to a head set containing hypernodes
        "x3", "x4", and "x5" with a positive regulator set containing
        hypernode "x6" and a negative regulator set containing hypernodes
        "x7" and "x8".

        """
        node_mapping_file = open(node_mapping_filename, 'r')
        node_mapping = {}

        # Skip the header line
        node_mapping_file.readline()

        line_number = 2
        for line in node_mapping_file.readlines():
            line = line.strip()
            # Skip empty lines
            if not line:
                continue

            words = line.split(sep)
            if len(words) != 2:
                raise \
                    IOError("Line {} ".format(line_number) +
                            "contains {} ".format(len(words)) +
                            "columns -- must contain only 2.")

            hypernode = words[0]
            composing_nodes = set(words[1].split(delim))
            node_mapping[hypernode] = composing_nodes

            line_number += 1

        hyperedge_file = open(hyperedge_filename, 'r')

        # Skip the header line
        hyperedge_file.readline()

        line_number = 2
        for line in hyperedge_file.readlines():
            line = line.strip()
            # Skip empty lines
            if not line:
                continue

            words = line.split(sep)
            if not (4 <= len(words) <= 5):
                raise \
                    IOError("Line {} ".format(line_number) +
                            "contains {} ".format(len(words)) +
                            "columns -- must contain only 4 or 5.")

            tail = set(words[0].split(delim))
            head = set(words[1].split(delim))
            pos_regs = set(words[2].split(delim))
            neg_regs = set(words[3].split(delim))
            if len(words) == 5:
                weight = float(words[4].split(delim)[0])
            else:
                weight = 1
            self.add_hyperedge(tail, head,
                               pos_regs, neg_regs,
                               node_mapping,
                               weight=weight)

            line_number += 1

        hyperedge_file.close()

    def write(self, hyperedge_filename, node_mapping_filename,
              delim=',', sep='\t'):
        """Write a signaling hypergraph from a file, where nodes and
        hypernodes are represented as strings.
        Each column is separated by "sep", and the individual
        tail, head, positive regulator, and negative regulator hypernodes
        are delimited by "delim".
        The header line is currently ignored, but columns (in a single row)
        should be of the format:
        tailhypernode1[delim]..tailhypernodeM[sep]
        headhypernode1[delim]..headhypernodeM[sep]
        posreghypernode1[delim]..posreghypernodeM[sep]
        negreghypernode1[delim]..negreghypernodeM[sep]weight

        As a concrete example, an arbitrary line with delim=',' and
        sep='    ' (4 spaces) may look like:
        ::

            x1,x2    x3,x4,x5    x6    x7,x8    12

        which defines a hyperedge of weight 12 from a tail set containing
        hypernodes "x1" and "x2" to a head set containing hypernodes
        "x3", "x4", and "x5" with a positive regulator set containing
        hypernode "x6" and a negative regulator set containing hypernodes
        "x7" and "x8".

        """
        # Write node mapping to file
        node_mapping_file = open(node_mapping_filename, 'w')

        # write first header line
        node_mapping_file.write("hypernode" + sep + "composing_nodes\n")

        for hypernode in self.get_hypernode_set():
            # Write hypernode into the first column followed by seperator
            line = "hypernode" + sep

            # Write the nodes into the second column, separated by delim
            for node in self.get_nodes_in_hypernode(hypernode):
                line += node + delim
            # Remove last (extra) delim and end the line
            line = line[:-1] + "\n"

            node_mapping_file.write(line)

        node_mapping_file.close()

        # Write hyperedge mapping to file
        hyperedge_file = open(hyperedge_filename, 'w')

        # write first header line
        node_mapping_file.write("tail" + sep + "head" + sep +
                                "pos_regs" + sep + "neg_regs" + sep +
                                "weight\n")

        for hyperedge_id in self.get_hyperedge_id_set():
            line = ""
            # Write each tail hypernode to the line, separated by delim
            for tail_hypernode in self.get_hyperedge_tail(hyperedge_id):
                line += tail_hypernode + delim
            # Remove last (extra) delim and add sep between columns
            line = line[:-1] + sep

            # Write each head hypernode to the line, separated by delim
            for head_hypernode in self.get_hyperedge_head(hyperedge_id):
                line += head_hypernode + delim
            # Remove last (extra) delim and add sep between columns
            line = line[:-1] + sep

            # Write each positive regulator to the line, separated by delim
            pos_regs = self.get_hyperedge_positive_regulators(hyperedge_id)
            for pos_reg in pos_regs:
                line += pos_reg + delim
            # Remove last (extra) delim and add sep between columns
            line = line[:-1] + sep

            # Write each negative regulator to the line, separated by delim
            neg_regs = self.get_hyperedge_negative_regulators(hyperedge_id)
            for neg_reg in neg_regs:
                line += neg_reg + delim
            # Remove last (extra) delim and add sep between columns
            line = line[:-1] + sep

            # Write the weight to the line and end the line
            line += sep + str(self.get_hyperedge_weight(hyperedge_id)) + "\n"

            hyperedge_file.write(line)

        hyperedge_file.close()
