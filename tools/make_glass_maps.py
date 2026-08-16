#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the displacement maps that give the glass surfaces real refraction.

`backdrop-filter: blur()` is frosting, not glass -- it never bends what is
behind it. To actually refract the page underneath, an SVG <feDisplacementMap>
needs a map whose red and green channels encode a per-pixel offset. These are
those maps.

The encoding is the one feDisplacementMap expects: channel 128 means no offset,
and the shift applied is ((channel / 255) - 0.5) * scale. Here the offset points
along the gradient of a rounded-rectangle signed distance field, so pixels are
pushed outward hard at the rim and not at all through the middle -- which is how
a real bevelled pane of glass behaves.

    python3 tools/make_glass_maps.py

Writes assets/img/glass-bar.png and assets/img/glass-card.png.
"""

import math
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img")


def rounded_rect_sdf(x, y, w, h, r):
    """Signed distance to a rounded rectangle centred on the origin."""
    qx = abs(x) - (w - r)
    qy = abs(y) - (h - r)
    ax, ay = max(qx, 0.0), max(qy, 0.0)
    return math.hypot(ax, ay) + min(max(qx, qy), 0.0) - r


def build(width, height, radius_px, band_px, path):
    """Write one displacement map.

    ``band_px`` is how far in from the edge the refraction reaches. A narrow
    band reads as a thin, hard bevel; a wide one as a thick, soft pane.
    """
    img = Image.new("RGB", (width, height), (128, 128, 128))
    px = img.load()

    hw, hh = width / 2.0, height / 2.0
    r = radius_px

    for py in range(height):
        y = py - hh + 0.5
        for pxi in range(width):
            x = pxi - hw + 0.5

            d = rounded_rect_sdf(x, y, hw, hh, r)
            if d > 0.0 or -d > band_px:
                # Outside the shape, or deep enough inside to be flat glass.
                continue

            # Gradient of the SDF by central difference: the surface normal,
            # projected into the plane.
            eps = 1.0
            gx = (rounded_rect_sdf(x + eps, y, hw, hh, r)
                  - rounded_rect_sdf(x - eps, y, hw, hh, r)) / (2 * eps)
            gy = (rounded_rect_sdf(x, y + eps, hw, hh, r)
                  - rounded_rect_sdf(x, y - eps, hw, hh, r)) / (2 * eps)
            length = math.hypot(gx, gy)
            if length < 1e-6:
                continue
            gx /= length
            gy /= length

            # Falloff from rim to centre. The cubic keeps the very edge intense
            # while dying away quickly, which is what stops the whole panel
            # looking like a warped mirror.
            t = 1.0 - (-d / band_px)
            falloff = t * t * t

            px[pxi, py] = (
                max(0, min(255, int(round(128 + gx * falloff * 127)))),
                max(0, min(255, int(round(128 + gy * falloff * 127)))),
                128,
            )

    img.save(path, "PNG", optimize=True)
    print("%s  %dx%d  %d KB" % (os.path.basename(path), width, height,
                                os.path.getsize(path) // 1024))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    # Wide, shallow surfaces: the sticky header and the call bar.
    build(640, 96, 10, 26, os.path.join(OUT, "glass-bar.png"))
    # Roughly square surfaces: cards, plan panels, callouts.
    build(384, 384, 14, 46, os.path.join(OUT, "glass-card.png"))
