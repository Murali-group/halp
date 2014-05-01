from __future__ import absolute_import

from hypergraph.directedHyperGraph import DirectedHyperGraph
from hypergraph.undirectedHyperGraph import UndirectedHyperGraph 

def test_write_directedgraph():
    '''
        Test reading directed and undirected hypergraphs from files,
        and add edges with and without weights.
    '''
    # read directed hypergraph
    directedHyperGraph = DirectedHyperGraph(set(), set())
    directedHyperGraph.readDirectedGraph('tests/data/dirhypergraph.txt')

    assert len(directedHyperGraph.nodes) == 5
    assert len(directedHyperGraph.hyperedges) == 4   
    

    
def test_write_undirectedgraph():
    '''
        Test reading directed and undirected hypergraphs from files,
        and add edges with and without weights.
    '''
    # read Undirected hypergraph
    undirectedHyperGraph = UndirectedHyperGraph(set(), set())
    undirectedHyperGraph.readUnDirectedGraph('tests/data/UnDirhypergraph.txt')

    assert len(undirectedHyperGraph.nodes) == 6
    assert len(undirectedHyperGraph.hyperedges) == 5      
   

