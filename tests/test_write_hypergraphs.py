from __future__ import absolute_import

from hypergraph.directedHyperGraph import DirectedHyperGraph
from hypergraph.undirectedHyperGraph import UndirectedHyperGraph


def test_write_directedgraph():
    '''
        Test writing directed hypergraph to file.
    '''
    # read directed hypergraph
    directedHyperGraph = DirectedHyperGraph(set(), set())
    directedHyperGraph.read('tests/data/dirhypergraph.txt')
    assert len(directedHyperGraph.nodes) == 5
    assert len(directedHyperGraph.hyperedges) == 4

    # write the graph and read it again
    directedHyperGraph.write('tests/data/dirhypergraph2.txt')
    directedHyperGraph = DirectedHyperGraph(set(), set())
    directedHyperGraph.read('tests/data/dirhypergraph2.txt')

    assert len(directedHyperGraph.nodes) == 5
    assert len(directedHyperGraph.hyperedges) == 4


def test_write_undirectedgraph():
    '''
        Test writing undirected hypergraph to files.
    '''
    # read Undirected hypergraph
    undirectedHyperGraph = UndirectedHyperGraph(set(), set())
    undirectedHyperGraph.read('tests/data/UnDirhypergraph.txt')
    assert len(undirectedHyperGraph.nodes) == 6
    assert len(undirectedHyperGraph.hyperedges) == 5

    # write the graph and read it again
    undirectedHyperGraph.write('tests/data/UnDirhypergraph2.txt')
    undirectedHyperGraph = UndirectedHyperGraph(set(), set())
    undirectedHyperGraph.read('tests/data/UnDirhypergraph2.txt')

    assert len(undirectedHyperGraph.nodes) == 6
    assert len(undirectedHyperGraph.hyperedges) == 5