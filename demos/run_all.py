from pathlib import Path

from physray.vector import Vec3
from physray.materials import Diffuse, Mirror, bk7
from physray.geometry import Sphere, Plane, Scene
from physray.camera import Camera
from physray.renderer import render_rgb, render_spectral
from physray.analysis import (
    plot_fresnel_air_glass,
    plot_sellmeier_bk7,
    longitudinal_chromatic_aberration,
    spot_diagram,
    paraxial_focus,
)
from physray.lens import SphericalSurface, ThickLens


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)


def build_scene():
    scene = Scene()

    scene.add(
        Sphere(
            Vec3(-0.95, 0.0, -3.5),
            0.72,
            Diffuse("red diffuse", Vec3(0.85, 0.18, 0.16)),
        )
    )

    scene.add(
        Sphere(
            Vec3(0.95, 0.0, -3.25),
            0.72,
            Mirror("mirror", Vec3(0.95, 0.98, 1.0)),
        )
    )

    # BK7 glass sphere exercises M1, M2 and M3.
    scene.add(
        Sphere(
            Vec3(0.0, 0.75, -4.25),
            0.58,
            bk7(),
        )
    )

    scene.add(
        Plane(
            Vec3(0, -0.75, 0),
            Vec3(0, 1, 0),
            Diffuse("ground", Vec3(0.68, 0.70, 0.72)),
        )
    )

    return scene


def build_demo_lens():
    # Symmetric BK7 biconvex lens, millimetre units.
    front = SphericalSurface(
        vertex_z=0.0,
        radius=50.0,
        aperture_radius=10.0
    )
    back = SphericalSurface(
        vertex_z=5.0,
        radius=-50.0,
        aperture_radius=10.0
    )
    return ThickLens(front, back, bk7())


def main():
    print("=== PhysRay Phase 1 demo ===")

    scene = build_scene()
    camera = Camera(
        position=Vec3(0, 0.15, 0.75),
        width=320,
        height=180,
        vertical_fov_deg=55,
    )

    print("\nM0–M2 render...")
    render_rgb(
        scene,
        camera,
        str(RESULTS / "m0_m2_renderer.png")
    )

    print("\nM3 multi-wavelength render...")
    render_spectral(
        scene,
        camera,
        str(RESULTS / "m3_spectral_renderer.png"),
        wavelengths=[420, 460, 500, 540, 580, 620, 660],
    )

    print("\nM2 Fresnel validation plot...")
    plot_fresnel_air_glass(
        str(RESULTS / "m2_fresnel_air_glass.png"),
        n2=1.5
    )

    print("\nM3 Sellmeier validation plot...")
    plot_sellmeier_bk7(
        str(RESULTS / "m3_bk7_sellmeier.png")
    )

    print("\nM4 aberration analysis...")
    lens = build_demo_lens()

    focuses = longitudinal_chromatic_aberration(
        lens,
        str(RESULTS / "m4_longitudinal_chromatic_aberration.png")
    )
    print("Chromatic focal positions (mm):")
    for w, z in focuses.items():
        print(f"  {w:6.1f} nm -> z = {z:.6f} mm")

    green_focus = paraxial_focus(lens, 587.6)
    print(f"Green reference image plane: {green_focus:.6f} mm")

    spot_diagram(
        lens,
        str(RESULTS / "m4_spot_diagram_on_axis.png"),
        image_plane_z=green_focus,
        field_angle_deg=0.0
    )

    spot_diagram(
        lens,
        str(RESULTS / "m4_spot_diagram_3deg_field.png"),
        image_plane_z=green_focus,
        field_angle_deg=3.0
    )

    print("\nAll Phase 1 demos completed.")
    print("Open the 'results' folder to inspect the outputs.")


if __name__ == "__main__":
    main()
