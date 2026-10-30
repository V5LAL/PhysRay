from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Optional
from .vector import Vec3
from .ray import Ray
from .optics import refract


@dataclass(frozen=True)
class SphericalSurface:
    """
    Rotationally symmetric spherical optical surface.

    Sign convention:
      radius > 0 -> center of curvature lies to +z of the vertex
      radius < 0 -> center lies to -z of the vertex
    """
    vertex_z: float
    radius: float
    aperture_radius: float

    @property
    def center(self) -> Vec3:
        return Vec3(0.0, 0.0, self.vertex_z + self.radius)

    def intersect(self, ray: Ray):
        C = self.center
        oc = ray.origin - C
        a = ray.direction.dot(ray.direction)
        half_b = oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius

        disc = half_b * half_b - a * c
        if disc < 0:
            return None

        sqrt_d = math.sqrt(disc)
        roots = sorted([
            (-half_b - sqrt_d) / a,
            (-half_b + sqrt_d) / a
        ])

        for t in roots:
            if t <= 1e-8:
                continue

            p = ray.at(t)

            # Select the physical branch nearest the requested vertex.
            # This rejects the opposite side of the full mathematical sphere.
            if abs(p.z - self.vertex_z) > abs(self.radius) * 0.5:
                continue

            if p.x * p.x + p.y * p.y > self.aperture_radius ** 2:
                continue

            outward = (p - C).normalized()
            return p, outward

        return None


@dataclass(frozen=True)
class ThickLens:
    front: SphericalSurface
    back: SphericalSurface
    material: object

    def trace(self, ray: Ray) -> Optional[Ray]:
        # Front surface: air -> glass.
        h1 = self.front.intersect(ray)
        if h1 is None:
            return None
        p1, outward1 = h1
        N1 = outward1 if ray.direction.dot(outward1) < 0 else -outward1

        n_glass = self.material.n(ray.wavelength_nm)
        d1 = refract(ray.direction, N1, 1.0, n_glass)
        if d1 is None:
            return None

        inside = Ray(p1 + d1 * 1e-6, d1, ray.wavelength_nm)

        # Back surface: glass -> air.
        h2 = self.back.intersect(inside)
        if h2 is None:
            return None
        p2, outward2 = h2
        N2 = outward2 if inside.direction.dot(outward2) < 0 else -outward2

        d2 = refract(inside.direction, N2, n_glass, 1.0)
        if d2 is None:
            return None

        return Ray(p2 + d2 * 1e-6, d2, ray.wavelength_nm)


def axis_crossing_z(ray: Ray) -> Optional[float]:
    """
    Estimate z at which a meridional ray crosses the optical axis.
    Uses x if available, otherwise y.
    """
    if abs(ray.direction.x) > 1e-12:
        t = -ray.origin.x / ray.direction.x
    elif abs(ray.direction.y) > 1e-12:
        t = -ray.origin.y / ray.direction.y
    else:
        return None

    if t <= 0:
        return None
    return ray.origin.z + t * ray.direction.z


def intersect_image_plane(ray: Ray, z_plane: float):
    if abs(ray.direction.z) < 1e-12:
        return None
    t = (z_plane - ray.origin.z) / ray.direction.z
    if t <= 0:
        return None
    return ray.at(t)
