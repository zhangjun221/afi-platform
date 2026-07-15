"""Load named places (POIs + AOIs) from the Beijing .pb map, converted to lng/lat.

Gives the mobility map "places" (restaurant / landmark names) at real positions,
so the HTML map isn't just empty dots. Uses pyproj with the map's transverse
Mercator projection to convert local x,y meters → lng,lat.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

try:
    import pyproj
    from pycityproto.city.map.v2 import map_pb2
    _HAVE_DEPS = True
except Exception:
    _HAVE_DEPS = False


def load_places_near(pb_path: str | Path, bounds: dict, max_n: int = 40) -> List[dict]:
    """POIs + AOI centroids within lng/lat bounds, with names.

    bounds = {lng_lo, lng_hi, lat_lo, lat_hi}. Returns list of
    {name, category, lng, lat, kind} (kind='poi' or 'aoi'), capped at max_n.
    Prefers POIs with non-empty names; falls back to AOI names.
    """
    if not _HAVE_DEPS:
        return []
    pb = map_pb2.Map()
    with open(pb_path, "rb") as f:
        pb.ParseFromString(f.read())
    proj_str = pb.header.projection
    try:
        proj = pyproj.Proj(proj_str)
    except Exception:
        return []

    lo, hi = bounds["lng_lo"], bounds["lng_hi"]
    la_lo, la_hi = bounds["lat_lo"], bounds["lat_hi"]

    def in_bounds(lng, lat):
        return lo <= lng <= hi and la_lo <= lat <= la_hi

    places = []
    # POIs (single position, named, categorized)
    for p in pb.pois:
        if not p.name:
            continue
        try:
            lng, lat = proj(p.position.x, p.position.y, inverse=True)
        except Exception:
            continue
        if in_bounds(lng, lat):
            places.append({"name": p.name, "category": p.category,
                           "lng": lng, "lat": lat, "kind": "poi"})
        if len(places) >= max_n:
            return places
    # AOI centroids (named areas) if room
    for a in pb.aois:
        if not a.name:
            continue
        if not a.positions:
            continue
        # centroid of first few positions (cheap)
        xs = [pt.x for pt in a.positions[:8]]
        ys = [pt.y for pt in a.positions[:8]]
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        try:
            lng, lat = proj(cx, cy, inverse=True)
        except Exception:
            continue
        if in_bounds(lng, lat):
            places.append({"name": a.name, "category": f"aoi(type={a.type})",
                           "lng": lng, "lat": lat, "kind": "aoi"})
        if len(places) >= max_n:
            break
    return places


def find_pb_path(run_dir: str | Path) -> Optional[str]:
    """Find the .pb map path from the run's MobilitySpace config (SOCIETY.json)."""
    soc = Path(run_dir) / "SOCIETY.json"
    if not soc.is_file():
        return None
    try:
        d = json.loads(soc.read_text(encoding="utf-8"))
    except Exception:
        return None
    # SOCIETY.json stores env_kwargs as {module_type: {file_path: ...}}
    ek = d.get("env_kwargs", {})
    fp = None
    if isinstance(ek, dict):
        for _mt, kw in ek.items():
            if isinstance(kw, dict) and kw.get("file_path"):
                fp = kw["file_path"]
                break
    # fallback: env_modules list shape
    if not fp:
        for m in d.get("env_modules", []) or []:
            kw = m.get("kwargs", {}) if isinstance(m, dict) else {}
            if kw.get("file_path"):
                fp = kw["file_path"]
                break
    if not fp:
        return None
    p = Path(fp)
    if not p.is_absolute():
        # file_path is relative to the AgentSociety workspace (run_dir's parent)
        p = (Path(run_dir).parent / p).resolve()
    return str(p) if p.is_file() else str(p)


# ── category → icon (emoji) for map markers ─────────────────────────────────

def category_icon(category: str) -> str:
    """Map a POI category string (e.g. 'amenity|restaurant') to an emoji icon."""
    c = (category or "").lower()
    if "restaurant" in c or "fast_food" in c or "food" in c:
        return "🍽"
    if "cafe" in c or "coffee" in c:
        return "☕"
    if "bar" in c or "pub" in c:
        return "🍺"
    if "cinema" in c or "theatre" in c:
        return "🎬"
    if "park" in c or "garden" in c:
        return "🌳"
    if "place_of_worship" in c or "church" in c or "temple" in c:
        return "⛪"
    if "bank" in c:
        return "🏦"
    if "hospital" in c or "clinic" in c:
        return "🏥"
    if "school" in c or "university" in c:
        return "🎓"
    if "shop" in c or "mall" in c or "supermarket" in c or "convenience" in c:
        return "🛒"
    if "hotel" in c or "guest_house" in c:
        return "🏨"
    if "parking" in c or "bicycle_parking" in c:
        return "🅿"
    if "fuel" in c or "gas" in c:
        return "⛽"
    if "bus" in c or "subway" in c or "railway" in c or "station" in c:
        return "🚉"
    if "toilet" in c:
        return "🚻"
    if "atm" in c:
        return "💳"
    return "📍"


