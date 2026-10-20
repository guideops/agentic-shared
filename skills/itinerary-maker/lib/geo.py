#!/usr/bin/env python3
"""Geocoding, routing and distance for the itinerary-maker.

Every network answer is cached on disk, because a re-run after adding two stops
should cost those two stops and nothing else. Both services are free, keyless
and public, so the politeness gap between calls is not optional.

Services:
  Nominatim  - place name -> coordinates
  Valhalla   - real routes over the road/foot network (auto, pedestrian, bicycle)

A routing outage degrades the numbers to a calibrated straight-line estimate
rather than killing the run; every answer carries how it was obtained so the
renderer can mark an estimate as an estimate.
"""
from __future__ import annotations

import json
import math
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request

NOMINATIM = "https://nominatim.openstreetmap.org/search"

# Bump when query construction changes, so stale negative results
# recorded by older, buggier query building get retried once.
NEGATIVE_VERSION = 2
VALHALLA = "https://valhalla1.openstreetmap.de/route"
OVERPASS = "https://overpass-api.de/api/interpreter"

UA = "itinerary-maker/1.0 (personal trip planning; contact via operator)"

# Calibrated fallbacks, used only when the router is unreachable.
# Measured on real legs: ~80 m/min walking on the network, and a road detour
# factor because straight-line systematically understates every journey.
WALK_M_PER_MIN = 80.0
DRIVE_KMH_FALLBACK = 55.0
DETOUR = 1.30

_MIN_GAP_S = 1.1          # be a polite citizen of a free public service
_last_call = [0.0]


def _throttle():
    wait = _MIN_GAP_S - (time.time() - _last_call[0])
    if wait > 0:
        time.sleep(wait)
    _last_call[0] = time.time()


def _get(url: str, timeout: int = 25) -> bytes:
    _throttle()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _post(url: str, payload: dict, timeout: int = 30) -> bytes:
    _throttle()
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"User-Agent": UA, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def haversine_km(a, b) -> float:
    """Great-circle km between (lat, lon) pairs."""
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(h))


class Cache:
    """A dict on disk. Written only when something actually changed."""

    def __init__(self, path: pathlib.Path):
        self.path = pathlib.Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.data = json.loads(self.path.read_text())
        except Exception:
            self.data = {}
        self.dirty = False
        self.hits = 0
        self.misses = 0

    def get(self, key):
        v = self.data.get(key)
        if v is not None:
            self.hits += 1
        return v

    def put(self, key, value):
        self.data[key] = value
        self.dirty = True
        self.misses += 1

    def save(self):
        if self.dirty:
            self.path.write_text(json.dumps(self.data, indent=1, sort_keys=True))
            self.dirty = False


