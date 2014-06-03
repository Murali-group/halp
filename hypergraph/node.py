from copy import deepcopy


class Node:

    def __init__(self, name="", nodeId=-1):
        try:
            hash(name)
        except TypeError, e:
            raise TypeError(str(e) + " node name must be hashable")
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
        Returns a copy of the node
        '''
        return deepcopy(self)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return ''.join(["<Node name=", str(self.name),
                        " nodeId=", str(self.nodeId), ">"])

    def __eq__(self, n2):
        return self.name == n2.name and self.nodeId == n2.nodeId

    def __hash__(self):
        return hash((self.name, self.nodeId))
