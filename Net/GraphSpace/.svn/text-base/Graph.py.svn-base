"""Represents a graph in GraphSpace."""

import re
from operator import attrgetter
from .Node import Node, new_node_from_serial
from .Edge import Edge, new_edge_from_serial

class Graph(object):

	@property
	def name(self):

		"""Name of the graph."""
		return self._name

	@name.setter
	def name(self, value):
		self._name = value

	@property
	def description(self):

		"""Graph description. Can contain some html."""
		return self._description

	@description.setter
	def description(self, value):
		self._description = value

	@property
	def tags(self):

		"""An array of tag names."""
		return self._tags

	@tags.setter
	def tags(self, value):
		self._tags = value

	@property
	def layout(self):

		"""Name of the default layout to use for the graph."""
		return self._layout

	@layout.setter
	def layout(self, value):
		self._layout = value

	def __init__(self, name = None, description = None, tags = None, layout = None):
		
		# initialize read-only and private attributes directly
		self._nodes = []
		self._edges = []
		self._nodes_map = {}

		# initialize read-write attributes normally
		self.name = name
		self.description = description
		self.tags = tags
		self.layout = layout
	
	def add_node(self, node):
		
		self._nodes.append(node)
		self._nodes_map[node.id] = node
		
	def add_edge(self, edge):

		if edge.source not in self._nodes_map:
			raise Exception("No such node corresponds to the edge's source node %s" %(edge.source))
		if edge.target not in self._nodes_map:
			raise Exception("No such node corresponds to the edge's target node %s" %(edge.target))
		self._edges.append(edge)
		
	def add_nodes(self, nodes):
		[self.add_node(node) for node in nodes]
		
	def add_edges(self, edges):
		[self.add_edge(edge) for edge in edges]

	def serialize(self):

		"""Return the graph in nested-dictionary form."""
		serial = {"metadata" : {}, "graph" : {"data" : {}}}
		for pair in vars(self).items():

			if pair[1] == None or pair[0] in ["_nodes_map"]:
				continue
			elif pair[0] in ["_nodes", "_edges"]:
				serial["graph"]["data"][re.sub(r"^_", "", pair[0])] = [part.serialize() for part in pair[1]]
			else:
				serial["metadata"][re.sub(r"^_", "", pair[0])] = pair[1]

		return serial
	
def new_graph_from_serial(serial):
	
	"""Return a new graph from nested-dictionary form."""
	g = Graph()
	for pair in serial["metadata"].items():

		gattr = attrgetter(pair[0])(g)
		if gattr:
			gattr = pair[1]

	for node in serial["graph"]["data"]["nodes"]:
		g.add_node(new_node_from_serial(node))
	for edge in serial["graph"]["data"]["edges"]:
		g.add_edge(new_edge_from_serial(edge))
	return g

