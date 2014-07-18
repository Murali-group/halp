"""Net.GraphSpace provides bindings for the GraphSpace API.
GraphSpace is a web based graph/network visualization tool and data store.
See http://graphspace.org for more information."""

from Net.GraphSpace.Node import Node
from Net.GraphSpace.Edge import Edge
from Net.GraphSpace.Graph import Graph, new_graph_from_serial
try:
    import urllib.request as urllib2
except:
    import urllib2
import json
import re

class GraphSpace(object):
	
	@property
	def user(self):

		"""Username on the GraphSpace server."""
		return self._user

	@property
	def password(self):

		"""Password on the GraphSpace server."""
		return self._password

	@property
	def url(self):

		"""URL of the GraphSpace server."""
		return self._url
	
	def __init__(self, user, password, url):
		
		# initialize read-only and private attributes directly
		self._user = user
		self._password = password
		self._url = url
		self._base = re.sub(r"\/$", "/api/", self.url)
		auth_handler = urllib2.HTTPBasicAuthHandler()
		auth_handler.add_password("restricted area", self.url, self.user, self.password)
		self._ua = urllib2.build_opener(auth_handler)

	def add_graph(self, graph, graph_id = None, update = False):
		
		"""Takes a Net.GraphSpace.Graph object and uploads it.
		If graph_id is not provided, an id is auto-generated for you by the server.
		An optional named parameter 'update' defaults to False.
		This means that an extra check is made to see if the graph with the given
		graph_id already exists on the server.
		An exception is thrown if it is found.
		Set update = True if you don't want this check.
		This will result in greater efficiency, since one less http request is made to
		the server.
		Also, if the graph already exists, it will get overwritten.
		Returns a dictionary of the form:
		
			{ "id" : "the id", "url" : "http://..." }
		
		The url is the location where the graph can be viewed."""
		req = None
		res = None
		if graph_id is not None:	

			if not update and self.get_graph(graph_id):
				raise Exception("Graph %s already exists" %(graph_id))
			#print 'REQUESTING URL %s' % (self._base + "users/%s/graphs/%s" %(self.user, graph_id))
			req = urllib2.Request(self._base + "users/%s/graphs/%s" %(self.user, graph_id), json.dumps(graph.serialize()))
			# this approach is not ideal
			req.get_method = lambda: "PUT"
			
		else:
			req = urllib2.Request(self._base + "users/%s/graphs" %(self.user), json.dumps(graph.serialize()))
		res = self._ua.open(req)
		return json.loads(res.read())

	def add_json_graph(self, graph, graph_id = None, update = False):
		
		"""Takes a Net.GraphSpace.Graph object and uploads it.
		If graph_id is not provided, an id is auto-generated for you by the server.
		An optional named parameter 'update' defaults to False.
		This means that an extra check is made to see if the graph with the given
		graph_id already exists on the server.
		An exception is thrown if it is found.
		Set update = True if you don't want this check.
		This will result in greater efficiency, since one less http request is made to
		the server.
		Also, if the graph already exists, it will get overwritten.
		Returns a dictionary of the form:
		
			{ "id" : "the id", "url" : "http://..." }
		
		The url is the location where the graph can be viewed."""
		req = None
		res = None
		if graph_id is not None:	

			if not update and self.get_graph(graph_id):
				raise Exception("Graph %s already exists" %(graph_id))
			#print 'REQUESTING URL %s' % (self._base + "users/%s/graphs/%s" %(self.user, graph_id))
			req = urllib2.Request(self._base + "users/%s/graphs/%s" %(self.user, graph_id), graph)
			# this approach is not ideal
			req.get_method = lambda: "PUT"
			
		else:
			req = urllib2.Request(self._base + "users/%s/graphs" %(self.user), graph) #json.dumps(graph.serialize())
		res = self._ua.open(req)
		return json.loads(res.read())
		
	def get_graph(self, graph_id):

		"""Returns a Net.GraphSpace.Graph object for the given graph_id.
		Returns None if the graph could not be found."""
		req = urllib2.Request(self._base + "users/%s/graphs/%s" %(self.user, graph_id))
		res = None
		g = None
		try:
			res = self._ua.open(req)
		except Exception as e:
			
			if e.code != 404:
				raise e
		
		if res:
			g = new_graph_from_serial(json.loads(res.read()))
		return g
		
	
	def delete_graph(self, graph_id):
		
		"""Deletes the graph with id graph_id.
		Returns True on success."""
		req = urllib2.Request(self._base + "users/%s/graphs/%s" %(self.user, graph_id))
		# this approach is not ideal
		req.get_method = lambda: "DELETE"
		res = self._ua.open(req)
		return True

#	def create_group(self, group_id):
#		
#		"""Create a group named group_id.
#		Returns True on success."""
#		req = urllib2.Request(self._base + "api/groups/%s" %(group_id))
#		# this approach is not ideal
#		req.get_method = lambda: "PUT"
#		res = self._ua.open(req)
#		return True

#	def delete_group(self, group_id):
#		
#		"""Delete the group named group_id.
#		Returns True on success."""
#		req = urllib2.Request(self._base + "api/groups/%s" %(group_id))
#		# this approach is not ideal
#		req.get_method = lambda: "DELETE"
#		res = self._ua.open(req)
#		return True

#	def add_user_to_group(self, user_id, group_id):
#		
#		"""Adds the user with id user_id to the group named group_id.
#		Returns True on success."""
#		req = urllib2.Request(self._base + "api/groups/%s/adduser/%s" %(group_id, user_id))
#		# this approach is not ideal
#		req.get_method = lambda: "GET"
#		res = self._ua.open(req)
#		return True

#	def remove_user_from_group(self, user_id, group_id):
#		
#		"""Removes the user with id user_id from the group named group_id.
#		Returns True on success."""
#		req = urllib2.Request(self._base + "api/groups/%s/removeuser/%s" %(group_id, user_id))
#		# this approach is not ideal
#		req.get_method = lambda: "GET"
#		res = self._ua.open(req)
#		return True

	def share_graph(self, graph_id, group_id):
		
		"""Shares the graph with name graph_name with the group group_name.
		Returns True on success."""
		req = urllib2.Request(self._base + "users/%s/graphs/%s/share/%s" %(self.user, graph_id, group_id))
		# this approach is not ideal
		req.get_method = lambda: "GET"
		res = self._ua.open(req)
		return True

	def unshare_graph(self, graph_id, group_id):
		
		"""Unshares the graph with name graph_name with the group group_name.
		Returns True on success."""
		req = urllib2.Request(self._base + "users/%s/graphs/%s/unshare/%s" %(self.user, graph_id, group_id))
		# this approach is not ideal
		req.get_method = lambda: "GET"
		res = self._ua.open(req)
		return True