# ── AOI id → name lookup (for agent position labels) ─────────────────────────

_aoi_name_cache: dict = {}


def load_aoi_names(pb_path: str | Path, aoi_ids) -> dict:
    """Return {aoi_id: name} for the given AOI ids, parsed from the .pb.
    Cached per pb_path. Only loads names for requested ids (fast)."""
    if not _HAVE_DEPS:
        return {}
    key = str(pb_path)
    cache = _aoi_name_cache.setdefault(key, {})
    needed = [int(i) for i in aoi_ids if int(i) not in cache]
    if not needed:
        return {int(i): cache.get(int(i), "") for i in aoi_ids}
    needed_set = set(needed)
    pb = map_pb2.Map()
    with open(pb_path, "rb") as f:
        pb.ParseFromString(f.read())
    for a in pb.aois:
        if a.id in needed_set:
            cache[a.id] = a.name
            needed_set.discard(a.id)
            if not needed_set:
                break
    return {int(i): cache.get(int(i), "") for i in aoi_ids}


def aoi_centroid_lnglat(pb_path: str | Path, aoi_ids) -> dict:
    """Return {aoi_id: (lng, lat)} centroid for the given AOI ids."""
    if not _HAVE_DEPS:
        return {}
    pb = map_pb2.Map()
    with open(pb_path, "rb") as f:
        pb.ParseFromString(f.read())
    try:
        proj = pyproj.Proj(pb.header.projection)
    except Exception:
        return {}
    needed = set(int(i) for i in aoi_ids)
    out = {}
    for a in pb.aois:
        if a.id in needed:
            if a.positions:
                xs = [pt.x for pt in a.positions[:8]]
                ys = [pt.y for pt in a.positions[:8]]
                cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
                try:
                    lng, lat = proj(cx, cy, inverse=True)
                    out[a.id] = (lng, lat)
                except Exception:
                    pass
            needed.discard(a.id)
            if not needed:
                break
    return out


def load_scenario_places(pb_path: str | Path, run_dir: str | Path,
                          mobility_states: list) -> dict:
    """Scenario-relevant places only (not random POIs):
      - home/work AOIs of each agent (from SOCIETY.json persons config)
      - AOIs agents actually visited (from mobility_states aoi_ids)
    Returns {places: [{name,role,lng,lat,icon,aoi_id}], aoi_names: {id:name}}
    where role in {'home','work','visited'}."""
    import json as _json
    soc = Path(run_dir) / "SOCIETY.json"
    persons = []
    if soc.is_file():
        d = _json.loads(soc.read_text(encoding="utf-8"))
        ek = d.get("env_kwargs", {})
        for _mt, kw in (ek.items() if isinstance(ek, dict) else []):
            if isinstance(kw, dict) and kw.get("persons"):
                persons = kw["persons"]
                break
    # home/work aoi ids
    home_work_ids = set()
    for p in persons:
        for k in ("home_aoi", "work_aoi"):
            if p.get(k) is not None:
                home_work_ids.add(int(p["home_aoi"]) if k == "home_aoi" else int(p["work_aoi"]))
    # visited aoi ids
    visited_ids = set()
    for r in mobility_states:
        if r.get("aoi_id") is not None:
            visited_ids.add(int(r["aoi_id"]))
    all_ids = home_work_ids | visited_ids
    names = load_aoi_names(pb_path, all_ids) if all_ids else {}
    centroids = aoi_centroid_lnglat(pb_path, all_ids) if all_ids else {}
    # home/work with agent ownership
    home_of = {int(p["home_aoi"]): p["id"] for p in persons if p.get("home_aoi") is not None}
    work_of = {int(p["work_aoi"]): p["id"] for p in persons if p.get("work_aoi") is not None}
    places = []
    for aid in sorted(home_work_ids | visited_ids):
        if aid not in centroids:
            continue
        lng, lat = centroids[aid]
        name = names.get(aid, f"AOI {aid}")
        if aid in home_of:
            places.append({"name": name, "role": f"家(agent {home_of[aid]})",
                            "lng": lng, "lat": lat, "icon": "🏠", "aoi_id": aid})
        elif aid in work_of:
            places.append({"name": name, "role": f"工作地(agent {work_of[aid]})",
                            "lng": lng, "lat": lat, "icon": "💼", "aoi_id": aid})
        else:
            places.append({"name": name, "role": "到访过",
                            "lng": lng, "lat": lat, "icon": "📍", "aoi_id": aid})
    return {"places": places, "aoi_names": names}
