"""
.. module:: directed_statistics
   :synopsis: Defines several functions for generating statistics of
            the hypergraph and its properties.

"""
import numpy as np

from hypergraph.directed_hypergraph import DirectedHypergraph


def number_of_nodes(hypergraph):
    """Returns the number of nodes in the given hypergraph.

    :param hypergraph: the hypergraph whose nodes are to be counted.
    :returns: int -- number of nodes in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    if not isinstance(hypergraph, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    return len(hypergraph.get_node_set())


def number_of_hyperedges(hypergraph):
    """Returns the number of hyperedges in the given hypergraph.

    :param hypergraph: the hypergraph whose hyperedges are to be counted.
    :returns: int -- number of hyperedges in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    if not isinstance(hypergraph, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    return len(hypergraph.get_hyperedge_id_set())


def _F_outdegree(hypergraph, F):
    """Returns the result of a function F applied to the set of outdegrees in
    in the hypergraph.

    :param hypergraph: the hypergraph whose outdegrees will be operated on.
    :param F: function to execute on the list of outdegrees in the hypergraph.
    :returns: result of the given function F.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    if not isinstance(hypergraph, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    return F([len(hypergraph.get_forward_star(node))
             for node in hypergraph.get_node_set()])


def outdegree_list(hypergraph):
    """Returns a list of the hypergraph's nodes' outdegrees.
    Use this to manually perform statistics on the hypergraph's nodes'
    outdegrees or to avoid the performance cost of calling several
    built-in statistics functions.

    :param hypergraph: the hypergraph whose outdegrees are to be returned.
    :returns: list -- outdegrees for each node in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_outdegree(hypergraph, list)


def min_outdegree(hypergraph):
    """Returns the hypergraph's smallest outdegree.

    :param hypergraph: the hypergraph whose min outdegree is to be determined.
    :returns: int -- the min outdegree in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_outdegree(hypergraph, min)


def max_outdegree(hypergraph):
    """Returns the hypergraph's largest outdegree.

    :param hypergraph: the hypergraph whose max outdegree is to be determined.
    :returns: int -- the max outdegree in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_outdegree(hypergraph, max)


def mean_outdegree(hypergraph):
    """Returns the hypergraph's mean outdegree.

    :param hypergraph: the hypergraph whose mean outdegree is to be
                    determined.
    :returns: float -- the mean outdegree in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_outdegree(hypergraph, np.mean)


def _F_indegree(hypergraph, F):
    """Returns the result of a function F applied to the list of indegrees in
    in the hypergraph.

    :param hypergraph: the hypergraph whose indegrees will be operated on.
    :param F: function to execute on the list of indegrees in the hypergraph.
    :returns: result of the given function F.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    if not isinstance(hypergraph, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    return F([len(hypergraph.get_backward_star(node))
             for node in hypergraph.get_node_set()])


def indegree_list(hypergraph):
    """Returns a list of the hypergraph's nodes' indegrees.
    Use this to manually perform statistics on the hypergraph's nodes'
    indegrees or to avoid the performance cost of calling several
    built-in statistics functions.

    :param hypergraph: the hypergraph whose indegrees are to be returned.
    :returns: list -- indegrees for each node in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_indegree(hypergraph, list)


def min_indegree(hypergraph):
    """Returns the hypergraph's smallest indegree.

    :param hypergraph: the hypergraph whose min indegree is to be determined.
    :returns: int -- the min indegree in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_indegree(hypergraph, min)


def max_indegree(hypergraph):
    """Returns the hypergraph's largest indegree.

    :param hypergraph: the hypergraph whose max indegree is to be determined.
    :returns: int -- the max indegree in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_indegree(hypergraph, max)


def mean_indegree(hypergraph):
    """Returns the hypergraph's mean indegree.

    :param hypergraph: the hypergraph whose mean indegree is to be
                    determined.
    :returns: float -- the mean indegree in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_indegree(hypergraph, np.mean)


def _F_hyperedge_tail_cardinality(hypergraph, F):
    """Returns the result of a function F applied to the set of cardinalities
    of hyperedge tails in the hypergraph.

    :param hypergraph: the hypergraph whose tail cardinalities will be
                    operated on.
    :param F: function to execute on the set of cardinalities in the
            hypergraph.
    :returns: result of the given function F.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    if not isinstance(hypergraph, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    return F([len(hypergraph.get_hyperedge_tail(hyperedge_id))
             for hyperedge_id in hypergraph.get_hyperedge_id_set()])


def hyperedge_tail_cardinality_list(hypergraph):
    """Returns a list of the hypergraph's hyperedges' tail cardinalities.
    Use this to manually perform statistics on the hypergraph's
    hyperedges' tail cardinalities or to avoid the performance cost of calling
    several built-in statistics functions.

    :param hypergraph: the hypergraph whose tail cardinalities are to
                    be returned.
    :returns: list -- tail cardinalities for each hyperedge in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_hyperedge_tail_cardinality(hypergraph, list)


def min_hyperedge_tail_cardinality(hypergraph):
    """Returns the hypergraph's smallest hyperedge tail cardinality.

    :param hypergraph: the hypergraph whose min hyperedge tail cardinality
                is to be determined.
    :returns: int -- the min hyperedge tail cardinality in the graph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_hyperedge_tail_cardinality(hypergraph, min)


def max_hyperedge_tail_cardinality(hypergraph):
    """Returns the hypergraph's largest hyperedge tail cardinality.

    :param hypergraph: the hypergraph whose max hyperedge tail cardinality
                is to be determined.
    :returns: int -- the max hyperedge tail cardinality in the graph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_hyperedge_tail_cardinality(hypergraph, max)


def mean_hyperedge_tail_cardinality(hypergraph):
    """Returns the hypergraph's mean hyperedge tail cardinality.

    :param hypergraph: the hypergraph whose np.mean hyperedge tail cardinality
                is to be determined.
    :returns: float -- the np.mean hyperedge tail cardinality in the graph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_hyperedge_tail_cardinality(hypergraph, np.mean)


def _F_hyperedge_head_cardinality(hypergraph, F):
    """Returns the result of a function F applied to the set of cardinalities
    of hyperedge heads in the hypergraph.

    :param hypergraph: the hypergraph whose head cardinalities will be
                    operated on.
    :param F: function to execute on the set of cardinalities in the
            hypergraph.
    :returns: result of the given function F.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    if not isinstance(hypergraph, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    return F([len(hypergraph.get_hyperedge_head(hyperedge_id))
             for hyperedge_id in hypergraph.get_hyperedge_id_set()])


def hyperedge_head_cardinality_list(hypergraph):
    """Returns a list of the hypergraph's hyperedges' head cardinalities.
    Use this to manually perform statistics on the hypergraph's
    hyperedges' head cardinalities or to avoid the performance cost of calling
    several built-in statistics functions.

    :param hypergraph: the hypergraph whose head cardinalities are to
                    be returned.
    :returns: list -- head cardinalities for each hyperedge in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_hyperedge_head_cardinality(hypergraph, list)


def max_hyperedge_head_cardinality(hypergraph):

    """Returns the hypergraph's largest hyperedge head cardinality.

    :param hypergraph: the hypergraph whose max hyperedge head cardinality
                is to be determined.
    :returns: int -- the max hyperedge head cardinality in the graph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_hyperedge_head_cardinality(hypergraph, max)


def min_hyperedge_head_cardinality(hypergraph):
    """Returns the hypergraph's smallest hyperedge head cardinality.

    :param hypergraph: the hypergraph whose min hyperedge head cardinality
                is to be determined.
    :returns: int -- the min hyperedge head cardinality in the graph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_hyperedge_head_cardinality(hypergraph, min)


def mean_hyperedge_head_cardinality(hypergraph):
    """Returns the hypergraph's mean hyperedge head cardinality.

    :param hypergraph: the hypergraph whose np.mean hyperedge head cardinality
                is to be determined.
    :returns: float -- the np.mean hyperedge head cardinality in the graph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_hyperedge_head_cardinality(hypergraph, np.mean)


def _F_hyperedge_cardinality_ratio(hypergraph, F):
    """Returns the result of a function F applied to the set of cardinality
    ratios between the tail and the head sets (specifically, |tail|/|head|) of
    hyperedges in the hypergraph.

    :param hypergraph: the hypergraph whose cardinality ratios will be
                    operated on.
    :param F: function to execute on the set of cardinality ratios in the
            hypergraph.
    :returns: result of the given function F.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    if not isinstance(hypergraph, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    # Since |head| can potentially be 0 (causing a division by 0 exception),
    # we use numpy's float64 to have division by 0 result in inf, which is
    # then cast back to a float for our final result
    return F([float(len(hypergraph.get_hyperedge_tail(hyperedge_id)) /
              np.float64(len(hypergraph.get_hyperedge_head(hyperedge_id))))
             for hyperedge_id in hypergraph.get_hyperedge_id_set()])


def hyperedge_cardinality_ratio_list(hypergraph):
    """Returns a list of the hypergraph's hyperedges' cardinality ratios.
    Use this to manually perform statistics on the hypergraph's
    hyperedges' cardinality ratios or to avoid the performance cost of calling
    several built-in statistics functions.

    :param hypergraph: the hypergraph whose cardinality ratios are to
                    be returned.
    :returns: list -- cardinality ratios for each hyperedge in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_hyperedge_cardinality_ratio(hypergraph, list)


def min_hyperedge_cardinality_ratio(hypergraph):
    """Returns the hypergraph's smallest hyperedge cardinality ratio.

    :param hypergraph: the hypergraph whose min hyperedge cardinality ratio
                is to be determined.
    :returns: int -- the min hyperedge cardinality ratio in the graph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_hyperedge_cardinality_ratio(hypergraph, min)


def max_hyperedge_cardinality_ratio(hypergraph):
    """Returns the hypergraph's largest hyperedge cardinality ratio.

    :param hypergraph: the hypergraph whose max hyperedge cardinality ratio
                is to be determined.
    :returns: int -- the max hyperedge cardinality ratio in the graph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_hyperedge_cardinality_ratio(hypergraph, max)


def mean_hyperedge_cardinality_ratio(hypergraph):
    """Returns the hypergraph's mean hyperedge cardinality ratio.

    :param hypergraph: the hypergraph whose mean hyperedge cardinality ratio
                is to be determined.
    :returns: int -- the mean hyperedge cardinality ratio in the graph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_hyperedge_cardinality_ratio(hypergraph, np.mean)
