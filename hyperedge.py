# Would u plz always add comments to the code
class HyperEdge:
    pass


class DirectedHyperArc(HyperEdge):

    def __init__(self, head=set(), tail=None):
        self.tail = tail
        self.head = head


class DirectedHyperEdge(HyperEdge):

    def __init__(self, head=set(), tail=set()):
        self.tail = tail
        self.head = head
