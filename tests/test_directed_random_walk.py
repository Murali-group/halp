from __future__ import absolute_import

from hypergraph.directedHyperGraph import DirectedHyperGraph
import numpy as np

def test_directed_random_walk():
    '''
        Test reading directed hypergraphs from files,
        and add edges with and without weights.
    '''
    # read directed hypergraph
    directedHyperGraph = DirectedHyperGraph(set(), set())
    directedHyperGraph.read('tests/data/dirhypergraph.txt')

    assert len(directedHyperGraph.nodes) == 5
    assert len(directedHyperGraph.hyperedges) == 4

    '''
    Test the incidence matrix 
    '''
    directedHyperGraph.build_incidence_matrix()
    head= np.matrix('0 0 0 0; 1 0 0 0; 1 0 0 0; 0 1 0 0; 0 0 1 1')
    tail = np.matrix('1 0 1 0; 0 1 0 0; 0 0 1 0; 0 0 0 1; 0 0 0 0')     
    assert np.shape(directedHyperGraph.H_minus)==(5, 4)
    assert np.shape(directedHyperGraph.H_plus)==(5, 4)

    P = directedHyperGraph.build_transition_matrix()
    print(P)
