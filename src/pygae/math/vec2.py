from __future__ import annotations
import math
from collections.abc import Sequence
from typing import NamedTuple


class Vec2(NamedTuple):
    """
    Immutable 2D vector class supporting common vector operations.

    Attributes:
        x (float): X component of the vector.
        y (float): Y component of the vector.
    """

    x: float
    y: float

    @staticmethod
    def as_vec2(o: Vec2Like) -> Vec2:
        """Convert a Vec2-like object to a Vec2 instance.

        Args:
            o (Vec2Like): An object that can be interpreted as a 2D vector.

        Returns:
            Vec2: A Vec2 instance representing the same vector.
        """
        if isinstance(o, Vec2):
            return o
        else:
            x, y = o
            return Vec2(x, y)

    @staticmethod
    def _coerce(o: Vec2Like) -> tuple[float, float]:
        """Coerce a Vec2-like object to a tuple of floats (x, y).

        Args:
            o (Vec2Like): An object that can be interpreted as a 2D vector.

        Returns:
            tuple[float, float]: The (x, y) components as floats.

        Raises:
            NotImplementedError: If the object cannot be unpacked as (x, y).
        """
        try:
            x, y = o
            return float(x), float(y)
        except TypeError:
            raise NotImplementedError(f"Cannot unpack (x, y) from type {type(o)}")

    def __repr__(self) -> str:
        """Return a concise string representation of the vector.

        Returns:
            str: A string representation of the Vec2.
        """
        return f"Vec2(x={self.x:.3f}, y={self.y:.3f})"

    def __eq__(self, o: Vec2Like) -> bool:  # type: ignore[override]
        """Check equality with another Vec2-like object.

        Args:
            o (Vec2Like): Vector to compare with.

        Returns:
            bool: True if vectors are equal, False otherwise.
        """
        x, y = Vec2._coerce(o)
        return self.x == x and self.y == y

    def __add__(self, o: Vec2Like) -> Vec2:  # type: ignore[override]
        """Vector addition (self + o).

        Args:
            o (Vec2Like): Vector to add.

        Returns:
            Vec2: Resulting vector.
        """
        x, y = Vec2._coerce(o)
        return Vec2(self.x + x, self.y + y)

    def __radd__(self, o: Vec2Like) -> Vec2:
        """Right-hand addition (o + self).

        Args:
            o (Vec2Like): Vector to add.

        Returns:
            Vec2: Resulting vector.
        """
        return self.__add__(o)

    def __sub__(self, o: Vec2Like) -> Vec2:
        """Vector subtraction (self - o).

        Args:
            o (Vec2Like): Vector to subtract.

        Returns:
            Vec2: Resulting vector.
        """
        x, y = Vec2._coerce(o)
        return Vec2(self.x - x, self.y - y)

    def __rsub__(self, o: Vec2Like) -> Vec2:
        """Right-hand subtraction (o - self).

        Args:
            o (Vec2Like): Vector to subtract.

        Returns:
            Vec2: Resulting vector.
        """
        x, y = Vec2._coerce(o)
        return Vec2(x - self.x, y - self.y)

    def __mul__(self, o: Vec2Like | float) -> Vec2:  # type: ignore[override]
        """Multiply by a scalar or component-wise (Hadamard) product (self * o).

        Args:
            o (Vec2Like | float): Scalar or vector to multiply with.

        Returns:
            Vec2: Resulting vector.
        """
        if isinstance(o, (float, int)):
            s = float(o)
            return Vec2(self.x * s, self.y * s)
        # Hadamard product
        x, y = Vec2._coerce(o)
        return Vec2(self.x * x, self.y * y)

    def __rmul__(self, o: Vec2Like | float) -> Vec2:  # type: ignore[override]
        """Right-hand multiplication (o * self).

        Args:
            o (Vec2Like | float): Scalar or vector to multiply with.

        Returns:
            Vec2: Resulting vector.
        """
        return self.__mul__(o)

    def dot(self, o: Vec2Like) -> float:
        """Compute the dot product with another Vec2-like object.

        Args:
            o (Vec2Like): Vector to compute dot product with.

        Returns:
            float: The dot product.
        """
        x, y = Vec2._coerce(o)
        return (self.x * x) + (self.y * y)

    def cross(self, o: Vec2Like) -> float:
        """Compute the 2D cross product (scalar) with another Vec2-like object.

        Args:
            o (Vec2Like): Vector to compute cross product with.

        Returns:
            float: The scalar cross product.
        """
        x, y = Vec2._coerce(o)
        return (self.x * y) - (self.y * x)

    def magnitude(self) -> float:
        """Return the Euclidean length of the vector.

        Returns:
            float: Magnitude of the vector.
        """
        return math.hypot(self.x, self.y)

    def normalized(self) -> Vec2:
        """Return a unit vector in the same direction as this vector.

        Returns:
            Vec2: Normalized vector of length 1.
        """
        mag = self.magnitude()
        return Vec2(self.x / mag, self.y / mag)

    def lerp(self, o: Vec2Like, a: float) -> Vec2:
        """Linearly interpolate between this vector and another vector.

        Args:
            o (Vec2Like): Target vector.
            a (float): Interpolation factor between 0 and 1.

        Returns:
            Vec2: Interpolated vector.
        """
        x, y = Vec2._coerce(o)
        return Vec2(self.x + (x - self.x) * a, self.y + (y - self.y) * a)

    def rotate(self, r: float) -> Vec2:
        """Rotate the vector by r radians counter-clockwise.

        Args:
            r (float): Rotation angle in radians.

        Returns:
            Vec2: Rotated vector.
        """
        cos_a = math.cos(r)
        sin_a = math.sin(r)
        return Vec2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.x * cos_a,
        )

    def reflect(self, o: Vec2Like) -> Vec2:
        """Reflect this vector across a normal.

        Args:
            o (Vec2Like): Normal vector (will be normalized internally).

        Returns:
            Vec2: Reflected vector.
        """
        n = Vec2.as_vec2(o).normalized()
        dot = self.dot(n)
        return Vec2(self.x - 2 * dot * n.x, self.y - 2 * dot * n.y)

    def distance_sq(self, o: Vec2Like) -> float:
        """Compute squared distance to another vector.

        Args:
            o (Vec2Like): Target vector.

        Returns:
            float: Squared distance.
        """
        x, y = Vec2._coerce(o)
        dx = self.x - x
        dy = self.y - y
        return dx**2 + dy**2

    def distance(self, o: Vec2Like) -> float:
        """Compute Euclidean distance to another vector.

        Args:
            o (Vec2Like): Target vector.

        Returns:
            float: Distance.
        """
        return math.sqrt(self.distance_sq(o))

    def perpl(self) -> Vec2:
        """Return the vector rotated 90° counter-clockwise (left perpendicular).

        Returns:
            Vec2: Perpendicular vector to the left.
        """
        return Vec2(-self.y, self.x)

    def perpr(self) -> Vec2:
        """Return the vector rotated 90° clockwise (right perpendicular).

        Returns:
            Vec2: Perpendicular vector to the right.
        """
        return Vec2(self.y, -self.x)

    def project(self, o: Vec2Like) -> Vec2:
        """Project this vector onto another vector.

        Args:
            o (Vec2Like): Target vector to project onto.

        Returns:
            Vec2: Component of this vector along the target vector.
        """
        n = Vec2.as_vec2(o).normalized()
        s = self.dot(n)
        return Vec2(n.x * s, n.y * s)

    def snap(self, s: float = 1.0) -> Vec2:
        """Snap the vector to a grid of size `s`.

        Args:
            s (float): Grid spacing. Defaults to 1.0.

        Returns:
            Vec2: Snapped vector.
        """
        return Vec2(
            math.floor(self.x / s) * s,
            math.floor(self.y / s) * s,
        )

    ## TODO: angle_to(self, o: Vec2Like) -> float: # Compute the angle of self to o
    ## TODO: clamp(self) -> Vec2: # keeps a vector within a specified magnitude.
    ## TODO: .zero(), .one(), .from_angle(theta)
    ## TODO: Consider __lt__, __le__, ... based on magnitude
    ## TODO: .xx, .yy, .xy, .yx


Vec2Like = Sequence[float] | Vec2
