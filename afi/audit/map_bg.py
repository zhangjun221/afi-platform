"""Fetch + stitch OSM tiles into a map background, embedded as base64 in the HTML.

Server-side at report-generation time (so the browser doesn't need to reach OSM,
and the HTML stays self-contained). Uses Web Mercator tile math; for small areas
(Beijing ~7km) the linear lat approximation in the SVG aligns fine.
"""
from __future__ import annotations

import base64
import io
import math
import urllib.request
from typing import Optional

try:
    from PIL import Image
    _HAVE_PIL = True
except Exception:
    _HAVE_PIL = False


def _lng_to_tile_x(lng, zoom):
    return (lng + 180) / 360 * (2 ** zoom)

def _lat_to_tile_y(lat, zoom):
    lat_rad = math.radians(lat)
    return (1 - math.asinh(math.tan(lat_rad)) / math.pi) / 2 * (2 ** zoom)

def _fetch_tile(z, x, y):
    url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    req = urllib.request.Request(url, headers={"User-Agent": "afi/1.0 (research)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGB")


def fetch_osm_background(bounds: dict, out_w: int = 520, out_h: int = 400) -> Optional[str]:
    """Return a base64 data URI PNG of an OSM map covering `bounds`, or None on failure."""
    if not _HAVE_PIL:
        return None
    lo, hi = bounds["lng_lo"], bounds["lng_hi"]
    la_lo, la_hi = bounds["lat_lo"], bounds["lat_hi"]
    span = max(hi - lo, la_hi - la_lo, 1e-4)
    # pick zoom so the span maps to ~ out_w px (256 px per tile, 360 deg full)
    z = max(10, min(16, int(round(math.log2(out_w * 360 / (256 * span))))))
    # tile coords (float) for the bounds corners
    x0, x1 = _lng_to_tile_x(lo, z), _lng_to_tile_x(hi, z)
    y0, y1 = _lat_to_tile_y(la_hi, z), _lat_to_tile_y(la_lo, z)  # y grows southward
    tx0, tx1 = int(math.floor(min(x0, x1))), int(math.ceil(max(x0, x1)))
    ty0, ty1 = int(math.floor(min(y0, y1))), int(math.ceil(max(y0, y1)))
    # fetch + stitch
    try:
        tiles = []
        for ty in range(ty0, ty1 + 1):
            row = []
            for tx in range(tx0, tx1 + 1):
                try:
                    row.append(_fetch_tile(z, tx, ty))
                except Exception:
                    row.append(Image.new("RGB", (256, 256), (230, 230, 230)))
            tiles.append(row)
        tw = (tx1 - tx0 + 1) * 256
        th = (ty1 - ty0 + 1) * 256
        canvas = Image.new("RGB", (tw, th), (255, 255, 255))
        for i, row in enumerate(tiles):
            for j, img in enumerate(row):
                canvas.paste(img, (j * 256, i * 256))
        # crop to the bounds pixel rect within the stitched canvas
        px0 = (min(x0, x1) - tx0) * 256
        px1 = (max(x0, x1) - tx0) * 256
        py0 = (min(y0, y1) - ty0) * 256
        py1 = (max(y0, y1) - ty0) * 256
        crop = canvas.crop((int(px0), int(py0), int(px1), int(py1)))
        # scale to out size (aspect may differ; that's ok, SVG coords are linear in lng/lat)
        crop = crop.resize((out_w, out_h))
        buf = io.BytesIO()
        crop.save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None
