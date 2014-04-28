from __future__ import absolute_import

from copy import deepcopy

from .node import Node
from .hyperedge import *


class HyperGraph:

    def __init__(self, nodes=set(), hyperedges=set()):
        self._nodes = nodes
        self._hyperedges = hyperedges

    @property
    def nodes(self):
        '''
        Returns the nodes of the graph
        '''
        return self._nodes

    @property
    def hyperedges(self):
        '''
        Returns the edges of the graph.
        '''
        return self._hyperedges

    def add_node(self, n):
        '''
        Adds a node to the graph.
        '''
        try:
            assert isinstance(n, Node)
        except AssertionError:
            raise ValueError('Invalid node %s' % n)

        self._nodes.add(n)

    def get_node_by_name(self, nodeName):
        '''
        Get node by nodeName, otherwise returns None
        Node names should be unique
        '''
        for n in self.nodes:
            if n.name == nodeName:
                return n
        return None


    def remove_hypernode(self, n):
        '''
        Removes a hypernode from the graph.

        Should this remove all of the connected edges as well?
        '''
        pass

    def add_hyperedge(self, *args):
        '''
        Adds a hyperedge to the graph.
        Can be called with HyperEdge object or with edge names
        This method chooses the right class to call to hide this task 
        complexity from the user.
        usage:
            graph.add_hypergraph(hypergraph)
        or
            directedGraph.add_hypergraph(head, tail, weight)
            where:
                head = {'x1', 'x2', ...}
                tail = {'x4', 'x6', ...}
         or
            undirectedGraph.add_hypergraph(nodes, weight)
            where:
                nodes = {'x1', 'x2', ...}         
        '''
        if (len(args)==1):
            if (isinstance(args[0], HyperEdge)):
                self.add_hyperedgeByObject(args[0])
            else:
                self.add_hyperedgeByNames( args[0])
        elif (len(args)==2):
            self.add_hyperedgeByNames(args[0], args[1])
        elif (len(args)==3):
            self.add_hyperedgeByNames(args[0], args[1], args[2])
        else:
            raise ValueError('Invalid number of arguments {}'.format(len(args)))
            
    def add_hyperedgeByNames(self, **args):
        '''
            Add a hypergraph given the nodes names of the edge
            implimented in directed/undirected classes
        '''
        pass
        
    def add_hyperedgeByObject(self, h):
        '''
        Adds a hyperedge to the graph as a class h of HyperEdge.
        '''
        try:
            assert isinstance(h, HyperEdge)
        except AssertionError:
            #raise ValueError('Invalid hyperedge %s' % h)
            raise ValueError('Invalid hyperedge {}'.format(h))
       
        self._hyperedges.add(h)
        '''
        # nodes will be already be added before the edge
        self._nodes.update(h.head)
        if isinstance(h.tail, set):
            self._nodes.update(h.tail)
        else:
            self._nodes.add(h.tail)
        '''

    def remove_hyperedge(self, h):
        '''
        Removes a hyperedge from the graph
        '''
        self.hyperedges.remove(h)

    def copy(self):
        '''
        Returns a copy of the graph
        '''
        return deepcopy(self)
    
    def readDirectedHyperGraph(self):
        pass
    
    def readUndirectedHyperGraph(self):
        pass
    
    def printGraph(self):
       pass

'''----------------------- Directed HyperGraph --------------------------------- '''
class DirectedHyperGraph(HyperGraph):
    
    def __init__(self, nodes=set(), hyperedges=set()):
        HyperGraph.__init__(self, nodes, hyperedges)
       
    def printGraph(self):
        i = 1
        for h in self._hyperedges:
            print("Edge {}: Tail: {}, Head: {}, weight: {}".format(i, h.tail, h.head, h.weight))
            i +=1

    def add_hyperedgeByNames(self, head=set(), tail=set(), weight=0):
        '''
        Adds a hyperedge to the graph by node names.
        '''
         # Create hypergraph from current line
        hyperedge = HyperEdge(set(),set(), weight)
           
        # Read Tail nodes
        for t in tail:
            node = self.get_node_by_name(t)
            if (node == None):
                node = Node(t)
                self.add_node(node)
            hyperedge.tail.add(node)
        
        # Read Head nodes
        for h in head:
            node = self.get_node_by_name(h)
            if (node == None):
                node = Node(h)
                self.add_node(node)
            hyperedge.head.add(node)
        
        self.add_hyperedge(hyperedge)          

    def readDirectedGraph(self, fileName, sep='\t', delim=','):
        '''
            Read a directed hypergraph from file FileName
            each row is a hyperEdge.
            Tail, head and weight are separated by "sep"
            nodes within a hypernode are separated by "delim"
        '''
        fin = open(fileName, 'r')
    
        # read first header line
        fin.readline()
        i = 1
        for line in fin.readlines():
            line = line.strip('\n')
            if line == "": continue   # skip empty lines
            words = line.split(sep)
            if not (2 <= len(words) <= 3):
                raise Exception('File format error at line {}'.format(i))
            i+=1
            tail = words[0].split(delim)
            head = words[1].split(delim)
            try:
               weight = float(words[2].split(delim)[0])
            except: weight = 0
           
            # Create hypergraph from current line            
            self.add_hyperedge(head, tail, weight)              

class DirectedHyperArcGraph(HyperGraph):
    pass

'''----------------------- UnDirected HyperGraph --------------------------------- '''

class UndirectedHyperGraph(HyperGraph):
   
    def __init__(self, nodes=set(), hyperedges=set()):
        HyperGraph.__init__(self, nodes, hyperedges)
      
    def printGraph(self):
        i = 1
        for h in self._hyperedges:
            print("Edge {}: Nodes: {}, weight: {}".format(i, h.nodes, h.weight))
            i +=1
    
    def add_hyperedgeByNames(self, nodes=set(), weight=0):
        '''
        Adds a hyperedge to the graph by node names.
        '''
        # Create hypergraph from current line
        hyperedge = UndirectedHyperEdge(set(), weight)
           
        # Read edge nodes
        for n in nodes:
            node = self.get_node_by_name(n)
            if (node==None):
                node = Node(n)
                self.add_node(node)
            hyperedge.nodes.add(node)
       
        self.add_hyperedge(hyperedge)     
    
    def readUnDirectedGraph(self, fileName, sep='\t', delim=','):
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
            if line == "": continue   # skip empty lines
            words = line.split(sep)
            if not (1 <= len(words) <= 2):
                raise Exception('File format error at line {}'.format(i))
            i+=1
            nodes = words[0].split(delim)
            try:
               weight = float(words[1].split(delim)[0])
            except: weight = 0
           
            # Create hypergraph from current line           
            self.add_hyperedge(nodes, weight)
