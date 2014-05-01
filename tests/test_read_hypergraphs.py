from __future__ import absolute_import

from hypergraph.directedHyperGraph import DirectedHyperGraph
from hypergraph.undirectedHyperGraph import UndirectedHyperGraph 

def test_read_directedgraph():
    '''
        Test reading directed hypergraphs from files,
        and add edges with and without weights.
    '''
    # read directed hypergraph
    directedHyperGraph = DirectedHyperGraph(set(), set())
    directedHyperGraph.read('tests/data/dirhypergraph.txt')

    assert len(directedHyperGraph.nodes) == 5
    assert len(directedHyperGraph.hyperedges) == 4   
    
    # modify graph
    directedHyperGraph.add_hyperedge({'x10', 'x6'}, {'x7'}, 3.1)
    directedHyperGraph.add_hyperedge({'x2'}, {'x7', 'x9'})

    assert len(directedHyperGraph.nodes) == 9
    assert len(directedHyperGraph.hyperedges) == 6   
   
    # print Graph for testing
    print("This is directed HyperGraph:")
    directedHyperGraph.printGraph()
   
    
def test_read_undirectedgraph():
    '''
        Test reading undirected hypergraphs from files,
        and add edges with and without weights.
    '''    
    # read Undirected hypergraph
    undirectedHyperGraph = UndirectedHyperGraph(set(), set())
    undirectedHyperGraph.read('tests/data/UnDirhypergraph.txt')

    assert len(undirectedHyperGraph.nodes) == 6
    assert len(undirectedHyperGraph.hyperedges) == 5   
    # modify graph
    undirectedHyperGraph.add_hyperedge({'v2', 'v6', 'v7'}, 2)
    undirectedHyperGraph.add_hyperedge({'v7', 'v9'})
    
    assert len(undirectedHyperGraph.nodes) == 8
    assert len(undirectedHyperGraph.hyperedges) == 7   

    # print Graph for testing
    print("\nThis is Undirected HyperGraph:")
    undirectedHyperGraph.printGraph()

