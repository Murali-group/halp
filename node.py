class Node:

    def __init__(self, name="", nodeId=-1):
        self.name = name
        self.nodeId = nodeId

    @classmethod
    def fromNode(cls, node):
        name = node.name.copy()
        nodeId = node.nodeId.copy()
        return cls(name, nodeId)
