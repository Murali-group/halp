"""Represents a node in a GraphSpace graph."""

from operator import attrgetter
import re

class Node(object):

	@property
	def id(self):
		
		"""A string id unique among all nodes."""
		return self._id

	@property
	def parent(self):
		
		"""The node parent."""
		return self._label

	@parent.setter
	def parent(self, value):
		self._parent = value

	@property
	def label(self):
		
		"""The node label."""
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
		
		"""The node color in hex format.
		Examples: '#F00', '#F2F2F2'"""
		return self._color

	@color.setter
	def color(self, value):
		self._color = value

	@property
	def size(self):
		
		"""The node size.
		If set to 'auto', the node is automatically sized to fit the label.
		Examples: 42, 10.5, 'auto'"""
		return self._size

	@size.setter
	def size(self, value):
		self._size = value

	@property
	def shape(self):
		
		"""The shape of the node.
		See http://cytoscapeweb.cytoscape.org/documentation/shapes for possible values."""
		return self._shape

	@shape.setter
	def shape(self, value):
		self._shape = value

	@property
	def graph_id(self):
		
		"""The id of a related graph.
		Example: 'graph42'"""
		return self._graph_id

	@graph_id.setter
	def graph_id(self, value):
		self._graph_id = value

	@property
	def borderWidth(self):
		
		"""The width of the node border.
		Example: 2.5"""
		return self._borderWidth

	@borderWidth.setter
	def borderWidth(self, value):
		self._borderWidth = value

	@property
	def labelFontWeight(self):
		
		"""Can be set to 'normal' or 'bold'."""
		return self._labelFontWeight

	@labelFontWeight.setter
	def labelFontWeight(self, value):
		self._labelFontWeight = value

#	@property
#	def zIndex(self):
#		
#		""""""
#		return self._zIndex
#
#	@zIndex.setter
#	def zIndex(self, value):
#		self._zIndex = value

	@property
	def k(self):
		
		""""""
		return self._k

	@k.setter
	def k(self, value):
		self._k = value

	def __init__(self, id, parent = None, label = None, popup = None, color = None, size = None, shape = None, graph_id = None, borderWidth = None, labelFontWeight = None, zIndex = None, k = None):

		# initialize read-only and private attributes directly
		self._id = id

		# initialize read-write attributes normally
		self.parent = parent
		self.label = label
		self.popup = popup
		self.color = color
		self.size = size
		self.shape = shape
		self.graph_id = graph_id
		self.borderWidth = borderWidth
		self.labelFontWeight = labelFontWeight
#		self.zIndex = zIndex
		self.k = k

	def serialize(self):

		"""Return the node in nested-dictionary form."""
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

def new_node_from_serial(serial):

	"""Return a new node from nested-dictionary form."""
	n = Node(serial["id"])
	for pair in serial.items():

		nattr = attrgetter(pair[0])(n)
		if nattr:
			nattr = pair[1]

	return n

