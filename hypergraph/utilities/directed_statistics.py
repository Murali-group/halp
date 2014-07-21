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


def max_outdegree(hypergraph):
    """Returns the hypergraph's largest outdegree.

    :param hypergraph: the hypergraph whose max outdegree is to be determined.
    :returns: int -- the max outdegree in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_outdegree(hypergraph, max)


def min_outdegree(hypergraph):
    """Returns the hypergraph's smallest outdegree.

    :param hypergraph: the hypergraph whose min outdegree is to be determined.
    :returns: int -- the min outdegree in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_outdegree(hypergraph, min)


def average_outdegree(hypergraph):
    """Returns the hypergraph's average outdegree.

    :param hypergraph: the hypergraph whose average outdegree is to be
                    determined.
    :returns: float -- the average outdegree in the hypergraph.
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


def max_indegree(hypergraph):
    """Returns the hypergraph's largest indegree.

    :param hypergraph: the hypergraph whose max indegree is to be determined.
    :returns: int -- the max indegree in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_indegree(hypergraph, max)


def min_indegree(hypergraph):
    """Returns the hypergraph's smallest indegree.

    :param hypergraph: the hypergraph whose min indegree is to be determined.
    :returns: int -- the min indegree in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_indegree(hypergraph, min)


def average_indegree(hypergraph):
    """Returns the hypergraph's average indegree.

    :param hypergraph: the hypergraph whose average indegree is to be
                    determined.
    :returns: float -- the average indegree in the hypergraph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_indegree(hypergraph, np.mean)


def _F_tail_cardinality(hypergraph, F):
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


def max_tail_cardinality(hypergraph):
    """Returns the hypergraph's largest hyperedge tail cardinality.

    :param hypergraph: the hypergraph whose max hyperedge tail cardinality
                is to be determined.
    :returns: int -- the max hyperedge tail cardinality in the graph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_tail_cardinality(hypergraph, max)


def min_tail_cardinality(hypergraph):
    """Returns the hypergraph's largest hyperedge tail cardinality.

    :param hypergraph: the hypergraph whose min hyperedge tail cardinality
                is to be determined.
    :returns: int -- the min hyperedge tail cardinality in the graph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_tail_cardinality(hypergraph, min)


def average_tail_cardinality(hypergraph):
    """Returns the hypergraph's largest hyperedge tail cardinality.

    :param hypergraph: the hypergraph whose np.mean hyperedge tail cardinality
                is to be determined.
    :returns: float -- the np.mean hyperedge tail cardinality in the graph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_tail_cardinality(hypergraph, np.mean)


def _F_head_cardinality(hypergraph, F):
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


def max_head_cardinality(hypergraph):
    """Returns the hypergraph's largest hyperedge head cardinality.

    :param hypergraph: the hypergraph whose max hyperedge head cardinality
                is to be determined.
    :returns: int -- the max hyperedge head cardinality in the graph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_head_cardinality(hypergraph, max)


def min_head_cardinality(hypergraph):
    """Returns the hypergraph's largest hyperedge head cardinality.

    :param hypergraph: the hypergraph whose min hyperedge head cardinality
                is to be determined.
    :returns: int -- the min hyperedge head cardinality in the graph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_head_cardinality(hypergraph, min)


def average_head_cardinality(hypergraph):
    """Returns the hypergraph's largest hyperedge head cardinality.

    :param hypergraph: the hypergraph whose np.mean hyperedge head cardinality
                is to be determined.
    :returns: float -- the np.mean hyperedge head cardinality in the graph.
    :raises: TypeError -- Algorithm only applicable to directed hypergraphs

    """
    return _F_head_cardinality(hypergraph, np.mean)
