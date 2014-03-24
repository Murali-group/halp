class HyperGraph:

    def __init__(self, nodes=set(), hypernodes=set(), hyperedges=set()):
        self.nodes = nodes
        self.hypernodes = hypernodes
        self.hyperedges = hyperedges


class DirectedHyperGraph(HyperGraph):
    pass


class DirectedHyperArcGraph(HyperGraph):
    pass
