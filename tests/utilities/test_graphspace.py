import sys

from hypergraph.directed_hypergraph import DirectedHypergraph
from hypergraph.utilities import graphspace


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
