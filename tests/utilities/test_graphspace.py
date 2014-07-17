from hypergraph.directed_hypergraph import DirectedHypergraph
from hypergraph.utilities import graphspace


def test_graphspace():
    H = DirectedHypergraph()
    H.read("tests/data/basic_directed_hypergraph.txt")

    graphspace.post_to_graphspace(H,
                                  'basic_directed_hypergraph',
                                  'annaritz@vt.edu',
                                  'platypus')
