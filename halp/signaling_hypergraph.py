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
    The tail and head cannot both be empty.

    A node is simply any hashable type. See "add_node" or "add_nodes" for
    more details.

    A hypernode is also any hashable type, which can be associated with a set
    of nodes. See "add_hypernode" or "add_hypernodes" for more details.

    A signaling hyperedge is a tuple of the tail hypernodes, the head
    hypernodes, the positive regulator hypernodes, and the negative regulator
    hypernodes.
    This class assigns (upon adding) and refers to each signaling hyperedge by
    an internal ID. See "add_hyperedge" or "add_hyperedges" for more details.

    Self-loops are allowed, and parallel (multi-) hyperedges are allowed if they
    have different regulator sets.

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

        # The backward star of a hypernode is the set of hyperedges such that the
        # hypernode is in the head of each hyperedge in that set.
        #
        # _backward_star: a dictionary mapping a hypernode to the set of hyperedges
        # that are in that hypernode's backward star.
        #
        # Provides O(1) time access to a reference to the set of incoming
        # hyperedges from a hypernode.
        #
        # Used in the implementation of methods such as add_hypernode and
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
        # ID "e"+_current_hyperedge_id+"$"+_sub_id, where _sub_id is a unique
        # integer identifier used to differentiate between several possible
        # "multihyperedges" that have different regulator sets.
        #
        # Since the class takes responsibility for giving hyperedges
        # their IDs (i.e. a unique identifier; could be alternatively viewed
        # as a unique name, label, etc.), the issued IDs need to be kept
        # track of. A consecutive issuing of integer IDs to the hyperedges is a
        # simple strategy to ensure their uniqueness and allow for
        # intuitive readability.
        #
        # e.g., _current_hyperedge_id = 4  implies that 4 hyperedges that have
        # unique tail/head set combinations have been added to the hypergraph,
        # and that "e4$..." was the most recently assigned hyperedge.
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

	def has_hypernode(self, hypernode):
        """Determines if a specific hypernode is present in the hypergraph.

        :param node: reference to hypernode whose presence is being checked.
        :returns: bool -- true iff the node exists in the hypergraph.

        """
        return hypernode in self._hypernode_attributes

    def map_hypernode_to_nodes(self, hypernode, nodes):
    	"""Informs the library of the hypernode<-->nodes mapping.

    	:param hypernode: the hypernode to map to a group of nodes
    	:param nodes: the group of nodes to map to the hypernode

    	"""
    	pass

    def _add_hypernode_membership(self, node, hypernode):
		"""Adds the given hypernode into the node's "membership" structure,
		indicating that this node is a member of the given hypernode.

        :param node: reference to the node whose hypernode membership is
        			being modified.
		:param hypernode: reference to the hypernode that the given node is
						a member of.
        :raises: ValueError -- No such node exists.
        :raises: ValueError -- No such hypernode exists.

        """
        if not self.has_node(node):
            raise ValueError("No such node exists.")
        if not self.has_hypernode(hypernode)
            raise ValueError("No such hypernode exists.")

        self._node_attributes[node]["__in_hypernodes"].add(hypernode)

    def _remove_hypernode_membership(self, node, hypernode):
		"""Removes the given hypernode into the node's "membership" structure,
		indicating that this node is no longer a member of the given hypernode.

        :param node: reference to the node whose hypernode membership is
        			being modified.
		:param hypernode: reference to the hypernode that the given node is
						no longer a member of.
        :raises: ValueError -- No such node exists.
        :raises: ValueError -- No such hypernode exists.

        """
        if not self.has_node(node):
            raise ValueError("No such node exists.")
        if not self.has_hypernode(hypernode)
            raise ValueError("No such hypernode exists.")

        self._node_attributes[node]["__in_hypernodes"].remove(hypernode)

    def add_hypernode(self, hypernode, composing_nodes=set(), attr_dict=None, **attr):
        """Adds a hypernode to the graph, along with any related attributes
           of the hypernode.

        :param hypernode: reference to the hypernode being added.
        :param nodes: reference to the set of nodes that compose
        			the hypernode.
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
        	attr_dict["__composing_nodes"] = composing_nodes
        	added_nodes = composing_nodes
        	removed_nodes = set()
            self._hypernode_attributes[hypernode] = attr_dict
        # Otherwise, just update the hypernode's attributes
        else:
            self._hypernode_attributes[hypernode].update(attr_dict)
            added_nodes = composing_nodes - self._hypernode_attributes\
            			  [hypernode]["__composing_nodes"]
			removed_nodes = self._hypernode_attributes\
            			  	[hypernode]["__composing_nodes"] - composing_nodes
        
        # For every "composing node" added to this hypernode, update
        # those nodes attributes to be members of this hypernode
		for node in added_nodes:
			_add_hypernode_membership(node, hypernode)
		# For every "composing node" added to this hypernode, update
        # those nodes attributes to no longer be members of this hypernode
        for node in remove_nodes:
			_remove_hypernode_membership(node, hypernode)

    def get_hypernode_set(self):
        """Returns the set of hypernodes that are currently in the hypergraph.

        :returns: set -- all hypernodes currently in the hypergraph

        """
        return set(self._hypernode_attributes.keys())

    def hypernode_iterator(self):
        """Provides an iterator over the hypernodes.

        """
        return iter(self._hypernode_attributes)

    def _assign_next_hyperedge_id(self):
        """Returns the next [consecutive] ID to be assigned
            to a hyperedge.
        :returns: str -- hyperedge ID to be assigned.

        """
        self._current_hyperedge_id += 1
        return "e" + str(self._current_hyperedge_id)

    def add_hyperedge(self, tail, head,
    				  pos_regs=set(), neg_regs=set(),
    				  attr_dict=None, **attr):
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

        # Don't allow both empty tail and head containers (invalid hyperedge)
        if not tail and not head:
            raise ValueError("tail and head arguments \
                             cannot both be empty.")

        # Use frozensets for tail and head sets to allow for hashable keys
        frozen_tail = frozenset(tail)
        frozen_head = frozenset(head)
        frozen_pos_regs = frozenset(pos_regs)
        frozen_neg_regs = frozenset(neg_regs)

        # Initialize a successor dictionary for the tail and head, respectively
        if frozen_tail not in self._successors:
            self._successors[frozen_tail] = {}
        if frozen_head not in self._predecessors:
            self._predecessors[frozen_head] = {}

        is_new_diedge = not self.has_hyperedge(frozen_tail, frozen_head)
        if is_new_diedge:
            # Add tail and head nodes to graph (if not already present)
            self.add_hypernodes(frozen_head)
            self.add_hypernodes(frozen_tail)

            # Create new hyperedge name to use as reference for that hyperedge
            hyperedge_id = self._assign_next_hyperedge_id()

            # Add hyperedge to the forward-star and to the backward-star
            # for each hypernode in the tail and head sets, respectively
            for hypernode in frozen_tail:
                self._forward_star[hypernode].add(hyperedge_id)
            for hypernode in frozen_head:
                self._backward_star[hypernode].add(hyperedge_id)

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
                 "_signaling_id": 1
                 "weight": 1}
        else:
            # If its not a new hyperedge, just get its ID to update attributes
            hyperedge_id = self._successors[frozen_tail][frozen_head]

        # Set attributes and return hyperedge ID
        self._hyperedge_attributes[hyperedge_id].update(attr_dict)
        return hyperedge_id
