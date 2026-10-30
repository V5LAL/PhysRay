import math
import unittest

from physray.vector import Vec3
from physray.ray import Ray
from physray.optics import (
    reflect, refract, fresnel_dielectric,
    critical_angle_deg, brewster_angle_deg
)
from physray.materials import sellmeier_index, BK7_B, BK7_C, bk7
from physray.geometry import Sphere
from physray.materials import Diffuse
from physray.lens import SphericalSurface, ThickLens
from physray.analysis import paraxial_focus


class Phase1Tests(unittest.TestCase):
    def assertVecNear(self, a, b, tol=1e-9):
        self.assertLess((a - b).length(), tol)

    # M0
    def test_vec3(self):
        a = Vec3(1, 2, 3)
        b = Vec3(4, 5, 6)
        self.assertEqual(a + b, Vec3(5, 7, 9))
        self.assertAlmostEqual(a.dot(b), 32.0)

    def test_sphere_intersection(self):
        sphere = Sphere(
            Vec3(0, 0, -3),
            1.0,
            Diffuse("test", Vec3(1, 0, 0))
        )
        ray = Ray(Vec3(0, 0, 0), Vec3(0, 0, -1))
        hit = sphere.intersect(ray)
        self.assertIsNotNone(hit)
        self.assertAlmostEqual(hit.t, 2.0, places=10)

    def test_reflection(self):
        I = Vec3(1, -1, 0)
        N = Vec3(0, 1, 0)
        R = reflect(I, N)
        self.assertVecNear(R, Vec3(1, 1, 0).normalized())

    # M1
    def test_snell_normal_incidence(self):
        I = Vec3(0, 0, -1)
        N = Vec3(0, 0, 1)
        T = refract(I, N, 1.0, 1.5)
        self.assertVecNear(T, I)

    def test_snell_air_to_glass_30deg(self):
        theta_i = math.radians(30)
        I = Vec3(math.sin(theta_i), 0, -math.cos(theta_i))
        N = Vec3(0, 0, 1)
        T = refract(I, N, 1.0, 1.5)
        self.assertIsNotNone(T)
        theta_t = math.degrees(math.acos(-T.dot(N)))
        expected = math.degrees(math.asin(math.sin(theta_i) / 1.5))
        self.assertAlmostEqual(theta_t, expected, places=8)

    def test_total_internal_reflection(self):
        theta_i = math.radians(60)
        I = Vec3(math.sin(theta_i), 0, math.cos(theta_i))
        # For a ray inside glass approaching an air boundary, use a normal
        # that opposes the ray.
        N = Vec3(0, 0, -1)
        T = refract(I, N, 1.5, 1.0)
        self.assertIsNone(T)

    def test_critical_angle(self):
        self.assertAlmostEqual(
            critical_angle_deg(1.5, 1.0),
            41.8103148958,
            places=7
        )

    # M2
    def test_fresnel_normal_incidence(self):
        I = Vec3(0, 0, -1)
        N = Vec3(0, 0, 1)
        Rs, Rp, R = fresnel_dielectric(I, N, 1.0, 1.5)
        expected = ((1.0 - 1.5) / (1.0 + 1.5)) ** 2
        self.assertAlmostEqual(Rs, expected, places=12)
        self.assertAlmostEqual(Rp, expected, places=12)
        self.assertAlmostEqual(R, expected, places=12)

    def test_brewster_angle_rp_near_zero(self):
        th = math.radians(brewster_angle_deg(1.0, 1.5))
        I = Vec3(math.sin(th), 0, -math.cos(th))
        N = Vec3(0, 0, 1)
        Rs, Rp, R = fresnel_dielectric(I, N, 1.0, 1.5)
        self.assertLess(Rp, 1e-12)

    # M3
    def test_bk7_dispersion_direction(self):
        n_blue = sellmeier_index(450, BK7_B, BK7_C)
        n_red = sellmeier_index(650, BK7_B, BK7_C)
        self.assertGreater(n_blue, n_red)

    def test_bk7_reasonable_n(self):
        n_d = sellmeier_index(587.6, BK7_B, BK7_C)
        self.assertTrue(1.51 < n_d < 1.52)

    # M4
    def test_demo_lens_has_finite_focus(self):
        lens = ThickLens(
            SphericalSurface(0.0, 50.0, 10.0),
            SphericalSurface(5.0, -50.0, 10.0),
            bk7(),
        )
        z = paraxial_focus(lens, 587.6)
        self.assertTrue(40.0 < z < 60.0)

    def test_blue_focus_differs_from_red(self):
        lens = ThickLens(
            SphericalSurface(0.0, 50.0, 10.0),
            SphericalSurface(5.0, -50.0, 10.0),
            bk7(),
        )
        zb = paraxial_focus(lens, 486.1)
        zr = paraxial_focus(lens, 656.3)
        self.assertNotAlmostEqual(zb, zr, places=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
