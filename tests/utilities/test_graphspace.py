import sys

from halp.directed_hypergraph import DirectedHypergraph
from halp.utilities import graphspace


def test_graphspace():
    # Current version of GraphSpace won't work with Python3, so don't even try
    if sys.version_info >= (3, 0):
        return

    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    graphspace.post_to_graphspace(H,
                                  'basic_directed_hypergraph',
                                  'annaritz@vt.edu',
                                  'platypus')

    # Post to group
    graphspace.post_to_graphspace(H,
                                  'basic_directed_hypergraph',
                                  'annaritz@vt.edu',
                                  'platypus',
                                  'hypergraph_test_group')

    # Try posting invalid directed hypergraph
    try:
        graphspace.post_to_graphspace("invalid_graph",
                                      'basic_directed_hypergraph',
                              		  'annaritz@vt.edu',
                              		  'platypus')
        assert False
    except TypeError:
        pass
    except BaseException as e:
        assert False, e
