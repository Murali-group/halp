from os import remove
import numpy as np
from scipy import sparse

from hypergraph.undirected_hypergraph import UndirectedHypergraph
from hypergraph.algorithms.undirected_hypergraph_algorithm import UndirectedHypergraphAlgorithm

def test_init():
    H = UndirectedHypergraph()
    H.read('./tests/data/Undirectedhypergraph.txt')
    UHA = UndirectedHypergraphAlgorithm(H)
    #W = UHA.getDiagonalWeightMatrix()
    #H = UHA.incidenceMatrix
    #print(UHA.getDiagonalNodeMatrix(W,H).todense())
    
    #print(UHA.getDiagonalEdgeMatrix().todense())
    #print(UHA.randomWalkMatrix().todense())
    #I = [0,1,1,1,1,2,2,3,4,4,4,5,5,6,7,7,8,9]
    #J = [6,1,2,3,4,2,7,3,1,5,7,3,6,9,1,7,8,0]
    #V = [1,0.3,0.3,0.1,0.3,0.6,0.4,1,0.4,0.3,0.3,0.9,0.1,1,0.8,0.2,1,1]
    #I = [0,0,0,1,1,1,2,2,2]
    #J = [0,1,2,0,1,2,0,1,2]
    #V = [0.33,0.33,0.34,0.25,0.5,0.25,0.17,0.33,0.5]
    #P = [[0.33,0.33,0.34],[0.25,0.5,0.25],[0.17,0.33,0.5]]
    #P = sparse.csc_matrix((V,(I,J)),shape=(3,3))
    #P = UHA.randomWalkMatrix()
    #SD = UHA.stationaryDistribution(P)
    nl = UHA.normalizedLaplacian()
    nodeNumber = UHA.getNodeNumber()
    #from math import ceil
    #numberOfEigenValues = ceil((nodeNumber*30.0)/100)
    #numberOfEigenValues = nodeNumber - 2
    partition = UHA.minCut(0)
    print(partition)
    assert len(partition) == 2