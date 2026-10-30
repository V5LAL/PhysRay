# PhysRay — Phase 1 in Python

A beginner-friendly implementation of Phase 1 of the **Physically-Based Ray
Tracer: Theoretical Foundations and Solid-State Optical Extension** project.

Phase 1 corresponds to milestones **M0–M4**:

| Milestone | What this project implements |
|---|---|
| M0 | Vector math, rays, sphere/plane intersections, camera, diffuse and mirror rendering |
| M1 | Vector Snell refraction, entering/exiting-medium logic, total internal reflection |
| M2 | Exact s/p Fresnel dielectric reflectance and recursive reflected/transmitted rays |
| M3 | Sellmeier wavelength-dependent refractive index and multi-wavelength tracing |
| M4 | Thick-lens ray bundles, chromatic focal shift and spot diagrams |

---

# 1. What you need

You need **Python 3.11 or newer**.

You do **not** need Visual Studio or a C++ compiler for this version.

Install Python from:

    https://www.python.org/downloads/

On Windows, during installation, enable:

    Add python.exe to PATH

---

# 2. Open the project

Extract the ZIP, for example to:

    C:\physray_phase1_python

Open Command Prompt and enter:

    cd C:\physray_phase1_python

Check Python:

    python --version

If `python` does not work, try:

    py --version

If `py` works, use `py` instead of `python` in every command below.

---

# 3. Install the three Python packages

Run:

    python -m pip install -r requirements.txt

This installs:

- NumPy — image arrays / numerical work
- Matplotlib — scientific plots and spot diagrams
- Pillow — PNG output

---

# 4. Run the automated physics tests FIRST

Run:

    python -m unittest tests.test_phase1 -v

You should see tests covering:

- vector mathematics
- sphere intersection
- mirror reflection
- Snell refraction
- total internal reflection
- critical angle
- Fresnel reflectance at normal incidence
- Brewster-angle extinction of p reflection
- BK7 Sellmeier dispersion
- thick-lens focal behavior
- chromatic focal shift

The final line should say:

    OK

If it does, the mathematical core is behaving as expected.

---

# 5. Run all Phase 1 demos

Run:

    python demos\run_all.py

On macOS/Linux use:

    python demos/run_all.py

The program creates files in:

    results\

including:

    m0_m2_renderer.png
    m2_fresnel_air_glass.png
    m3_bk7_sellmeier.png
    m3_spectral_renderer.png
    m4_longitudinal_chromatic_aberration.png
    m4_spot_diagram_on_axis.png
    m4_spot_diagram_3deg_field.png

The rendering demos may take a little while because they deliberately trace rays
in plain Python so the implementation remains readable.

---

# 6. What each milestone means

## M0 — Core geometric tracer

The computer learns:

1. a ray has an origin and direction,
2. a ray can hit a sphere or plane,
3. the hit point has a surface normal,
4. the camera generates one primary ray per pixel,
5. diffuse surfaces respond to a light direction,
6. mirror surfaces spawn reflected secondary rays.

Main files:

    physray/vector.py
    physray/ray.py
    physray/geometry.py
    physray/camera.py
    physray/renderer.py

---

## M1 — Snell refraction

The project implements vector Snell refraction:

    n1 sin(theta1) = n2 sin(theta2)

The implementation does not need to explicitly convert vectors into angles.

It also detects total internal reflection. In that case the refract function
returns `None` and the renderer follows the reflected path.

Main file:

    physray/optics.py

Important tests:

    test_snell_normal_incidence
    test_snell_air_to_glass_30deg
    test_total_internal_reflection
    test_critical_angle

---

## M2 — Exact Fresnel equations

For a non-absorbing dielectric interface, the renderer computes:

    Rs
    Rp
    R = (Rs + Rp) / 2

It then recursively evaluates reflected and transmitted rays and combines them
using the exact unpolarized Fresnel reflectance.

Main file:

    physray/optics.py

Validation output:

    results/m2_fresnel_air_glass.png

The p-polarized curve should fall to essentially zero at Brewster's angle.

---

## M3 — Sellmeier dispersion

BK7 glass no longer uses one fixed refractive index.

Instead:

    wavelength -> Sellmeier equation -> n(wavelength)

Blue light obtains a slightly higher refractive index than red light.

Main file:

    physray/materials.py

Validation output:

    results/m3_bk7_sellmeier.png

The project also includes a simple multi-wavelength renderer:

    results/m3_spectral_renderer.png

Important limitation:
the wavelength-to-RGB conversion is intentionally a simple educational display
mapping, not yet a rigorous CIE colorimetric pipeline. The whitepaper lists a
CIE-based spectral-to-color pass as the eventual architecture, so this is one
place worth upgrading later.

---

## M4 — Aberration analysis

A separate optical-analysis mode traces parallel ray bundles through a thick
BK7 biconvex lens.

The demo lens uses:

    R1 = +50 mm
    R2 = -50 mm
    centre thickness = 5 mm
    aperture radius = 10 mm

It calculates:

1. paraxial focal position,
2. focal position versus wavelength,
3. an on-axis spot diagram,
4. a 3-degree field-angle spot diagram.

Main files:

    physray/lens.py
    physray/analysis.py

Outputs:

    results/m4_longitudinal_chromatic_aberration.png
    results/m4_spot_diagram_on_axis.png
    results/m4_spot_diagram_3deg_field.png

---

# 7. Recommended order for YOU to study the code

Do not try to understand everything simultaneously.

Study in this order:

1. `physray/vector.py`
2. `physray/ray.py`
3. `physray/geometry.py`
4. `physray/camera.py`
5. the M0 parts of `physray/renderer.py`
6. `reflect()` in `physray/optics.py`
7. `refract()` in `physray/optics.py`
8. Snell tests in `tests/test_phase1.py`
9. `fresnel_dielectric()`
10. Fresnel tests
11. `sellmeier_index()`
12. Sellmeier tests
13. `physray/lens.py`
14. M4 functions in `physray/analysis.py`

A good rule is:

    equation -> small function -> automated test -> visual demonstration

---

# 8. First modifications to try yourself

### Experiment A — move a sphere

Open:

    demos/run_all.py

Change:

    Vec3(-0.95, 0.0, -3.5)

to:

    Vec3(-1.30, 0.30, -3.5)

Run the demos again.

### Experiment B — change glass curvature

Change the M4 lens:

    radius=50.0

to:

    radius=40.0

and the other radius:

    radius=-50.0

to:

    radius=-40.0

Re-run the program and compare the focal position and spot diagram.

### Experiment C — change aperture

Change:

    aperture_radius=10.0

to:

    aperture_radius=5.0

You should generally see the outer spherical-aberration contribution shrink.

---

# 9. Important scientific limitations of this Phase 1 implementation

This is a learning/portfolio implementation, not Zemax/Code V.

Current simplifications include:

- isotropic, homogeneous materials,
- non-absorbing dielectrics in Fresnel,
- air treated as n = 1,
- no nested-medium stack,
- no polarization state carried along each ray,
- simple direct illumination for diffuse rendering,
- no Monte Carlo path tracing,
- approximate wavelength-to-RGB display conversion,
- M4 uses spherical refracting surfaces only,
- no diffraction or wavefront propagation,
- no MTF calculation yet.

Those limitations are useful to document rather than hide.

---

# 10. What Phase 2 would add

Phase 2 can later extend the same architecture with:

- complex refractive index n + ik,
- Beer–Lambert absorption,
- Drude metal/free-carrier response,
- Tauc semiconductor absorption edge,
- Kramers–Kronig checks,
- thin-film transfer matrices.

But do not start Phase 2 until you can explain and validate Phase 1.
