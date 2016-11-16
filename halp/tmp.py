from algorithms.directed_paths import *
#from directed_hypergraph import DirectedHypergraph
#from directed_hyperedge import DirectedHyperedge

# TEMP - for testing
def main():
    H = DirectedHypergraph()
    H.add_node("A")
    H.add_node("B")
    H.add_node("C")
    H.add_node("D")
    H.add_node("E")
    edge = H.add_hyperedge(set(["A", "B"]), set(["C", "D", "E"]), {'color': 'red'})
    print(edge.get_attributes())
    print(H.has_hyperedge(("A", "B"), ("C", "D", "E")))

main()
