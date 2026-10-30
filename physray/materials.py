from __future__ import annotations
from dataclasses import dataclass
import math
from .vector import Vec3

# Schott N-BK7 Sellmeier coefficients.
# Wavelength is in micrometres.
BK7_B = (1.03961212, 0.231792344, 1.01046945)
BK7_C = (0.00600069867, 0.0200179144, 103.560653)


def sellmeier_index(wavelength_nm: float, B, C) -> float:
    lam_um = wavelength_nm / 1000.0
    lam2 = lam_um * lam_um
    n2 = 1.0
    for Bi, Ci in zip(B, C):
        n2 += Bi * lam2 / (lam2 - Ci)
    if n2 <= 0:
        raise ValueError("Sellmeier equation produced non-physical n^2.")
    return math.sqrt(n2)


@dataclass(frozen=True)
class Material:
    name: str


@dataclass(frozen=True)
class Diffuse(Material):
    color: Vec3


@dataclass(frozen=True)
class Mirror(Material):
    tint: Vec3 = Vec3(1.0, 1.0, 1.0)


@dataclass(frozen=True)
class DielectricConstant(Material):
    refractive_index: float

    def n(self, wavelength_nm: float) -> float:
        return self.refractive_index


@dataclass(frozen=True)
class DielectricSellmeier(Material):
    B: tuple
    C: tuple

    def n(self, wavelength_nm: float) -> float:
        return sellmeier_index(wavelength_nm, self.B, self.C)


def bk7() -> DielectricSellmeier:
    return DielectricSellmeier("BK7", BK7_B, BK7_C)
