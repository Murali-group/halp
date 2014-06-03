from hypergraph.hyperedge import HyperEdge
from hypergraph.node import Node
from hypergraph.directedHyperGraph import DirectedHyperGraph
from PIL import Image
import numpy
from IPython import embed
import math


def PIL2array(img):
    return numpy.array(img.getdata(), numpy.int32).reshape(
        (img.size[1], img.size[0]))

flower = Image.open('./flower.jpg').convert('L')


class FPixel:

    def __init__(self, xy, f):
        self.xy = xy
        self.f = f

    def __repr__(self):
        return "<FPixel " + str(self.xy) + " f=" + str(self.f) + ">"

    def __eq__(self, fpix):
        return self.f == fpix.f and self.xy == fpix.xy

    def __hash__(self):
        return hash((self.xy[0], self.xy[1], self.f))


def neighbors(arr, i, j, d):
    assert i < arr.shape[0] and i >= 0
    assert j < arr.shape[1] and j >= 0
    left_d = min(d, i)
    right_d = min(d, arr.shape[0] - (i + 1))
    top_d = min(d, j)
    bottom_d = min(d, arr.shape[1] - (j + 1))

    for r in xrange(i - left_d, i + right_d + 1):
        for c in xrange(j - top_d, j + bottom_d + 1):
            if (r, c) != (i, j):
                yield FPixel((r, c), arr[r, c])


def compute_lambda(b_neighbors, v_center):
    intensities = [v.f for v in b_neighbors + [v_center]]
    avg = numpy.average(intensities)
    std = numpy.std(intensities)
    if std == 0:
        return avg
    else:
        return avg / std


def Gamma(arr, x, y, beta, lmbda):
    vp = FPixel((x, y), arr[x, y])
    b_neighbors = neighbors(arr, x, y, beta)
    l_neighbors = [v for v in b_neighbors if abs(v.f - vp.f) <= lmbda]
    return l_neighbors


def weight(head, center_v):
    s = 0
    for v in head:
        s += abs(v.f - center_v.f)
    avg = s / float(len(head))
    return math.exp(avg)


def gen_missing_hyperedges(head1, head2, center_v, b_neighbors):
    missing = set(b_neighbors) - set(head1).union(set(head2))
    for v in missing:
        yield HyperEdge(set([Node(v)]), set([Node(center_v)]), 10e-4)


def gen_DINH_hyperedges(arr, beta, x, y):
    vpix = FPixel((x, y), arr[x, y])
    b_neighbors = list(neighbors(arr, x, y, beta))
    l = compute_lambda(b_neighbors, vpix)
    gamma = Gamma(arr, x, y, beta, l)
    e1_tail = set(v for v in gamma if v.f < vpix.f)
    e1_head = set(v for v in gamma if v.f >= vpix.f)
    e2_tail = set(v for v in gamma if v.f > vpix.f)
    e2_head = set(v for v in gamma if v.f <= vpix.f)

    e1_tail.add(vpix)
    e2_tail.add(vpix)

    def mk_node_set(s):
        return set(map(Node, s))

    hes = []
    if e1_head:
        e1 = HyperEdge(mk_node_set(e1_head),
                       mk_node_set(e1_tail),
                       weight(e1_head, vpix))
        hes.append(e1)
    if e2_head:
        e2 = HyperEdge(mk_node_set(e2_head),
                       mk_node_set(e2_tail),
                       weight(e2_head, vpix))
        hes.append(e2)
    missing = list(gen_missing_hyperedges(e1_head, e2_head, vpix, b_neighbors))
    return hes + missing


def gen_DINH(img):
    arr = PIL2array(img)
    d = DirectedHyperGraph(set(), set())
    print(arr.shape)
    for i in xrange(arr.shape[0]):
        for j in xrange(arr.shape[1]):
            for he in gen_DINH_hyperedges(arr, 1, i, j):
                d.add_hyperedgeByObject(he)
        print(i, i/float(arr.shape[0]))
    return d

d = gen_DINH(flower)
# p = d._transition_matrix()

embed()
