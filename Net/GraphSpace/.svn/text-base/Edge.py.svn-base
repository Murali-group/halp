"""Represents an edge in a GraphSpace graph.
Note that a source and target node are required, even if your edges are undirected."""

from operator import attrgetter
import re

class Edge(object):

	@property
	def id(self):

		"""A string id unique among all edges."""
		return self._id

	@property
	def source(self):

		"""The id of the source node."""
		return self._source

	@property
	def target(self):

		"""The id of the target node."""
		return self._target

	@property
	def directed(self):

		"""True if the edge is directed from source to target."""
		return self._directed

	@directed.setter
	def directed(self, value):
		self._directed = value

	@property
	def label(self):

		"""The edge label."""
		return self._label

	@label.setter
	def label(self, value):
		self._label = value

	@property
	def popup(self):

		"""Stuff that goes in the popup window.
		Currently, this can contain some html."""
		return self._popup

	@popup.setter
	def popup(self, value):
		self._popup = value

	@property
	def color(self):

		"""The edge color in hex format.
		Examples: '#F00', '#F2F2F2'"""
		return self._color

	@color.setter
	def color(self, value):
		self._color = value

	@property
	def width(self):

		"""The width size as a floating point value."""
		return self._width

	@width.setter
	def width(self, value):
		self._width = value


	@property
	def style(self):

		"""The style (one of 'SOLID','DOT','LONG_DASH','EQUAL_DASH')"""
		return self._style

	@style.setter
	def style(self, value):
		self._style = value

	@property
	def graph_id(self):

		"""The id of a related graph.
		Example: 'graph42'"""
		return self._graph_id

	@graph_id.setter
	def graph_id(self, value):
		self._graph_id = value

	@property
	def labelFontWeight(self):

		"""Can be set to 'normal' or 'bold'."""
		return self._labelFontWeight

	@labelFontWeight.setter
	def labelFontWeight(self, value):
		self._labelFontWeight = value

	@property
	def k(self):

		""""""
		return self._k

	@k.setter
	def k(self, value):
		self._k = value

	def __init__(self, id, source, target, directed = None, label = None, popup = None, color = None, width = None, graph_id = None, labelFontWeight = None, k = None, style=None):
		
		# initialize read-only and private attributes directly
		self._id = id
		self._source = source
		self._target = target

		# initialize read-write attributes normally
		self.directed = directed
		self.label = label
		self.popup = popup
		self.color = color
		self.width = width
		self.graph_id = graph_id
		self.labelFontWeight = labelFontWeight
		self.k = k
		self.style = style

	def serialize(self):

		"""Return the edge in nested-dictionary form."""
		# the regex strips the leading _ from attribute names so the graphspace server will recognize them
		serial = {}
		for pair in vars(self).items():

			if pair[1] == None:# or pair[0] in []:
				continue
#			elif pair[0] in []:
#				serial[re.sub(r"^_", "", pair[0])] = [part.serialize() for part in pair[1]]
			else:
				serial[re.sub(r"^_", "", pair[0])] = pair[1]

		return serial


def new_edge_from_serial(serial):

	"""Return a new edge from nested-dictionary form."""
	e = Edge(serial["id"], serial["source"], serial["target"], serial["directed"])
	for pair in serial.items():

		eattr = attrgetter(pair[0])(e)
		if eattr:
			eattr = pair[1]

	return e

