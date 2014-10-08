"""
.. module:: priority_queue
   :synopsis: Wrapper for python's heapq to provide some standard
            operations expected a priority queue.

"""
import heapq
import itertools


class PriorityQueue(object):
    """
    Priority queue implementation based on the suggested "mark-as-invalid"
    technique by Python's heapq documentation:
    https://docs.python.org/3.4/library/heapq.html#priority-queue-implementation-notes

    :note: This implementation only allows unique elements.

    """

    def __init__(self):
        """
        Constructor for the PriorityQueue class.

        """
        # pq: the priority queue list; heapq ensures that pq maintains
        # the heap invariant
        self.pq = []

        # counter: unique sequence count (to resolve element orderings in the
        # case of equal priorities)
        self.counter = itertools.count(1)

        # element_finder: mapping of elements to entries (allows element
        # priority modification or deletion)
        self.element_finder = {}

        # INVALID: mark an entry as deleted (via assigning count of 0)
        self.INVALID = 0

    def add_element(self, priority, element, count=None):
        """Adds an element with a specific priority.

        :param priority: priority of the element.
        :param element: element to add.

        """
        if count is None:
            count = next(self.counter)
        entry = [priority, count, element]
        self.element_finder[element] = entry
        heapq.heappush(self.pq, entry)

    def get_top_priority(self):
        """Pops the element that has the top (smallest) priority.

        :returns: element with the top (smallest) priority.
        :raises: IndexError -- Priority queue is empty.

        """
        if self.is_empty():
            raise IndexError("Priority queue is empty.")
        _, _, element = heapq.heappop(self.pq)
        if element in self.element_finder:
            del self.element_finder[element]
        return element

    def delete_element(self, element):
        """Deletes an element (lazily).

        :raises: ValueError -- No such element in the priority queue.

        """
        if element not in self.element_finder:
            raise ValueError("No such element in the priority queue.")
        entry = self.element_finder[element]
        entry[1] = self.INVALID

    def reprioritize(self, priority, element):
        """Updates the priority of an element.

        :raises: ValueError -- No such element in the priority queue.

        """
        if element not in self.element_finder:
            raise ValueError("No such element in the priority queue.")
        entry = self.element_finder[element]
        self.add_element(priority, element, entry[1])
        entry[1] = self.INVALID

    def peek(self):
        """Returns the element with top (lowest) priority without popping it.

        :returns: element with top (lowest) priority.
        :raises: IndexError -- Priority queue is empty.

        """
        if self.is_empty():
            raise IndexError("Priority queue is empty.")
        return self.pq[0][2]

    def contains_element(self, element):
        """Determines if an element is contained in the priority queue."

        :returns: bool -- true iff element is in the priority queue.

        """
        return (element in self.element_finder) and \
            (self.element_finder[element][1] != self.INVALID)

    def is_empty(self):
        """Determines if the priority queue has any elements.
        Performs removal of any elements that were "marked-as-invalid".

        :returns: true iff the priority queue has no elements.

        """
        while self.pq:
            if self.pq[0][1] != self.INVALID:
                return False
            else:
                _, _, element = heapq.heappop(self.pq)
                if element in self.element_finder:
                    del self.element_finder[element]
        return True
