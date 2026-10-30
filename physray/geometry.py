from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .vector import Vec3
from .ray import Ray
from .materials import Material

EPSILON = 1e-5


@dataclass
class Hit:
    t: float
    point: Vec3
    normal: Vec3
    front_face: bool
    material: Material

    @staticmethod
    def from_outward_normal(
        ray: Ray,
        t: float,
        point: Vec3,
        outward_normal: Vec3,
        material: Material
    ) -> "Hit":
        front = ray.direction.dot(outward_normal) < 0
        normal = outward_normal if front else -outward_normal
        return Hit(t, point, normal.normalized(), front, material)


@dataclass(frozen=True)
class Sphere:
    center: Vec3
    radius: float
    material: Material

    def intersect(self, ray: Ray) -> Optional[Hit]:
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        half_b = oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius

        disc = half_b * half_b - a * c
        if disc < 0:
            return None

        sqrt_d = disc ** 0.5
        roots = [(-half_b - sqrt_d) / a, (-half_b + sqrt_d) / a]

        for t in roots:
            if t > EPSILON:
                p = ray.at(t)
                outward = (p - self.center) / self.radius
                return Hit.from_outward_normal(
                    ray, t, p, outward, self.material
                )

        return None


@dataclass(frozen=True)
class Plane:
    point: Vec3
    normal: Vec3
    material: Material

    def intersect(self, ray: Ray) -> Optional[Hit]:
        N = self.normal.normalized()
        denom = N.dot(ray.direction)
        if abs(denom) < 1e-10:
            return None

        t = (self.point - ray.origin).dot(N) / denom
        if t <= EPSILON:
            return None

        p = ray.at(t)
        return Hit.from_outward_normal(ray, t, p, N, self.material)


class Scene:
    def __init__(self):
        self.objects = []

    def add(self, obj) -> None:
        self.objects.append(obj)

    def closest_hit(self, ray: Ray) -> Optional[Hit]:
        best = None
        best_t = float("inf")
        for obj in self.objects:
            hit = obj.intersect(ray)
            if hit is not None and hit.t < best_t:
                best = hit
                best_t = hit.t
        return best
