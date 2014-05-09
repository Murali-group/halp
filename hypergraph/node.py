from copy import deepcopy


class Node(object):

    def __init__(self, name="", nodeId=-1):
        self._name = name
        self._nodeId = nodeId

    @property
    def name(self):
        '''
        Returns the name of the node
        '''
        return self._name

    @property
    def nodeId(self):
        '''
        Returns the id of the node
        '''
        return self._nodeId

    def copy(self):
        '''
        Returns a ccopy of the node
        '''
        return deepcopy(self)

    def __repr__(self):
        return self._name

    def __str__(self):
        return self._name

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self._name == other._name
                and self._nodeId == other._nodeId)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self._name, self._nodeId))
