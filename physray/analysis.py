from __future__ import annotations
import math
import numpy as np
import matplotlib.pyplot as plt

from .vector import Vec3
from .ray import Ray
from .optics import fresnel_dielectric, brewster_angle_deg
from .materials import sellmeier_index, BK7_B, BK7_C
from .lens import ThickLens, axis_crossing_z, intersect_image_plane


def plot_fresnel_air_glass(filename: str, n2: float = 1.5):
    angles = np.linspace(0.0, 89.9, 900)
    Rs, Rp, Ru = [], [], []

    for deg in angles:
        th = math.radians(deg)
        I = Vec3(math.sin(th), 0, -math.cos(th))
        N = Vec3(0, 0, 1)
        rs, rp, r = fresnel_dielectric(I, N, 1.0, n2)
        Rs.append(rs)
        Rp.append(rp)
        Ru.append(r)

    plt.figure(figsize=(8, 5))
    plt.plot(angles, Rs, label="Rs (s-polarized)")
    plt.plot(angles, Rp, label="Rp (p-polarized)")
    plt.plot(angles, Ru, label="Unpolarized")
    plt.axvline(
        brewster_angle_deg(1.0, n2),
        linestyle="--",
        linewidth=1,
        label="Brewster angle"
    )
    plt.xlabel("Incidence angle (degrees)")
    plt.ylabel("Reflectance")
    plt.title(f"Exact Fresnel Reflectance: air → n={n2}")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=160)
    plt.close()


def plot_sellmeier_bk7(filename: str):
    wl = np.linspace(400, 700, 500)
    n = [sellmeier_index(x, BK7_B, BK7_C) for x in wl]

    plt.figure(figsize=(8, 5))
    plt.plot(wl, n)
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Refractive index n")
    plt.title("BK7 Sellmeier Dispersion")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=160)
    plt.close()


def paraxial_focus(lens: ThickLens, wavelength_nm: float) -> float:
    """
    Trace a very near-axis parallel ray and use its axis crossing
    as the paraxial focal position.
    """
    ray = Ray(Vec3(0.1, 0.0, -20.0), Vec3(0, 0, 1), wavelength_nm)
    out = lens.trace(ray)
    if out is None:
        raise RuntimeError("Near-axis ray failed to pass through lens.")
    z = axis_crossing_z(out)
    if z is None:
        raise RuntimeError("Could not find paraxial focus.")
    return z


def longitudinal_chromatic_aberration(
    lens: ThickLens,
    filename: str,
    wavelengths=(450, 486.1, 550, 587.6, 656.3)
):
    focuses = [paraxial_focus(lens, w) for w in wavelengths]

    plt.figure(figsize=(8, 5))
    plt.plot(wavelengths, focuses, marker="o")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Paraxial focus z (mm)")
    plt.title("Longitudinal Chromatic Aberration")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=160)
    plt.close()

    return dict(zip(wavelengths, focuses))


def generate_pupil_points(radius: float, rings: int = 7):
    pts = [(0.0, 0.0)]
    for ring in range(1, rings + 1):
        r = radius * ring / rings
        count = max(8, 8 * ring)
        for i in range(count):
            phi = 2 * math.pi * i / count
            pts.append((r * math.cos(phi), r * math.sin(phi)))
    return pts


def spot_diagram(
    lens: ThickLens,
    filename: str,
    image_plane_z: float,
    wavelengths=(486.1, 587.6, 656.3),
    field_angle_deg: float = 0.0,
    pupil_fraction: float = 0.95
):
    pupil = generate_pupil_points(
        lens.front.aperture_radius * pupil_fraction,
        rings=7
    )

    plt.figure(figsize=(6, 6))

    all_points = {}
    theta = math.radians(field_angle_deg)
    direction = Vec3(math.sin(theta), 0, math.cos(theta))

    for w in wavelengths:
        xs, ys = [], []

        for x0, y0 in pupil:
            ray = Ray(Vec3(x0, y0, -20.0), direction, w)
            out = lens.trace(ray)
            if out is None:
                continue
            p = intersect_image_plane(out, image_plane_z)
            if p is None:
                continue
            xs.append(p.x)
            ys.append(p.y)

        plt.scatter(xs, ys, s=8, label=f"{w:.1f} nm")
        all_points[w] = list(zip(xs, ys))

    plt.axhline(0, linewidth=0.5)
    plt.axvline(0, linewidth=0.5)
    plt.xlabel("Image-plane x (mm)")
    plt.ylabel("Image-plane y (mm)")
    plt.title(
        f"Spot Diagram at z={image_plane_z:.3f} mm, "
        f"field={field_angle_deg:.1f}°"
    )
    plt.axis("equal")
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=180)
    plt.close()

    return all_points
