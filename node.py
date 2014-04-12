from copy import deepcopy

class Node:

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
