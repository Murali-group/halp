from __future__ import absolute_import

from hypergraph.undirectedHyperGraph import UndirectedHyperGraph
import numpy as np

def test_incidence_matrix():
    '''
        Test reading undirected hypergraphs from files,
        and add edges with and without weights.
    '''
    # read Undirected hypergraph
    undirectedHyperGraph = UndirectedHyperGraph(set(), set())
    undirectedHyperGraph.read('tests/data/UnDirhypergraph.txt')

    assert len(undirectedHyperGraph.nodes) == 6
    assert len(undirectedHyperGraph.hyperedges) == 5

    undirectedHyperGraph.getIncidenceMatrix()
    incidenceMatrix = undirectedHyperGraph.H
    assert len(incidenceMatrix) == 6
    assert len(incidenceMatrix[0]) == 5
    #print(incidenceMatrix)
    d_v = undirectedHyperGraph.getDiagonalNodeMatrix()
    assert d_v.shape == (6,6)
    #print(d_v)
    w = undirectedHyperGraph.getDiagonalWeightMatrix()
    assert w.shape == (5,5)
    #print(w)
    d_e = undirectedHyperGraph.getDiagonalEdgeMatrix()
    #print(d_e)	
    P = undirectedHyperGraph.randomWalkMatrix()
    probs = [round(elem, 2) for elem in np.sum(P,axis = 1)]
    '''
    assert to see if all the rows sum up to 1
    '''
    assert len(set(probs)) == 1
    pi_star = undirectedHyperGraph.stationaryDistribution(P)
    assert round(np.sum(pi_star),2) == 1
    laplacian = undirectedHyperGraph.normalizedLaplacian()
    minCut = undirectedHyperGraph.minCut(0)
        
    # print Graph for testing
    print("\nThis is Undirected HyperGraph:")
    undirectedHyperGraph.printGraph()

if __name__ == "__main__":
    test_incidence_matrix()
