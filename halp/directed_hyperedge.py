"""
.. module:: directed_hyperedge
    :synopsis: Defines DirectedHyperedge class for the properties of
            hyperedges in the directed hypergraph class. 

"""

import copy

class DirectedHyperedge(object):
    """
    The DirectedHyperedge class provides ...
    """
    
    def __init__(self, id, tail, head, attributes):
        """
        Constructor for the DirectedHyperedge class.

        This initializes all of the private fields necessary for storing
	information about this hyperedge.
        """
        self._id = id
        self._tail = tail
        self._head = head
        self._attributes = attributes

	# If weight attribute is not defined, assign it a default value of 1.
	if not "weight" in self._attributes:
	    self._attributes["weight"] = 1	    

        self.__frozen_tail = frozenset(tail)
        self.__frozen_head = frozenset(head)

    # This function is helpful for testing equality between hyperedges in
    # different hypergraphs or between a hyperedge and its deepcopy.
    def __eq__(self, other):
        return self._tail, self._head == other._tail, other._head

    def __hash__(self):
        return hash((self.__frozen_tail, self.__frozen_head))

    def get_attribute(self, attribute_name):
        """Given the name of an attribute, get a copy of it.

        :param attribute_name: name of the attribute to retrieve.
        :returns: attribute value of the attribute_name key for the
                specified hyperedge.
        :raises: ValueError -- No such attribute exists.

        Examples:
        ::

            >>> H = DirectedHypergraph()
            >>> hyperedge_list = (["A"], ["B", "C"]),
                                  (("A", "B"), ("C"), {weight: 2}),
                                  (set(["B"]), set(["A", "C"])))
            >>> hyperedges = H.add_hyperedges(hyperedge_list)
	    >>> attribute = hyperedges[1].get_attribute("weight")

        """
        if attribute_name not in self._attributes:
            raise ValueError("No such attribute exists.")
        else:
            return copy.copy(self._attributes[attribute_name])

    def get_attributes(self):
        """Get a dictionary of copies of this hyperedge's attributes.

        :returns: dict -- copy of each attribute of this hyperedge.

        """
        dict_to_copy = self._attributes.items()
        attributes = {}
        for attr_name, attr_value in dict_to_copy:
            attributes[attr_name] = copy.copy(attr_value)
        return attributes

    def set_attribute(attribute_name, value):
	"""Updates an attribute or adds it to the hyperedge.

        :param attribute_name: name of the attribute to set.
	:param value: the value to set the attribute.

        Examples:
        ::

            >>> H = DirectedHypergraph()
            >>> hyperedge_list = (["A"], ["B", "C"]),
                                  (("A", "B"), ("C"), {weight: 2}),
                                  (set(["B"]), set(["A", "C"])))
            >>> hyperedges = H.add_hyperedges(hyperedge_list)
	    >>> hyperedges[0].set_attribute("color", "red")

        """
	self._attributes[attribute_name] = value

    def get_tail(self):
        """Get a copy of this hyperedge's tail.
        
        :returns: a copy of the container of nodes that the user provided
            as the tail to this hyperedge.
        """
        return self._tail
                                                                
    def get_head(self):
        """Get a copy of this hyperedge's head.
        
        :returns: a copy of the container of nodes that the user provided
            as the head to this hyperedge.
        """
        return self._tail

    def get_weight(self):
	"""Gets the weight of this hyperedge.

	:returns: the weight of this hyperedge
	"""
	return self.get_attribute("weight")

