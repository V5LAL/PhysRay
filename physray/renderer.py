from __future__ import annotations
import numpy as np
from PIL import Image

from .vector import Vec3
from .ray import Ray
from .geometry import Scene
from .materials import Diffuse, Mirror, DielectricConstant, DielectricSellmeier
from .optics import reflect, refract, fresnel_dielectric
from .color import wavelength_to_rgb

EPS = 1e-4
MAX_DEPTH = 8
LIGHT_DIR = Vec3(-0.6, 1.0, -0.5).normalized()


def background(ray: Ray) -> Vec3:
    t = 0.5 * (ray.direction.y + 1.0)
    return Vec3(0.88, 0.93, 1.0) * (1 - t) + Vec3(0.40, 0.62, 0.92) * t


def trace_ray(ray: Ray, scene: Scene, depth: int = 0) -> Vec3:
    if depth >= MAX_DEPTH:
        return Vec3(0, 0, 0)

    hit = scene.closest_hit(ray)
    if hit is None:
        return background(ray)

    mat = hit.material

    if isinstance(mat, Diffuse):
        ndotl = max(0.0, hit.normal.dot(LIGHT_DIR))
        return mat.color * (0.12 + 0.88 * ndotl)

    if isinstance(mat, Mirror):
        d = reflect(ray.direction, hit.normal)
        new_ray = Ray(hit.point + hit.normal * EPS, d, ray.wavelength_nm)
        return trace_ray(new_ray, scene, depth + 1) * mat.tint

    if isinstance(mat, (DielectricConstant, DielectricSellmeier)):
        n_mat = mat.n(ray.wavelength_nm)

        if hit.front_face:
            n1, n2 = 1.0, n_mat
        else:
            n1, n2 = n_mat, 1.0

        Rs, Rp, R = fresnel_dielectric(ray.direction, hit.normal, n1, n2)

        reflected_dir = reflect(ray.direction, hit.normal)
        reflected_ray = Ray(
            hit.point + hit.normal * EPS,
            reflected_dir,
            ray.wavelength_nm
        )
        reflected_color = trace_ray(reflected_ray, scene, depth + 1)

        transmitted_dir = refract(ray.direction, hit.normal, n1, n2)

        if transmitted_dir is None:
            return reflected_color

        # Offset transmission to the opposite side of the oriented normal.
        transmitted_ray = Ray(
            hit.point - hit.normal * EPS,
            transmitted_dir,
            ray.wavelength_nm
        )
        transmitted_color = trace_ray(transmitted_ray, scene, depth + 1)

        return reflected_color * R + transmitted_color * (1.0 - R)

    return Vec3(1.0, 0.0, 1.0)


def _to_uint8(v: Vec3):
    c = v.clamp()
    # Gamma ~2.0
    r = int(255 * (c.x ** 0.5))
    g = int(255 * (c.y ** 0.5))
    b = int(255 * (c.z ** 0.5))
    return r, g, b


def render_rgb(scene: Scene, camera, filename: str):
    img = np.zeros((camera.height, camera.width, 3), dtype=np.uint8)

    for y in range(camera.height):
        if y % max(1, camera.height // 10) == 0:
            print(f"RGB render: row {y+1}/{camera.height}")
        for x in range(camera.width):
            ray = camera.ray_for_pixel(x, y, 550.0)
            img[y, x] = _to_uint8(trace_ray(ray, scene))

    Image.fromarray(img, "RGB").save(filename)
    print("Saved:", filename)


def render_spectral(scene: Scene, camera, filename: str, wavelengths=None):
    """
    Educational multi-wavelength renderer.

    Each sampled wavelength is traced independently, then mapped approximately
    into display RGB and accumulated.
    """
    if wavelengths is None:
        wavelengths = [420, 460, 500, 540, 580, 620, 660]

    accum = np.zeros((camera.height, camera.width, 3), dtype=float)

    for wi, wavelength in enumerate(wavelengths):
        print(f"Spectral pass {wi+1}/{len(wavelengths)}: {wavelength} nm")
        basis = wavelength_to_rgb(wavelength)

        for y in range(camera.height):
            for x in range(camera.width):
                ray = camera.ray_for_pixel(x, y, wavelength)
                scalar_color = trace_ray(ray, scene)

                # Treat scene radiance as a broadband intensity estimate and
                # weight it by the selected wavelength's display basis.
                intensity = (
                    scalar_color.x + scalar_color.y + scalar_color.z
                ) / 3.0

                accum[y, x, 0] += intensity * basis.x
                accum[y, x, 1] += intensity * basis.y
                accum[y, x, 2] += intensity * basis.z

    # Normalize robustly for display.
    p = np.percentile(accum, 99.5)
    if p > 0:
        accum /= p
    accum = np.clip(accum, 0, 1)
    accum = np.sqrt(accum)
    img = (255 * accum).astype(np.uint8)

    Image.fromarray(img, "RGB").save(filename)
    print("Saved:", filename)
