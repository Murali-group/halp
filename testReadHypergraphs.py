from hypergraph import *
from hyperedge import HyperEdge
from node import Node

def main():
    # read directed hypergraph
    directedHyperGraph = DirectedHyperGraph()
    directedHyperGraph.readDirectedGraph('./data/dirhypergraph.txt')
    # print Graph for testing
    print("This is directed HyperGraph:")
    directedHyperGraph.printGraph()
    
    # read Undirected hypergraph
    undirectedHyperGraph = UndirectedHyperGraph()
    undirectedHyperGraph.readUnDirectedGraph('./data/unDirhypergraph.txt')
    # print Graph for testing
    print("\nThis is Undirected HyperGraph:")
    undirectedHyperGraph.printGraph()


if __name__ == "__main__": main()
