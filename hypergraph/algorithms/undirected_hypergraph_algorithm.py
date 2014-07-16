import random
import numpy as np
from scipy import sparse
from scipy.sparse import linalg


class UndirectedHypergraphAlgorithm(object):

    def __init__(self, UndirectedHypergraph=None):
        self._H = UndirectedHypergraph
        self._nodeidList2nodeset, self._nodeset2nodeid = \
            self._get_nodeset2nodeid()
        self._hyperedgeWeight = {}
        self._incidenceMatrix = self._getIncidenceMatrix()
        self._W = self._getDiagonalWeightMatrix()
        self._D_v = self._getDiagonalNodeMatrix()
        self._D_e = self._getDiagonalEdgeMatrix()
        print("Hypergraph with {0} number of nodes and {1} number of edges"
              .format(len(self._H.get_node_set()),
                      len(self._H.get_hyperedge_id_set())))

    def getNodeNumber(self):
        return len(self._H.get_node_set())

    def getHyperedgeNumber(self):
        return len(self._H.get_hyperedge_id_set())

    def get_nodeid2nodeset(self):
        return self._nodeidList2nodeset

    def get_nodeset2nodeid(self):
        return self._nodeset2nodeidList

    def _get_nodeset2nodeid(self):
        nodeSet = self._H.get_node_set()
        nodeset2nodeidList = {}
        nodeidList2nodeset = {}
        node_id = 0
        for node in nodeSet:
            nodeset2nodeidList.update({node: node_id})
            nodeidList2nodeset.update({node_id: node})
            node_id += 1
        return nodeidList2nodeset, nodeset2nodeidList

    def _getIncidenceMatrix(self):
        nodeNumber = len(self._H.get_node_set())
        edgeNumber = len(self._H.get_hyperedge_id_set())
        rows = []
        cols = []

        for hyperedge_id in self._H.hyperedge_id_iterator():
            for node in self._H.get_hyperedge_nodes(hyperedge_id):
                # get the mapping btw node and its id
                rows.append(self._nodeset2nodeid.get(node))
                # since it starts with e, like e31
                cols.append(int(hyperedge_id[1:])-1)
            self._hyperedgeWeight.update(
                {str(int(hyperedge_id[1:])-1):
                 self._H.get_hyperedge_weight(hyperedge_id)})
        values = np.ones(len(rows), dtype=int)
        return sparse.csc_matrix((values, (rows, cols)),
                                 shape=(len(set(rows)),
                                 len(set(cols))))

    '''
        Returns a diagonal matrix containing the hyperedge weights
    '''
    def _getDiagonalWeightMatrix(self):
        edgeNumber = len(self._H.get_hyperedge_id_set())
        edgeWeightVector = []
        for i in range(edgeNumber):
            edgeWeightVector.append(self._hyperedgeWeight.get(str(i)))
        return sparse.diags([edgeWeightVector], [0])

    '''
        Returns a diagonal matrix containing the node degrees
        which is basically the summation of the weights of each
        node's incident edges
    '''
    def _getDiagonalNodeMatrix(self):
        return sparse.diags([self._incidenceMatrix * self._W.diagonal()], [0])

    '''
        Returns a diagonal matrix containing the hyperedge degrees
    '''
    def _getDiagonalEdgeMatrix(self):
        edgeNumber = len(self._H.get_hyperedge_id_set())
        degrees = self._incidenceMatrix.sum(0)
        new_degree = []
        degrees = degrees.transpose()
        for degree in degrees:
            new_degree.append(int(degree[0:]))

        return sparse.diags([new_degree], [0])

    '''
        this inverse only works for diagonal matrix and its much faster
        than the linalg.inv() function
    '''
    def _fastInverse(self, M):
        diags = M.diagonal()
        new_diag = []
        for value in diags:
            new_diag.append(1.0/value)
        return sparse.diags([new_diag], [0])

    '''
        Creates the transition matrix for the random walk
    '''
    def randomWalkMatrix(self):
        H = self._incidenceMatrix
        D_v_inverse = self._fastInverse(self._D_v)
        D_e_inverse = self._fastInverse(self._D_e)
        H_transpose = H.transpose()
        P = D_v_inverse * H
        P = P * self._W
        P = P * D_e_inverse
        P = P * H_transpose
        return P

    '''
        Creates a random vector as the starting point for doing the random walk
    '''
    def _createRandomStarter(self):
        nodeNumber = len(self._H.get_node_set())
        pi = np.zeros(nodeNumber, dtype=float)
        for i in range(nodeNumber):
            pi[i] = random.random()
        summation = np.sum(pi)
        for i in range(nodeNumber):
            pi[i] = pi[i] / summation
        return pi

    '''
        Checks whether the stationary distribution converged
    '''
    def _converged(self, pi_star, pi):
        nodeNumber = pi.shape[0]
        for i in range(nodeNumber):
            if pi[i]-pi_star[i] > 10e-6:
                return False
        return True

    '''
        Finds the stationary distribution of a hypergraph
    '''
    def stationaryDistribution(self, P):
        nodeNumber = len(self._H.get_node_set())
        pi = self._createRandomStarter()
        pi_star = self._createRandomStarter()
        while not self._converged(pi_star, pi):
            pi = pi_star
            pi_star = pi * P
        return pi

    '''
        Finds the Normalized Laplacian Matrix
    '''
    def normalizedLaplacian(self):
        nodeNumber = len(self._H.get_node_set())
        D_v_sqrt = self._D_v.sqrt()
        D_v_sqrt_inverse = np.real(self._fastInverse(D_v_sqrt).todense())
        D_v_sqrt_inverse = sparse.csc_matrix(D_v_sqrt_inverse)
        D_e_inverse = self._fastInverse(self._D_e)
        H = self._incidenceMatrix
        H_transpose = H.transpose()
        Theta = D_v_sqrt_inverse * H
        Theta = Theta * self._W
        Theta = Theta * D_e_inverse
        Theta = Theta * H_transpose
        Theta = Theta * D_v_sqrt_inverse
        I = sparse.eye(nodeNumber)
        Delta = I - Theta
        return Delta

    '''
        Applies the Normalized MinCut algorithm.
        The result of this algorithm is a bipartition
        The return value is a two dimensional array containing
        the node names for the first and second partition
    '''
    def minCut(self, threshold=0, numberOfEigenValues=None):
        '''
        TODO: make sure that the hypergraph is connected
        '''
        Delta = self.normalizedLaplacian()
        eigenValues, eigenVectors = np.linalg.eig(Delta.todense())
        '''
            since the eigs method in sparse.linalg library doesn't find
            all the eigenvalues and eigenvectors, it doesn't give us an
            exact and correct solution. Therefore, we should use the
            numpy library which works on dense graphs. This might be
            problematic for large graphs.
        '''
        # eigenValues,eigenVectors = linalg.eigs(Delta,k=numberOfEigenValues)
        second_min_index = np.argsort(eigenValues)[1]
        secondEigenVector = eigenVectors[:, second_min_index]

        partitionIndex = [
            i for i in range(
                len(secondEigenVector)) if secondEigenVector[i] >= threshold]
        Partition = [list() for x in range(2)]
        for (key, value) in list(self._nodeset2nodeid.items()):
            if value in partitionIndex:
                Partition[0].append(key)
            else:
                Partition[1].append(key)
        return Partition
