import pytest
from pygame.math import Vector2

from data_structures import AABB, KdTree


class DummyElement:
    def __init__(self, x: float, y: float, name: str = ""):
        self.pos = Vector2(x, y)
        self.name = name

    def __repr__(self):
        return f"DummyElement(name={self.name}, pos=({self.pos.x}, {self.pos.y}))"


@pytest.fixture
def bounds():
    return AABB(Vector2(0, 0), Vector2(100, 100))


@pytest.fixture
def tree(bounds):
    return KdTree(bounds, max_capacity=2, max_depth=6)


def test_insert_and_query_point(tree):
    e1 = DummyElement(10, 10, "a")
    e2 = DummyElement(20, 20, "b")

    assert tree.insert(e1) is True
    assert tree.insert(e2) is True

    results = tree.query(Vector2(10, 10))
    assert e1 in results
    assert e2 not in results


def test_query_point_out_of_bounds_returns_empty(tree):
    assert tree.query(Vector2(1000, 1000)) == []


def test_query_aabb_returns_elements_inside(bounds):
    kd = KdTree(bounds, max_capacity=4, max_depth=6)
    e1 = DummyElement(10, 10, "a")
    e2 = DummyElement(30, 30, "b")
    e3 = DummyElement(90, 90, "c")

    kd.insert(e1)
    kd.insert(e2)
    kd.insert(e3)

    results = kd.query(AABB(Vector2(0, 0), Vector2(50, 50)))
    assert e1 in results
    assert e2 in results
    assert e3 not in results


def test_insert_out_of_bounds_returns_false(bounds):
    kd = KdTree(bounds)
    e = DummyElement(150, 150, "outside")
    assert kd.insert(e) is False


def test_remove_existing_element(tree):
    e = DummyElement(25, 25, "a")
    tree.insert(e)

    assert tree.remove(e) is True
    assert tree.query(Vector2(25, 25)) == []


def test_remove_missing_element_returns_false(tree):
    e = DummyElement(25, 25, "missing")
    assert tree.remove(e) is False


def test_nearest_returns_closest(bounds):
    kd = KdTree(bounds, max_capacity=2, max_depth=6)
    e1 = DummyElement(10, 10, "a")
    e2 = DummyElement(90, 90, "b")

    kd.insert(e1)
    kd.insert(e2)

    assert kd.nearest(Vector2(12, 12)) == e1
    assert kd.nearest(Vector2(99, 99)) == e2


def test_nearest_returns_none_when_empty(tree):
    assert tree.nearest(Vector2(50, 50)) is None
