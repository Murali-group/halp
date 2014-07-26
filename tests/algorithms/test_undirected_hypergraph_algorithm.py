from os import remove
import numpy as np
from scipy import sparse

from hypergraph.undirected_hypergraph import UndirectedHypergraph
from hypergraph.algorithms import undirected_hypergraph_algorithm as UHA


def test_init():
    UH = UndirectedHypergraph()
    UH.read('./tests/data/Undirectedhypergraph.txt')
    W = UHA.getDiagonalWeightMatrix(UH)
    H = UHA.getIncidenceMatrix(UH)
    nl = UHA.normalizedLaplacian(UH)
    partition = UHA.minCut(UH, 0)
    assert len(partition) == 2
