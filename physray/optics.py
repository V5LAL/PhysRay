from __future__ import annotations
import math
from typing import Optional, Tuple
from .vector import Vec3


def reflect(incident: Vec3, normal: Vec3) -> Vec3:
    """
    Perfect specular reflection:
        R = I - 2(I·N)N
    """
    I = incident.normalized()
    N = normal.normalized()
    return (I - 2.0 * I.dot(N) * N).normalized()


def refract(
    incident: Vec3,
    normal: Vec3,
    n1: float,
    n2: float,
    eps: float = 1e-12
) -> Optional[Vec3]:
    """
    Vector Snell refraction.

    Convention:
      - incident points toward the interface
      - normal points against the incident ray
      - n1 is the refractive index of the incident medium
      - n2 is the refractive index of the transmitted medium

    Returns None for total internal reflection.
    """
    I = incident.normalized()
    N = normal.normalized()

    cos_i = max(-1.0, min(1.0, -I.dot(N)))
    eta = n1 / n2
    k = 1.0 - eta * eta * (1.0 - cos_i * cos_i)

    if k < -eps:
        return None

    k = max(0.0, k)
    T = eta * I + (eta * cos_i - math.sqrt(k)) * N
    return T.normalized()


def fresnel_dielectric(
    incident: Vec3,
    normal: Vec3,
    n1: float,
    n2: float
) -> Tuple[float, float, float]:
    """
    Exact Fresnel power reflectances for non-absorbing dielectrics.

    Returns:
        Rs, Rp, R_unpolarized

    Under total internal reflection, all are 1.
    """
    I = incident.normalized()
    N = normal.normalized()

    cos_i = max(-1.0, min(1.0, -I.dot(N)))
    sin_i2 = max(0.0, 1.0 - cos_i * cos_i)

    eta = n1 / n2
    sin_t2 = eta * eta * sin_i2

    if sin_t2 > 1.0:
        return 1.0, 1.0, 1.0

    cos_t = math.sqrt(max(0.0, 1.0 - sin_t2))

    rs = (n1 * cos_i - n2 * cos_t) / (n1 * cos_i + n2 * cos_t)
    rp = (n2 * cos_i - n1 * cos_t) / (n2 * cos_i + n1 * cos_t)

    Rs = rs * rs
    Rp = rp * rp
    return Rs, Rp, 0.5 * (Rs + Rp)


def critical_angle_deg(n_high: float, n_low: float) -> float:
    if n_high <= n_low:
        raise ValueError("Critical angle requires n_high > n_low.")
    return math.degrees(math.asin(n_low / n_high))


def brewster_angle_deg(n1: float, n2: float) -> float:
    return math.degrees(math.atan2(n2, n1))
