from hypergraph.priority_queue import PriorityQueue


def test_priority_queue():
    Q = PriorityQueue()

    Q.add_element(3, "a")
    Q.add_element(2, "b")
    Q.add_element(4, "c")
    Q.add_element(1, "d")
    Q.add_element(5, "e")

    assert not Q.is_empty()

    assert Q.contains_element("a")
    assert Q.contains_element("b")
    assert Q.contains_element("c")
    assert Q.contains_element("d")
    assert Q.contains_element("e")

    assert Q.peek() == "d"

    Q.reprioritize(6, "d")
    Q.reprioritize(7, "d")
    Q.reprioritize(8, "d")

    assert Q.peek() == "b"

    Q.delete_element("b")

    assert not Q.contains_element("b")
    assert Q.peek() == "a"
    assert Q.get_top_priority() == "a"
    assert not Q.contains_element("a")

    # Try invalid delete
    try:
        Q.delete_element("b")
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    # Try invalid reprioritize
    try:
        Q.reprioritize(1, "b")
        assert False
    except ValueError:
        pass
    except BaseException as e:
        assert False, e

    Q = PriorityQueue()

    # Try invalid peek
    try:
        Q.peek()
        assert False
    except IndexError:
        pass
    except BaseException as e:
        assert False, e

    # Try invalid get_top_priority
    try:
        Q.get_top_priority()
        assert False
    except IndexError:
        pass
    except BaseException as e:
        assert False, e
