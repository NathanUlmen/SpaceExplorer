from pygame.math import Vector2


class AABB:
    def __init__(self, min: Vector2, max: Vector2):
        self.min = min
        self.max = max
        pass

    def contains(self, target: Vector2) -> bool:
        return (
                self.min.x <= target.x <= self.max.x and
                self.min.y <= target.y <= self.max.y
        )

    def intersects(self, other: "AABB") -> bool:
        return not (
                self.max.x < other.min.x or
                self.min.x > other.max.x or
                self.max.y < other.min.y or
                self.min.y > other.max.y
        )


class StagedCollection:
    def __init__(self):
        self.elements = []
        self.to_add = []
        self.to_remove = []

    def __len__(self):
        return len(self.elements)

    def flush(self):
        # Remove
        for element in self.to_remove:
            self.elements.remove(element)
        self.to_remove.clear()

        # Add
        self.elements += self.to_add
        self.to_add.clear()

    def stage_append(self, element):
        self.to_add.append(element)

    def stage_removal(self, element):
        self.to_remove.append(element)

    def __iter__(self):
        return iter(self.elements)


class KdTree:
    def __init__(self, bounds: AABB, max_capacity: int = 20, max_depth: int = 10, depth: int = 0):
        self.bounds = bounds
        self.max_capacity = max_capacity
        self.max_depth = max_depth
        self.depth = depth

    def insert(self, element) -> bool:
        raise NotImplementedError

    def remove(self, element) -> bool:
        raise NotImplementedError

    def query(self, param: Vector2 | AABB) -> list:
        raise NotImplementedError

    def nearest(self, target: Vector2):
        raise NotImplementedError

    def remove_nearest(self, target: Vector2):
        raise NotImplementedError


class QuadTree:
    def __init__(self, aabb: AABB, max_capacity: int = 20, max_depth: int = 10, depth: int = 0):
        self.aabb = aabb
        self.max_capacity = max_capacity
        self.max_depth = max_depth
        self.depth = depth
        self.children = None
        self.elements = []

    def __str__(self) -> str:
        return self._to_string()

    def _to_string(self, indent: int = 0) -> str:
        pad = "  " * indent
        s = (
            f"{pad}QuadTree(depth={self.depth}, "
            f"bounds=({self.aabb.min.x}, {self.aabb.min.y}) -> ({self.aabb.max.x}, {self.aabb.max.y}), "
            f"elements={len(self.elements)})"
        )
        if self.children:
            for child in self.children:
                s += "\n" + child._to_string(indent + 1)
        return s

    def insert(self, element) -> bool:
        assert (element and isinstance(element.pos, Vector2))
        if not self.aabb.contains(element.pos):
            return False

        if self.children is None:
            self.elements.append(element)
            if len(self.elements) > self.max_capacity:
                self._split()
            return True

        for child in self.children:
            if child.aabb.contains(element.pos):
                return child.insert(element)

        self.elements.append(element)
        return True

    def remove(self, element) -> bool:
        assert (element and isinstance(element.pos, Vector2))
        if not self.aabb.contains(element.pos):
            return False

        if element in self.elements:
            self.elements.remove(element)
            return True

        if self.children is None:
            return False

        for child in self.children:
            if child.remove(element):
                return True

        return False

    def query(self, param: Vector2 | AABB) -> list:
        if isinstance(param, Vector2):
            if not self.aabb.contains(param):
                return []

            to_return = []
            for element in self.elements:
                if param == element.pos:
                    to_return.append(element)

            if self.children:
                for child in self.children:
                    if child.aabb.contains(param):
                        to_return += child.query(param)
                        break
            return to_return
        elif isinstance(param, AABB):
            to_return = []
            if not self.aabb.intersects(param):
                return to_return

            # Base Case
            for element in self.elements:
                if param.contains(element.pos):
                    to_return.append(element)

            if self.children is None:
                return to_return

            for child in self.children:
                if child.aabb.intersects(param):
                    to_return += child.query(param)

            return to_return
        else:
            return []

    def _split(self) -> None:
        if self.depth >= self.max_depth:
            return

        center_x = (self.aabb.min.x + self.aabb.max.x) / 2
        center_y = (self.aabb.min.y + self.aabb.max.y) / 2

        self.children = [
            # Top Left
            QuadTree(AABB(Vector2(self.aabb.min.x, center_y), Vector2(center_x, self.aabb.max.y)),
                     self.max_capacity, self.max_depth, self.depth + 1),
            # Top Right
            QuadTree(AABB(Vector2(center_x, center_y), self.aabb.max.copy()),
                     self.max_capacity, self.max_depth, self.depth + 1),
            # Bottom Left
            QuadTree(AABB(self.aabb.min.copy(), Vector2(center_x, center_y)),
                     self.max_capacity, self.max_depth, self.depth + 1),
            # Bottom Right
            QuadTree(AABB(Vector2(center_x, self.aabb.min.y), Vector2(self.aabb.max.x, center_y)),
                     self.max_capacity, self.max_depth, self.depth + 1)
        ]

        to_insert = self.elements
        self.elements = []
        for element in to_insert:
            self.insert(element)
