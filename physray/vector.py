from __future__ import annotations
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Vec3:
    """Small 3-D vector class used throughout the project."""
    x: float
    y: float
    z: float

    def __add__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, value) -> "Vec3":
        if isinstance(value, Vec3):
            return Vec3(self.x * value.x, self.y * value.y, self.z * value.z)
        return Vec3(self.x * value, self.y * value, self.z * value)

    def __rmul__(self, value: float) -> "Vec3":
        return self * value

    def __truediv__(self, value: float) -> "Vec3":
        return Vec3(self.x / value, self.y / value, self.z / value)

    def __neg__(self) -> "Vec3":
        return Vec3(-self.x, -self.y, -self.z)

    def dot(self, other: "Vec3") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "Vec3") -> "Vec3":
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def length_squared(self) -> float:
        return self.dot(self)

    def length(self) -> float:
        return math.sqrt(self.length_squared())

    def normalized(self) -> "Vec3":
        L = self.length()
        if L == 0:
            raise ValueError("Cannot normalize the zero vector.")
        return self / L

    def clamp(self, lo: float = 0.0, hi: float = 1.0) -> "Vec3":
        return Vec3(
            min(hi, max(lo, self.x)),
            min(hi, max(lo, self.y)),
            min(hi, max(lo, self.z)),
        )
