"""
.. module:: node
   :synopsis: Defines Node class and other useful properties associated
   with nodes.

"""

from copy import deepcopy


class Node(object):
    """
    Node class provides a basic node object which is identified by a name.

    """

    def __init__(self, name=""):
        """
        Node class constructor.
        :param name: Name to reference the node by.
        :type name: str.
        :raises: TypeError

        """

        try:
            hash(name)
        except TypeError as e:
            raise TypeError(str(e) + " node name must be hashable")

        self._name = name

    @property
    def name(self):
        """
        Returns the name of the node.
        :returns: str -- name of the node.

        """

        return self._name

    @name.setter
    def name(self, value):
        """
        Sets the name of the node.
        :param value: name to set the node.
        :type value: str.

        """

        self._name = value

    def copy(self):
        """
        Returns a deep copy of the node.
        :returns: Node -- new node with same name.

        """

        return deepcopy(self)

    def __str__(self):
        """
        Returns overriden Node to-string as:
            <Node name="node_name">
        :returns: str -- node representation string.

        """

        return "<Node name=" + str(self.name) + ">"

    def __repr__(self):
        """
        Returns overriden Node representation to be equivalent to __str__.
        :returns: str -- node representation as __str__.

        """

        return str(self)

    def __eq__(self, other):
        """
        Returns overriden Node equality to be true iff names match.
        :returns: bool. -- whether nodes are equal based on names.

        """

        return isinstance(other, self.__class__) and (self.name == other.name)

    def __hash__(self):
        """
        Returns overriden Node hash to be the hash of the node's name.
        :returns: int -- hash of the node object.

        """

        return hash(self.name)
