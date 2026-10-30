from .vector import Vec3


def wavelength_to_rgb(wavelength_nm: float) -> Vec3:
    """
    Approximate visible-wavelength-to-display-RGB mapping.
    This is a display helper, not a colorimetric CIE implementation.
    """
    w = wavelength_nm
    if w < 380 or w > 780:
        return Vec3(0, 0, 0)

    if w < 440:
        r, g, b = -(w - 440) / (440 - 380), 0.0, 1.0
    elif w < 490:
        r, g, b = 0.0, (w - 440) / (490 - 440), 1.0
    elif w < 510:
        r, g, b = 0.0, 1.0, -(w - 510) / (510 - 490)
    elif w < 580:
        r, g, b = (w - 510) / (580 - 510), 1.0, 0.0
    elif w < 645:
        r, g, b = 1.0, -(w - 645) / (645 - 580), 0.0
    else:
        r, g, b = 1.0, 0.0, 0.0

    if w < 420:
        factor = 0.3 + 0.7 * (w - 380) / 40
    elif w <= 700:
        factor = 1.0
    else:
        factor = 0.3 + 0.7 * (780 - w) / 80

    return Vec3(r * factor, g * factor, b * factor)