class Geo:
    """Geocoder + router, both cached, both degrading rather than failing."""

    def __init__(self, cache_dir: pathlib.Path):
        cache_dir = pathlib.Path(cache_dir)
        self.geocode_cache = Cache(cache_dir / "geocode.json")
        self.route_cache = Cache(cache_dir / "routes.json")
        self.offline = False

    # ---------------------------------------------------------------- geocode
    def geocode(self, query: str, near: str = ""):
        """Place name -> {'lat','lon','display'} or None.

        `near` is appended to disambiguate: 'Skyline Gondola' alone is
        ambiguous worldwide, 'Skyline Gondola, Queenstown, New Zealand' is not.
        """
        query, near = query.strip(), near.strip()
        # Appending a region the query already states produces nonsense like
        # 'Gibbston Valley Winery, Gibbston, New Zealand, Queenstown, New
        # Zealand', which Nominatim rightly fails to resolve.
        if near:
            tail = near.split(",")[-1].strip().lower()
            if tail and tail in query.lower():
                near = ""
        q = ", ".join(x for x in (query, near) if x)
        key = q.lower()
        hit = self.geocode_cache.get(key)
        if hit is not None:
            if hit.get("lat") is not None:
                return hit
            # Re-try misses recorded before the current query-building logic.
            if hit.get("_miss") == NEGATIVE_VERSION:
                return None

        result = None
        if not self.offline:
            try:
                url = NOMINATIM + "?" + urllib.parse.urlencode(
                    {"q": q, "format": "json", "limit": 1, "addressdetails": 1})
                rows = json.loads(_get(url))
                if rows:
                    r = rows[0]
                    result = {"lat": float(r["lat"]), "lon": float(r["lon"]),
                              "display": r.get("display_name", q)}
            except Exception:
                pass

        # Cache the miss too. A place Nominatim cannot find will not be found
        # on the next run either, and re-asking just burns the rate limit.
        self.geocode_cache.put(key, result or {"_miss": NEGATIVE_VERSION})
        return result

    # ------------------------------------------------------------------ route
    def route(self, a, b, mode: str = "auto"):
        """Travel between (lat,lon) points.

        Returns {'mins', 'km', 'how'} where `how` is 'routed' or 'estimated'.
        Never raises: a routing outage degrades the number, it does not end
        the trip.
        """
        if a is None or b is None:
            return None
        key = f"{mode}:{a[0]:.5f},{a[1]:.5f}>{b[0]:.5f},{b[1]:.5f}"
        hit = self.route_cache.get(key)
        if hit is not None:
            return hit

        out = None
        if not self.offline:
            try:
                payload = {
                    "locations": [{"lat": a[0], "lon": a[1]}, {"lat": b[0], "lon": b[1]}],
                    "costing": mode,
                    "directions_options": {"units": "kilometers"},
                }
                d = json.loads(_post(VALHALLA, payload))
                s = d["trip"]["summary"]
                out = {"mins": round(s["time"] / 60.0, 1),
                       "km": round(s["length"], 2), "how": "routed"}
            except Exception:
                pass

        if out is None:
            out = self._estimate(a, b, mode)

        self.route_cache.put(key, out)
        return out

    @staticmethod
    def _estimate(a, b, mode):
        km = haversine_km(a, b) * DETOUR
        if mode == "pedestrian":
            mins = km * 1000.0 / WALK_M_PER_MIN
        elif mode == "bicycle":
            mins = km / 15.0 * 60.0
        else:
            mins = km / DRIVE_KMH_FALLBACK * 60.0
        return {"mins": round(mins, 1), "km": round(km, 2), "how": "estimated"}

    def save(self):
        self.geocode_cache.save()
        self.route_cache.save()

    def stats(self):
        return {
            "geocode_hits": self.geocode_cache.hits,
            "geocode_lookups": self.geocode_cache.misses,
            "route_hits": self.route_cache.hits,
            "route_lookups": self.route_cache.misses,
        }


def overpass(query: str, timeout: int = 60):
    """Run a raw Overpass QL query. Returns [] on any failure.

    Used for coordinates and gap-filling only. Overpass is excellent at
    'where is this' and poor at 'is this worth doing' - its top results for a
    resort town include unnamed viewpoints and derelict huts.
    """
    try:
        _throttle()
        data = urllib.parse.urlencode({"data": query}).encode()
        req = urllib.request.Request(OVERPASS, data=data, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read()).get("elements", [])
    except Exception:
        return []


def pois_near(lat: float, lon: float, radius_m: int, kinds: dict, limit: int = 60):
    """Named POIs near a point. `kinds` maps an OSM key to a regex of values.

    Unnamed elements are dropped on the way out: a stop you cannot name is a
    stop you cannot put on an itinerary.
    """
    clauses = []
    for key, values in kinds.items():
        for typ in ("node", "way"):
            clauses.append(f'{typ}["{key}"~"{values}"]["name"](around:{radius_m},{lat},{lon});')
    q = f"[out:json][timeout:50];({''.join(clauses)});out center {limit};"
    out = []
    for e in overpass(q):
        t = e.get("tags", {})
        name = t.get("name")
        if not name:
            continue
        elat = e.get("lat") or (e.get("center") or {}).get("lat")
        elon = e.get("lon") or (e.get("center") or {}).get("lon")
        if elat is None or elon is None:
            continue
        out.append({
            "name": name,
            "lat": float(elat),
            "lon": float(elon),
            "osm_kind": t.get("tourism") or t.get("leisure") or t.get("amenity")
                        or t.get("natural") or t.get("historic") or "",
            "opening_hours": t.get("opening_hours", ""),
            "website": t.get("website") or t.get("contact:website", ""),
            "phone": t.get("phone") or t.get("contact:phone", ""),
            "cuisine": t.get("cuisine", ""),
        })
    return out
