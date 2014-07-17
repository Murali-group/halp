"""
   :module: graphspace
   :synopsis: Provides functionality to post directed hypergraphs to GraphSpace (located at www.holmes.cs.vt.edu).  Users must have an account on GraphSpace.

"""

from Net.GraphSpace.Node import Node
from Net.GraphSpace.Edge import Edge
from Net.GraphSpace.Graph import Graph
from Net.GraphSpace import GraphSpace

from hypergraph.directed_hypergraph import DirectedHypergraph

def post_to_graphspace(hypergraph,graphid,username,password,group=None):
    """Posts a directed hypergraph to GraphSpace with a specified graphid from a user with username and password.  Optionally shares the hypergraph with a group.  This function assumes that nodes are strings.

    Currently requires the GraphSpace python module written by David Badger.

    :param hypergraph: the hypergraph to post to GraphSpace.
    :param graphid: the name of the hypergraph in GraphSpace.
    :param username: the name of the user posting to GraphSpace
    (an email address)
    :param password: password of the user posting to GraphSpace
    :param group: (Optional) the name of the group the graph will 
    be shared with.

    :raises: TypeError -- only directed hypergraphs can be posted 
    to GraphSpace.

    """

    # TODO: how to deal with python module??  For now
    # I added it to the repo.

    # TODO: other things that will be useful:  
    # - Mapper dictionary of {node ids: common name}
    # - Add node colors, shapes, etc. as attributes
    # - Add edges colors, directed (True/False), width as attributes
    # - I often make a COLORS dictionary that maps color 
    # - Description HTML to describe the general graph 
    #   names / node types to HTML color codes.
    # - write the JSON to file (need to import json)

    if not isinstance(hypergraph, DirectedHypergraph):
        raise TypeError("Algorithm only applicable to directed hypergraphs")

    ## initialize GS graph
    ## no tags for now
    ## empty description for now.
    graph_space_graph = Graph(layout = 'ForceDirected', tags = [], \
                                  description = '')

    ## Node shape is fixed as a circle. Node size is fixed to 'auto'
    ## to make sure label fits in circle.  Color is fixed to
    ## gray. Node popup is empty (can be filled with HTML)
    node_shape = 'circle'
    node_size = 'auto'
    node_color = 'gray'
    node_popup = ''

    ## iterate over all nodes and add to GraphSpace graph.
    for node in hypergraph.get_node_set():
        # make graph space node
        graph_space_node = Node(id=node,label=node,color=node_color,\
                                    shape=node_shape,size=node_size,popup=node_popup)

        # add node to graph space graph
        graph_space_graph.add_node(graph_space_node)

    ## Hyperedge color is fixed as black. Hyperedge width is fixed at
    ## 1.  Hyperedges are directed, and a white square is introduced
    ## if there are multiple nodes in the tail or the head of a
    ## hyperedge.  In this case, the tail nodes are connected to the
    ## white square with undirected edges and the head nodes are
    ## connected to the white square with directed edges.
    hyperedge_color = 'black'
    hyperedge_width = 1
    hyperedge_popup = ''

    ## iterate over all hyperedges and add to GraphSpace graph.
    for hyperedge_id in hypergraph.get_hyperedge_id_set():

        # hyperedges should at least have a tail set, a head set, and a weight
        hyperedge_tail_set = hypergraph.get_hyperedge_attribute(hyperedge_id,'tail')
        hyperedge_head_set = hypergraph.get_hyperedge_attribute(hyperedge_id,'head')
        hyperedge_weight = hypergraph.get_hyperedge_attribute(hyperedge_id,'weight')

        ## if there is only one node in the tail and one node in the
        ## head, connect it with a directed edge.
        if len(hyperedge_tail_set)==1 and len(hyperedge_head_set)==1:
            # get single tail and single head from set. There must be
            # a better way to do this.
            hyperedge_tail = [t for t in hyperedge_tail_set][0]
            hyperedge_head = [t for t in hyperedge_head_set][0]

            # make graph space edge
            graph_space_edge = Edge(id=hyperedge_id,label='%s: weight=%f' % (hyperedge_id,hyperedge_weight),\
                                        source=hyperedge_tail,\
                                        target=hyperedge_head,color=hyperedge_color,\
                                        directed=True,width=hyperedge_width,\
                                        popup=hyperedge_popup)

            # add hyperedge to graph space graph
            graph_space_graph.add_edge(graph_space_edge)

        else:
            ## there is more than one node in the tail and/or one node
            ## in the head.  Introduce a white square node and use
            ## this to add the hyperedge to GraphSpace.

            # add white square node to graph space graph
            square_node = Node(id=hyperedge_id,label=hyperedge_id,color='white',\
                                   shape='square',size='auto',popup='')
            graph_space_graph.add_node(square_node)

            # add tails to reaction node
            for hyperedge_tail in hyperedge_tail_set:
                edge_name = hyperedge_tail+'-'+hyperedge_id
                # make graph space edge
                tail_edge = Edge(id=edge_name,\
                                     label='%s: weight=%f' % (edge_name,hyperedge_weight),\
                                     source=hyperedge_tail,\
                                     target=hyperedge_id,color=hyperedge_color,\
                                     directed=False,width=hyperedge_width,\
                                     popup=hyperedge_popup)
                # add hyperedge to graph space graph
                graph_space_graph.add_edge(tail_edge)

            # add reaction node to heads
            for hyperedge_head in hyperedge_head_set:
                edge_name = hyperedge_id+'-'+hyperedge_head
                # make graph space edge
                head_edge = Edge(id=edge_name,\
                                     label='%s: weight=%f' % (edge_name,hyperedge_weight),\
                                     source=hyperedge_id,\
                                     target=hyperedge_head,color=hyperedge_color,\
                                     directed=True,width=hyperedge_width,\
                                     popup=hyperedge_popup)
                # add hyperedge to graph space graph
                graph_space_graph.add_edge(head_edge)

    ## Graph Space Graph now contains all the information we want.
    ## Post it to the website.
    client = GraphSpace(user=username,password=password,url='http://holmes.cs.vt.edu/')
    client.add_graph(graph_space_graph,graphid,True)
        
    ## If specified, share the graph with a group. 
    if group != None:
        client.share_graph(graphid,group)


    return
