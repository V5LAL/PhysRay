from dataclasses import dataclass
import math
from .vector import Vec3
from .ray import Ray


@dataclass(frozen=True)
class Camera:
    position: Vec3
    width: int
    height: int
    vertical_fov_deg: float = 55.0

    def ray_for_pixel(
        self,
        x: int,
        y: int,
        wavelength_nm: float = 550.0
    ) -> Ray:
        aspect = self.width / self.height
        scale = math.tan(math.radians(self.vertical_fov_deg) / 2)

        u = (x + 0.5) / self.width
        v = (y + 0.5) / self.height

        sx = (2 * u - 1) * aspect * scale
        sy = (1 - 2 * v) * scale

        return Ray(
            self.position,
            Vec3(sx, sy, -1.0),
            wavelength_nm
        )
