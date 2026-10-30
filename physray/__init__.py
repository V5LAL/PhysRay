"""
PhysRay Phase 1 — educational physically-based ray tracer and optics analysis.
"""
from .vector import Vec3
from .ray import Ray
from .optics import reflect, refract, fresnel_dielectric
from .materials import (
    Material, Diffuse, Mirror, DielectricConstant, DielectricSellmeier,
    BK7_B, BK7_C
)
from .geometry import Sphere, Plane, Scene
from .camera import Camera
