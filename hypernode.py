class HyperNode:

    def __init__(self, nodes=set(), inList=set(), outList=set()):
        self.nodes = nodes
        self.inList = inList
        self.outList = outList

    @classmethod
    def fromHyperNode(cls, hypernode):
        nodes = hypernode.nodes
        inList = hypernode.inList
        outList = hypernode.outList
        return cls(nodes, inList, outList)
