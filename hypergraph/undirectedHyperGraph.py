from __future__ import absolute_import

from .hypergraph import HyperGraph
from copy import deepcopy

from .node import Node
from .hyperedge import HyperEdge, UndirectedHyperEdge

'''----------------------- UnDirected HyperGraph ---------------------------'''


class UndirectedHyperGraph(HyperGraph):

    def __init__(self, nodes=set(), hyperedges=set()):
        HyperGraph.__init__(self, nodes, hyperedges)

    def printGraph(self):
        i = 1
        for h in self._hyperedges:
            print(
                "Edge {}: Nodes: {}, weight: {}".format(i, h.nodes, h.weight))
            i += 1

    def add_hyperedgeByNames(self, nodes=set(), weight=0):
        '''
        Adds a hyperedge to the graph by node names.
        '''
        # Create hypergraph from current line
        hyperedge = UndirectedHyperEdge(set(), weight)

        # Read edge nodes
        for n in nodes:
            node = self.get_node_by_name(n)
            if (node is None):
                node = Node(n)
                self.add_node(node)
            hyperedge.nodes.add(node)

        self.add_hyperedge(hyperedge)

    def read(self, fileName, sep='\t', delim=','):
        '''
            Read an undirected hypergraph from file FileName
            each row is a hyperEdge.
            nodes and weight are separated by "sep"
            nodes within a hyperedge are separated by "delim"
        '''
        fin = open(fileName, 'r')

        # read first header line
        fin.readline()
        i = 1
        for line in fin.readlines():
            line = line.strip('\n')
            if line == "":
                continue   # skip empty lines
            words = line.split(sep)
            if not (1 <= len(words) <= 2):
                raise Exception('File format error at line {}'.format(i))
            i += 1
            nodes = words[0].split(delim)
            try:
                weight = float(words[1].split(delim)[0])
            except:
                weight = 0

            # Create hypergraph from current line
            self.add_hyperedge(nodes, weight)
        fin.close()

    def write(self, fileName, sep='\t', delim=','):
        '''
            write an undirected hypergraph to file FileName
            each row is a hyperEdge.
            Tail, head and weight are separated by "sep"
            nodes within a hypernode are separated by "delim"
        '''
        fout = open(fileName, 'w')

        # write first header line
        fout.write("Edge"+ sep+"weight\n")
       
        for e in self.hyperedges:
            line = ""
            for n in e.nodes:
               line+=n.name + delim
            line = line[:-1]    # remove last extra delim                     
            line+=sep + str(e.weight) + "\n"
            fout.write(line)            
        fout.close()