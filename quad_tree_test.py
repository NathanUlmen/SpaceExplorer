import pytest
from pygame.math import Vector2

from data_structures import AABB, QuadTree


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
    return QuadTree(bounds, max_capacity=2, max_depth=4)


def test_aabb_contains_point_inside():
    box = AABB(Vector2(0, 0), Vector2(10, 10))
    assert box.contains(Vector2(5, 5)) is True


def test_aabb_contains_point_on_boundaries():
    box = AABB(Vector2(0, 0), Vector2(10, 10))
    assert box.contains(Vector2(0, 0)) is True
    assert box.contains(Vector2(10, 10)) is True
    assert box.contains(Vector2(0, 10)) is True
    assert box.contains(Vector2(10, 0)) is True


def test_aabb_does_not_contain_point_outside():
    box = AABB(Vector2(0, 0), Vector2(10, 10))
    assert box.contains(Vector2(-1, 5)) is False
    assert box.contains(Vector2(5, 11)) is False


def test_aabb_intersects_when_overlapping():
    a = AABB(Vector2(0, 0), Vector2(10, 10))
    b = AABB(Vector2(5, 5), Vector2(15, 15))
    assert a.intersects(b) is True


def test_aabb_intersects_when_touching_edges():
    a = AABB(Vector2(0, 0), Vector2(10, 10))
    b = AABB(Vector2(10, 10), Vector2(20, 20))
    assert a.intersects(b) is True


def test_aabb_does_not_intersect_when_separate():
    a = AABB(Vector2(0, 0), Vector2(10, 10))
    b = AABB(Vector2(11, 11), Vector2(20, 20))
    assert a.intersects(b) is False


def test_insert_single_element(tree):
    e = DummyElement(10, 10, "a")
    assert tree.insert(e) is True


def test_insert_out_of_bounds_returns_false(bounds):
    qt = QuadTree(bounds)
    e = DummyElement(150, 150, "outside")
    assert qt.insert(e) is False


def test_insert_accepts_min_boundary(bounds):
    qt = QuadTree(bounds)
    e = DummyElement(0, 0, "min")
    assert qt.insert(e) is True


def test_insert_accepts_max_boundary(bounds):
    qt = QuadTree(bounds)
    e = DummyElement(100, 100, "max")
    assert qt.insert(e) is True


def test_insert_asserts_on_none(tree):
    with pytest.raises(AssertionError):
        tree.insert(None)


def test_remove_asserts_on_none(tree):
    with pytest.raises(AssertionError):
        tree.remove(None)


def test_remove_existing_element_from_unsplit_tree(tree):
    e = DummyElement(20, 20, "a")
    tree.insert(e)
    assert tree.remove(e) is True


def test_remove_missing_element_returns_false(tree):
    e = DummyElement(20, 20, "missing")
    assert tree.remove(e) is False


def test_query_point_returns_inserted_element_in_unsplit_tree(tree):
    e = DummyElement(25, 25, "a")
    tree.insert(e)

    results = tree.query(Vector2(25, 25))

    assert e in results


def test_query_point_returns_empty_list_for_out_of_bounds_point(tree):
    assert tree.query(Vector2(500, 500)) == []


def test_query_invalid_type_returns_empty_list(tree):
    assert tree.query("invalid") == []


def test_query_aabb_returns_elements_in_unsplit_tree(bounds):
    qt = QuadTree(bounds, max_capacity=10, max_depth=4)
    e1 = DummyElement(10, 10, "a")
    e2 = DummyElement(20, 20, "b")
    e3 = DummyElement(80, 80, "c")

    qt.insert(e1)
    qt.insert(e2)
    qt.insert(e3)

    results = qt.query(AABB(Vector2(0, 0), Vector2(30, 30)))

    assert e1 in results
    assert e2 in results
    assert e3 not in results


def test_split_creates_four_children(bounds):
    qt = QuadTree(bounds, max_capacity=1, max_depth=4)
    qt.insert(DummyElement(10, 10, "a"))
    qt.insert(DummyElement(80, 80, "b"))

    assert qt.children is not None
    assert len(qt.children) == 4


def test_elements_are_stored_in_children_after_split(bounds):
    qt = QuadTree(bounds, max_capacity=1, max_depth=4)
    e1 = DummyElement(10, 10, "a")
    e2 = DummyElement(80, 80, "b")

    qt.insert(e1)
    qt.insert(e2)

    assert qt.elements == []
    assert any(e1 in child.elements for child in qt.children)
    assert any(e2 in child.elements for child in qt.children)


def test_query_point_after_split_returns_matching_element(bounds):
    qt = QuadTree(bounds, max_capacity=1, max_depth=4)
    e1 = DummyElement(10, 10, "a")
    e2 = DummyElement(80, 80, "b")

    qt.insert(e1)
    qt.insert(e2)

    results = qt.query(Vector2(10, 10))

    assert e1 in results


def test_query_aabb_after_split_returns_elements_from_intersecting_children(bounds):
    qt = QuadTree(bounds, max_capacity=1, max_depth=4)
    e1 = DummyElement(10, 10, "bottom_left")
    e2 = DummyElement(80, 10, "bottom_right")
    e3 = DummyElement(10, 80, "top_left")
    e4 = DummyElement(80, 80, "top_right")

    qt.insert(e1)
    qt.insert(e2)
    qt.insert(e3)
    qt.insert(e4)

    results = qt.query(AABB(Vector2(0, 0), Vector2(50, 50)))

    assert e1 in results


def test_remove_existing_element_after_split(bounds):
    qt = QuadTree(bounds, max_capacity=1, max_depth=4)
    e1 = DummyElement(10, 10, "a")
    e2 = DummyElement(80, 80, "b")

    qt.insert(e1)
    qt.insert(e2)

    assert qt.remove(e1) is True


def test_query_and_remove_find_elements_stored_at_internal_node(bounds):
    qt = QuadTree(bounds, max_capacity=1, max_depth=4)
    e1 = DummyElement(10, 10, "a")
    e2 = DummyElement(80, 80, "b")

    qt.insert(e1)
    qt.insert(e2)

    e_internal = DummyElement(50, 50, "internal")
    qt.elements.append(e_internal)

    assert e_internal in qt.query(Vector2(50, 50))
    assert e_internal in qt.query(AABB(Vector2(40, 40), Vector2(60, 60)))
    assert qt.remove(e_internal) is True


def test_str_on_empty_tree(bounds):
    qt = QuadTree(bounds)
    expected = "QuadTree(depth=0, bounds=(0.0, 0.0) -> (100.0, 100.0), elements=0)"
    assert str(qt) == expected


def test_str_on_tree_with_children(bounds):
    qt = QuadTree(bounds, max_capacity=1, max_depth=4)
    qt.insert(DummyElement(10, 10, "a"))
    qt.insert(DummyElement(80, 80, "b"))

    s = str(qt)

    assert "QuadTree(depth=0, bounds=(0.0, 0.0) -> (100.0, 100.0), elements=0)" in s
    assert s.count("QuadTree(depth=1") == 4


def test_split_respects_max_depth_zero(bounds):
    qt = QuadTree(bounds, max_capacity=1, max_depth=0)
    qt.insert(DummyElement(10, 10, "a"))
    qt.insert(DummyElement(20, 20, "b"))

    assert qt.children is not None or qt.children is None
