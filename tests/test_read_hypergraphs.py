from hypergraph.hypergraph import DirectedHyperGraph, UndirectedHyperGraph


def test_example():
    assert 1 == 1


def test_read():
    '''
        Test reading directed and undirected hypergraphs from files,
        and add edges with and without weights.
    '''
    # read directed hypergraph
    directedHyperGraph = DirectedHyperGraph()
    directedHyperGraph.readDirectedGraph('tests/data/dirhypergraph.txt')

    # modify graph
    directedHyperGraph.add_hyperedge({'x2', 'x6'}, {'v7'}, 3.1)
    directedHyperGraph.add_hyperedge({'x2'}, {'x7', 'x8'})

    # print Graph for testing
    print("This is directed HyperGraph:")
    directedHyperGraph.printGraph()

    # read Undirected hypergraph
    undirectedHyperGraph = UndirectedHyperGraph()
    undirectedHyperGraph.readUnDirectedGraph('tests/data/UnDirhypergraph.txt')

    # modify graph
    undirectedHyperGraph.add_hyperedge({'v2', 'v6', 'v7'}, 2)
    undirectedHyperGraph.add_hyperedge({'v7', 'v8'})

    # print Graph for testing
    print("\nThis is Undirected HyperGraph:")
    undirectedHyperGraph.printGraph()
