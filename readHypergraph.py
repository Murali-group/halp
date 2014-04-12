from hypergraph import HyperGraph
from hyperedge import HyperEdge
from node import Node
from collections import Set

def main():
    directedHyperGraph = readDirectedGraph('data/dirhypergraph.txt')
    # print Graph for testing
    directedHyperGraph.printGraph()
    

def readDirectedGraph(fileName, sep='\t', delim=','):
    '''
        Read a directed hypergraph from file FileName
        each row is a hyperEdge.
        Tails and heads are separated by "sep"
        nodes within a hypernode are separated by "delim"
    '''
    fin = open(fileName, 'r')

    # read first header line
    fin.readline()
    graph = HyperGraph()
    i = 1
    for line in fin.readlines():
        line = line.strip('\n')
        if line=="": continue   # skip empty lines
        words = line.split(sep)
        if len(words) != 2:
            raise Exception('File format error at line {}'.format(i))
        i+=1
        tail = words[0].split(delim)
        head = words[1].split(delim)
       
        # Create hypergraph from current line
        hyperedge = HyperEdge(set(),set())
       
        # Read Tail nodes
        for t in tail:
            node=graph.get_node_by_name(t)
            if (node==None):
                node = Node(t)
                graph.add_node(node)
            hyperedge.tail.add(node)
        
        # Read Head nodes
        for h in head:
            node=graph.get_node_by_name(h)
            if (node==None):
                node = Node(h)
                graph.add_node(node)
            hyperedge.head.add(node)
        graph.add_hyperedge(hyperedge)    
      
    return graph

if __name__ == "__main__": main()
