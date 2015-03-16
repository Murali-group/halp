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

        # _hyperedge_attributes: a 2-dimensional dictionary mapping a
        # hyperedge ID (initially created by the call to add_hyperedge
        # or add_hyperedges) (first) as (tail, head) tuple identifier to
        # a dictionary of all signaling hyperedges that share this tuple,
        # and (second) to the attributes of that specific signaling hyperedge.
        #
        # Given a hyperedge ID in the form hyperedge_id="x$y",
        # _hyperedge_attributes[x][y] stores:
        # the tail of the hyperedge as specified by the user (as "tail"),
        # the head of the hyperedge as specified by the user (as "head"),
        # the positive regulators as specified by the user (as "pos_regs"),
        # the negative regulators as specified by the user (as "neg_regs"),
        # and the weight of the hyperedge (as "weight").
        # Here, x refers to the hyperedge identified by the (tail,head) tuple,
        # and y refers to the specific signaling hyperedge identified by the
        # (tail, head, pos_regs, neg_regs) tuple.
        # For internal purposes, it also stores the frozenset versions of
        # the tail, head, and regulators (as "__frozen_tail", "__frozen_head",
        # "__pos_regs", "__neg_regs").
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
