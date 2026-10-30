from dataclasses import dataclass
from .vector import Vec3


@dataclass(frozen=True)
class Ray:
    origin: Vec3
    direction: Vec3
    wavelength_nm: float = 550.0

    def __post_init__(self):
        object.__setattr__(self, "direction", self.direction.normalized())

    def at(self, t: float) -> Vec3:
        return self.origin + self.direction * t
